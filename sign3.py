from flask import Flask, g, session, request, flash, render_template, redirect
from flask_openid import OpenID
import sqlite3
#import os
#os.random(24)

conn=sqlite3.connect('game.db')
c=conn.cursor()

#c.execute('CREATE TABLE users(id CHAR(100) not null, nickname CHAR(100) not null)')


app = Flask(__name__)
app.config.from_object('config')
#from flask_login import LoginManager
#lm = LoginManager()
oid = OpenID(app, 'tmp')


@app.before_request
def lookup_current_user():
    g.user = None
    if 'user_id' in session:
        g.user = session['user_id']

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['nickname'])
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())


@oid.after_login
def create_or_login(resp): 
    cursor = c.execute('SELECT id FROM users WHERE id=?', [resp.identity_url])
    if cursor.fetchone() is None:
        c.execute("INSERT INTO users VALUES(?, ?)", [resp.identity_url, resp.nickname])
        conn.commit()   
    session['user_id'] = resp.identity_url    
    return redirect('static/profile.html')



