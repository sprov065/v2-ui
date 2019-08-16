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


def all_settings():
    return Setting.query.filter(Setting.name != '').all()


def get_port():
    return __get('port', 65432)


def get_address():
    return __get('address', '0.0.0.0')


def get_cert_file():
    return __get('cert_file', '')


def get_key_file():
    return __get('key_file', '')


def get_login_title():
    return __get('login_title', 'Login')


def get_v2_config_path():
    return __get('v2_config_path', '/etc/v2ray/config.json')


def get_v2_restart_cmd():
    return __get('v2_restart_cmd', 'systemctl restart v2ray')


def get_v2_stop_cmd():
    return __get('v2_stop_cmd', 'systemctl stop v2ray')


def get_v2_start_cmd():
    return __get('v2_start_cmd', 'systemctl start v2ray')


def get_v2_config_check_interval():
    return __get('v2_config_check_interval', 60)


def get_v2_template_config():
    return __get('v2_template_config')


def get_traffic_job_interval():
    return __get('traffic_job_interval', 60)


def get_base_path():
    return __get('base_path', '')


def get_secret_key():
    return __get('secret_key', os.urandom(24))


def get_current_version():
    return '4.3.0'


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
    add_if_not_exist(Setting(
        'address', 'Panel Web Listening Address', '0.0.0.0', 'text',
        'Be careful modifying it!!! If you use software such as nginx, you can set this to 127.0.0.1 so that the outside world cannot access the panel directly. Don't change it if you don't understand', True), update)
    add_if_not_exist(Setting(
        'port', 'Panel web port', '65432', 'int',
        '', True), update)
    add_if_not_exist(Setting(
        'base_path', 'Panel page root path', '', 'text',
        'Be careful modifying it!!! You can fill in the root path of your personality page, such as /v2-ui, which is empty by default. If the fill-in must start with / and cannot end with /, the error will result in inaccessible panels', True), update)
    add_if_not_exist(Setting(
        'cert_file', 'Panel ssl cert file path', '', 'text',
        'Be careful modifying it!!! An absolute path is required, and a modification error will prevent the panel from starting', True), update)
    add_if_not_exist(Setting(
        'key_file', 'Panel ssl key file path', '', 'text',
        'Be careful modifying it!!! An absolute path is required, and a modification error will prevent the panel from starting', True), update)
    add_if_not_exist(Setting(
        'login_title', 'Login page title', 'sign in', 'text',
        '', False), update)
    add_if_not_exist(Setting(
        'v2_config_path', 'v2ray config.json path', '/etc/v2ray/config.json', 'text',
        'Be careful modifying it!!! The resulting v2ray configuration is written to the file of this configuration and generally does not need to be modified', False), update)
    add_if_not_exist(Setting(
        'v2_template_config', 'v2ray config template', __read_v2_template_config(), 'textarea',
        'Be careful modifying it!!! Make sure you are very familiar with the configuration of v2ray, please do not delete the configuration about api', False), update)
    add_if_not_exist(Setting(
        'v2_config_check_interval', 'Change Effective Time (seconds)', '60', 'int',
        'Too small number can lead to increased CPU usage, fill 0 or negative at your own risk', True), update)
    add_if_not_exist(Setting(
        'v2_restart_cmd', 'Command to restart v2ray', 'systemctl restart v2ray', 'text',
        'When v2ray needs to be restarted, the panel will automatically run this command to restart v2ray, generally without modification', False), update)
    add_if_not_exist(Setting(
        'traffic_job_interval', 'Statistical traffic interval time (seconds)', '60', 'int',
        'Too small number can lead to increased CPU usage, fill 0 or negative at your own risk', True), update)
    add_if_not_exist(Setting('secret_key', '', os.urandom(24), 'text', '', True), False)
    db.session.commit()


init_db()
