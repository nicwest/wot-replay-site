from flask import render_template, flash, redirect, session, g, request, url_for
from app import app, db, oid
from models import *
from forms import *
from lib.wotapi import WotAPI
from lib.wotreplay import WotReplay
from werkzeug.utils import secure_filename

import os
import datetime
import re


@app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()

@oid.after_login
def create_or_login(resp):
    session['openid'] = resp.identity_url
    user = User.query.filter_by(openid=resp.identity_url).first()

    #check url is valid
    valid_url = re.compile('https://(eu|ru|na|asia|kr).wargaming.net/id/([0-9]*?)-(.*?)/')
    check_user = re.match(valid_url, session['openid'])

    if not check_user:
        session.pop('verified', None)
        session.pop('openid', None)
        flash('invalid OpenID url, please use a Wargaming OpenID')
        return url_for('login')

    server = check_user.group(1)
    wg_id = check_user.group(2)
    api = WotAPI(server, app.config.get('WOT_API_KEYS'))
    apiquery = api.get_player_data(wg_id, ['nickname', 'clan.clan_id'])
    nickname = apiquery['nickname']
    clan = apiquery['clan']
    if clan and 'clan_id' in clan:
        clan = clan['clan_id']

    if user is not None:
        g.user = user
        g.user.set_meta('clan_id', clan)
        return redirect(url_for('index'))
    else:
        newuser = User(username=nickname, openid=session['openid'], server=server)
        db.session.add(newuser)
        db.session.commit()
        newuser.set_meta('clan_id', clan)
        return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())

    form = LoginForm()
    if form.validate_on_submit():
        return oid.try_login(form.openid.data)
    return render_template('login.html',
                           form=form,
                           next=oid.get_next_url(),
                           error=oid.fetch_error())


@app.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You were signed out')
    return redirect(oid.get_next_url())


def format_vehicle(self, typeCompDescr):
    countryID = typeCompDescr >> 4 & 15
    tankID = typeCompDescr >> 8 & 65535
    typeID = typeCompDescr & 15

    return countryID, tankID, typeID