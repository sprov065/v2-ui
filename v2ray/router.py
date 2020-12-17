import json

from flask import Blueprint, render_template, jsonify, request
from flask_babel import gettext
from sqlalchemy import and_

from base.models import Msg
from base.models import User
from init import db
from util import config, server_info, v2_util
from util.v2_jobs import v2_config_change
from v2ray.models import Inbound

v2ray_bp = Blueprint('v2ray', __name__, url_prefix='/v2ray')

__check_interval = config.get_v2_config_check_interval()


@v2ray_bp.route('/', methods=['GET'])
def index():
    from init import common_context
    status = json.dumps(server_info.get_status(), ensure_ascii=False)
    return render_template('v2ray/index.html', **common_context, status=status)


@v2ray_bp.route('/accounts/', methods=['GET'])
def accounts():
    from init import common_context
    inbs = Inbound.query.all()
    inbs = '[' + ','.join([json.dumps(inb.to_json(), ensure_ascii=False) for inb in inbs]) + ']'
    user = User.query.first()
    has_changed = user.username != 'admin' or user.password != 'admin'
    return render_template('v2ray/accounts.html', **common_context,
                           inbounds=inbs, has_changed=has_changed)


@v2ray_bp.route('/clients/', methods=['GET'])
def clients():
    from init import common_context
    return render_template('v2ray/clients.html', **common_context)


@v2ray_bp.route('/setting/', methods=['GET'])
def setting():
    from init import common_context
    settings = config.all_settings()
    settings = '[' + ','.join([json.dumps(s.to_json(), ensure_ascii=False) for s in settings]) + ']'
    return render_template('v2ray/setting.html', **common_context, settings=settings,
                           v2ray_version=v2_util.get_v2ray_version())


@v2ray_bp.route('/tutorial/', methods=['GET'])
def tutorial():
    from init import common_context
    return render_template('v2ray/tutorial.html', **common_context)


@v2ray_bp.route('/donate/', methods=['GET'])
def donate():
    from init import common_context
    return render_template('v2ray/donate.html', **common_context)


@v2ray_bp.route('/inbounds', methods=['GET'])
def inbounds():
    return jsonify([inb.to_json() for inb in Inbound.query.all()])


@v2ray_bp.route('inbound/add', methods=['POST'])
@v2_config_change
def add_inbound():
    port = int(request.form['port'])
    if Inbound.query.filter_by(port=port).count() > 0:
        return jsonify(Msg(False, gettext('port exists')))
    listen = request.form['listen']
    protocol = request.form['protocol']
    settings = request.form['settings']
    stream_settings = request.form['stream_settings']
    sniffing = request.form['sniffing']
    remark = request.form['remark']
    inbound = Inbound(port, listen, protocol, settings, stream_settings, sniffing, remark)
    db.session.add(inbound)
    db.session.commit()
    return jsonify(
        Msg(True,
            gettext(u'Successfully added, will take effect within %(seconds)d seconds', seconds=__check_interval)
            )
    )


@v2ray_bp.route('inbound/update/<int:in_id>', methods=['POST'])
@v2_config_change
def update_inbound(in_id):
    update = {}
    port = request.form.get('port')
    add_if_not_none(update, 'port', port)
    if port:
        if Inbound.query.filter(and_(Inbound.id != in_id, Inbound.port == port)).count() > 0:
            return jsonify(Msg(False, gettext('port exists')))
        add_if_not_none(update, 'tag', 'inbound-' + port)
    add_if_not_none(update, 'listen', request.form.get('listen'))
    add_if_not_none(update, 'protocol', request.form.get('protocol'))
    add_if_not_none(update, 'settings', request.form.get('settings'))
    add_if_not_none(update, 'stream_settings', request.form.get('stream_settings'))
    add_if_not_none(update, 'sniffing', request.form.get('sniffing'))
    add_if_not_none(update, 'remark', request.form.get('remark'))
    add_if_not_none(update, 'enable', request.form.get('enable') == 'true')
    Inbound.query.filter_by(id=in_id).update(update)
    db.session.commit()
    return jsonify(
        Msg(True,
            gettext(u'Successfully updated, will take effect within %(seconds)d seconds', seconds=__check_interval)
            )
    )


@v2ray_bp.route('inbound/del/<int:in_id>', methods=['POST'])
@v2_config_change
def del_inbound(in_id):
    Inbound.query.filter_by(id=in_id).delete()
    db.session.commit()
    return jsonify(
        Msg(True,
            gettext(u'Successfully deleted, will take effect within %(seconds)d seconds', seconds=__check_interval)
            )
    )


@v2ray_bp.route('reset_traffic/<int:in_id>', methods=['POST'])
def reset_traffic(in_id):
    Inbound.query.filter_by(id=in_id).update({'up': 0, 'down': 0})
    db.session.commit()
    return jsonify(Msg(True, gettext('Reset traffic successfully')))


@v2ray_bp.route('reset_all_traffic', methods=['POST'])
def reset_all_traffic():
    Inbound.query.update({'up': 0, 'down': 0})
    db.session.commit()
    return jsonify(Msg(True, gettext('Reset add traffic successfully')))


def add_if_not_none(d, key, value):
    if value is not None:
        d[key] = value
