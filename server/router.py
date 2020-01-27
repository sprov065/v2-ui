from flask import jsonify, request
from flask.blueprints import Blueprint
from flask_babel import gettext

from base.models import Msg, User
from init import db
from util import server_info, config, v2_jobs, file_util

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
