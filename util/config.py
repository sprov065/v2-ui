import os

from base.models import Setting
from init import db, BASE_DIR


def __read_v2_template_config():
    with open(os.path.join(BASE_DIR, 'template_config.json'), encoding='utf-8') as f:
        return f.read()


def get_setting_value(setting):
    if setting.value_type.startswith('text'):
        return setting.value
    elif setting.value_type == 'int':
        return int(setting.value)
    elif setting.value_type == 'bool':
        return setting.value.lower() == 'true'


def __get(key, default=None):
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        return get_setting_value(setting)
    else:
        return default


def contains_id(setting_id):
    return Setting.query.filter_by(id=setting_id).count() > 0


def update_setting(setting_id, key, name, value, value_type='text'):
    if setting_id and contains_id(setting_id):
        Setting.query.filter_by(id=setting_id).update({'name': name, 'value': value, 'value_type': value_type})
    else:
        setting = Setting(key, name, value, value_type)
        db.session.add(setting)
    db.session.commit()


def update_setting_by_key(key, value):
    Setting.query.filter_by(key=key).update({'value': value})
    db.session.commit()


def all_settings():
    return Setting.query.filter(Setting.name != '', Setting.name != 'is_traffic_reset').all()


def get_port():
    return __get('port', 65432)


def get_address():
    return __get('address', '0.0.0.0')


def get_cert_file():
    return __get('cert_file', '')


def get_key_file():
    return __get('key_file', '')


def get_login_title():
    return __get('login_title', 'Sign in')


# def get_v2_config_path():
#     return __get('v2_config_path', '/etc/v2ray/config.json')


def get_v2_restart_cmd():
    return __get('v2_restart_cmd', 'systemctl restart v2ray')


def get_v2_stop_cmd():
    return __get('v2_stop_cmd', 'systemctl stop v2ray')


def get_v2_start_cmd():
    return __get('v2_start_cmd', 'systemctl start v2ray')


def get_v2_config_check_interval():
    return __get('v2_config_check_interval', 10)


def get_v2_template_config():
    return __get('v2_template_config')


def get_traffic_job_interval():
    return __get('traffic_job_interval', 30)


def get_reset_traffic_day():
    return __get('reset_traffic_day', 0)


def is_traffic_reset():
    return __get('is_traffic_reset', 0) != 0


def get_base_path():
    return __get('base_path', '')


# def get_v2ctl_cmd_path():
#     return __get('v2ctl_cmd_path', '/usr/bin/v2ray/v2ctl')


def get_dir(*paths):
    if not paths:
        return BASE_DIR
    return os.path.join(BASE_DIR, *paths)


def get_secret_key():
    return __get('secret_key', os.urandom(24))


def get_current_version():
    return '5.4.5'


def add_if_not_exist(setting, update=False):
    if Setting.query.filter_by(key=setting.key).count() > 0:
        if update:
            Setting.query.filter_by(key=setting.key).update({
                'name': setting.name,
                'value': setting.value,
                'value_type': setting.value_type,
            })
        return
    db.session.add(setting)


def reset_config():
    init_db(True)


def init_db(update=False):
    add_if_not_exist(Setting('address', 'address', '', 'text', '', True), update)
    add_if_not_exist(Setting('port', 'port', '65432', 'int', '', True), update)
    add_if_not_exist(Setting('base_path', 'base_path', '', 'text', '', True), update)
    add_if_not_exist(Setting('cert_file', 'cert_file', '', 'text', '', True), update)
    add_if_not_exist(Setting('key_file', 'key_file', '', 'text', '', True), update)
    add_if_not_exist(Setting('login_title', 'login_title', 'Sign in', 'text', '', False), update)
    add_if_not_exist(Setting('v2_config_path', 'v2_config_path', '/etc/v2ray/config.json', 'text', '', False), update)
    add_if_not_exist(Setting('v2_template_config', 'v2_template_config', __read_v2_template_config(), 'textarea', '', False), update)
    add_if_not_exist(Setting('v2_config_check_interval', 'v2_config_check_interval', '10', 'int', '', True), update)
    add_if_not_exist(Setting('v2_restart_cmd', 'v2_restart_cmd', 'systemctl restart v2ray', 'text', '', False), update)
    add_if_not_exist(Setting('traffic_job_interval', 'traffic_job_interval', '30', 'int', '', True), update)
    add_if_not_exist(Setting('reset_traffic_day', 'reset_traffic_day', '0', 'int', '', True), update)
    add_if_not_exist(Setting('is_traffic_reset', 'is_traffic_reset', '0', 'int', '', False), update)
    add_if_not_exist(Setting('v2ctl_cmd_path', 'v2ctl_cmd_path', '/usr/local/bin/v2ctl', 'text', '', True), update)
    add_if_not_exist(Setting('secret_key', '', os.urandom(24), 'text', '', True), False)
    db.session.commit()


init_db()
