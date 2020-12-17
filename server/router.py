import logging
import os
import platform
import stat
import time
import traceback
from typing import List

import requests
from flask import jsonify, request
from flask.blueprints import Blueprint
from flask_babel import gettext

from base.models import Msg, User
from init import db
from util import server_info, config, v2_jobs, file_util, v2_util

server_bp = Blueprint('server', __name__, url_prefix='/server')


@server_bp.route('/status', methods=['GET'])
def status():
    result = server_info.get_status()
    return jsonify(result)


@server_bp.route('/settings', methods=['GET'])
def settings():
    sets = config.all_settings()
    return jsonify([s.to_json() for s in sets])


@server_bp.route('/setting/update/<int:setting_id>', methods=['POST'])
def update_setting(setting_id):
    key = request.form['key']
    name = request.form['name']
    value = request.form['value']
    value_type = request.form['value_type']
    if key == 'cert_file' or key == 'key_file':
        if value and not file_util.is_file(value):
            return jsonify(Msg(False, gettext(u'File <%(file)s> does not exist.', file=value)))
    config.update_setting(setting_id, key, name, value, value_type)
    if key == 'v2_template_config':
        v2_jobs.__v2_config_changed = True
    return jsonify(Msg(True, gettext('update success, please determine if you need to restart the panel.')))


@server_bp.route('/user/update', methods=['POST'])
def update_user():
    old_username = request.form['old_username']
    old_password = request.form['old_password']
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=old_username, password=old_password).first()
    if not user:
        return jsonify(Msg(False, gettext('old username or old password wrong')))
    user.username = username
    user.password = password
    db.session.commit()
    return jsonify(Msg(True, gettext('update success')))


last_get_version_time = 0
v2ray_versions = []


@server_bp.route('/get_v2ray_versions', methods=['GET'])
def get_v2ray_versions():
    global v2ray_versions, last_get_version_time
    try:
        now = time.time()
        if now - last_get_version_time < 60:
            return jsonify(Msg(True, msg=gettext('Get v2ray version success'), obj=v2ray_versions))
        with requests.get('https://api.github.com/repos/v2fly/v2ray-core/releases') as response:
            release_list: List[dict] = response.json()

        versions = [release.get('tag_name') for release in release_list]
        if len(versions) == 0 or versions[0] is None:
            raise Exception()
        v2ray_versions = versions
        last_get_version_time = now
        return jsonify(Msg(True, msg=gettext('Get v2ray version success'), obj=versions))
    except Exception as e:
        logging.error(f'Get v2ray version failed.')
        logging.error(e)
        return jsonify(Msg(
            False, msg=gettext('Failed to check v2ray version from Github, please try again after a while')
        ))


@server_bp.route('/install_v2ray/<version>', methods=['POST'])
def install_v2ray_by_version(version: str):
    url = f'https://github.com/v2fly/v2ray-core/releases/download/{version}/v2ray-linux-64.zip'
    filename = config.get_dir('v2ray_temp.zip')
    zip_dest_dir = config.get_dir('temp_v2ray')
    try:
        with requests.get(url, stream=True) as response:
            with open(filename, 'wb') as f:
                for data in response.iter_content(8192):
                    f.write(data)
        file_util.mkdirs(zip_dest_dir)
        file_util.unzip_file(filename, zip_dest_dir)

        bin_dir = config.get_dir('bin')

        origin_names = ['v2ray', 'v2ctl', 'geoip.dat', 'geosite.dat']
        filenames = ['v2ray-v2-ui', 'v2ctl', 'geoip.dat', 'geosite.dat']

        for i in range(len(filenames)):
            origin_name = origin_names[i]
            name = filenames[i]

            dest_file_path = os.path.join(bin_dir, name)
            # del old file
            file_util.del_file(dest_file_path)

            # move new file to dest
            file_util.mv_file(os.path.join(zip_dest_dir, origin_name), dest_file_path)

            # +x
            os.chmod(dest_file_path, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)

        v2_util.__v2ray_version = ''
        v2_util.restart()

        return jsonify(Msg(True, gettext('Switch v2ray version success')))
    except Exception as e:
        logging.error(f'Download v2ray {version} failed.')
        logging.error(e)
        traceback.print_exc()
        return jsonify(Msg(False, gettext('Switch v2ray-core version failed.')))
    finally:
        file_util.del_file(filename)
        file_util.del_dir(zip_dest_dir)
