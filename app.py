import eventlet

eventlet.monkey_patch()

from flask_socketio import SocketIO
from flask import Flask, g, session, request, flash, render_template, redirect
from flask_openid import OpenID
import sqlite3
import threading
from config import off

app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(app, async_mode='eventlet')
oid = OpenID(app, 'tmp')

def login_user(url, nick):
    def execute():
        tls = threading.local()
        if not hasattr(tls, 'connection'):
            tls.connection = sqlite3.connect('game.db')
        conn = tls.connection
        c = conn.cursor()
    
        cursor = c.execute('SELECT id FROM users WHERE id=?', [url])
        if cursor.fetchone() is None:
            c.execute("INSERT INTO users VALUES(?, ?)", [url, nick])
            conn.commit()

    eventlet.tpool.execute(execute)


@app.route('/top')
def top():
   users = [('a', 'b'), ('b', 'c'), ('d', 'e')]
   return render_template('top10.html', raiting=users)

@app.before_request
def lookup_current_user():
    g.user = None
    if off:
        g.user = 'superuser'
        return

    if 'user_id' in session:
        g.user = session['user_id']



@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login(): 
    if g.user is not None:
       return render_template('profile.html') 
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
    return render_template('profile.html') 

@app.route('/profile')
def profile():
   return render_template('profile.html')
@app.route('/logout')
def logout():
   session.pop('openid', None)
   g.user=None
   return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())
   

if __name__ == '__main__':
   conn = sqlite3.connect('game.db')
   c = conn.cursor()
   app.run(debug=True)
