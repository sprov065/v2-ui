import logging
import os
import sys

from flask import Flask, request, redirect, url_for, jsonify
from flask_babel import Babel, gettext
from flask_sqlalchemy import SQLAlchemy

from util import session_util, file_util
from util.schedule_util import start_schedule

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
babel = Babel(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 6307200
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////etc/v2-ui/v2-ui.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
need_login_bps = []
common_context = {}


@babel.localeselector
def get_locale():
    match = request.accept_languages.best_match(['zh-TW', 'zh-HK', 'zh-CN', 'zh', 'en'], 'en')
    if 'TW' in match or 'HK' in match:
        return 'zh_Hant'
    if 'zh' in match:
        return 'zh_Hans'
    return 'en'


def init_db():
    from v2ray.models import Inbound
    from base.models import User, Setting
    User.__name__.lower()
    Inbound.__name__.lower()
    Setting.__name__.lower()
    file_util.mkdirs('/etc/v2-ui/')
    db.create_all()


def init_app():
    from util import config
    app.secret_key = config.get_secret_key()


def init_common_context():
    from util import config
    global common_context
    common_context = {
        'cur_ver': config.get_current_version(),
        'base_path': '' if app.debug else config.get_base_path(),
    }


def init_bps():
    from util import config
    from base.router import base_bp
    from server.router import server_bp
    from v2ray.router import v2ray_bp
    bps = [
        base_bp,
        v2ray_bp,
        server_bp,
    ]
    if not app.debug:
        base_path = config.get_base_path()
        for bp in bps:
            bp.url_prefix = base_path + (bp.url_prefix if bp.url_prefix else '')
    global need_login_bps
    need_login_bps += [v2ray_bp, server_bp]
    [app.register_blueprint(bp) for bp in bps]


def init_v2_jobs():
    from util import v2_jobs, v2_util
    v2_jobs.init()
    v2_util.init_v2ray()


def is_ajax():
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


@app.before_request
def before():
    from base.models import Msg
    if not session_util.is_login():
        for bp in need_login_bps:
            if request.path.startswith(bp.url_prefix):
                if is_ajax():
                    return jsonify(Msg(False, gettext('You has been logout, please refresh this page and login again')))
                else:
                    return redirect(url_for('base.index'))


@app.errorhandler(500)
def error_handle(e):
    from base.models import Msg
    logging.warning(e)
    response = jsonify(Msg(False, str(e)))
    response.status_code = 200
    return response


def logging_init():
    logging.basicConfig(stream=sys.stdout,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
                        level=logging.INFO)


init_db()
init_app()
init_common_context()
init_bps()
init_v2_jobs()
start_schedule()
logging_init()
