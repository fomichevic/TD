import eventlet
from flask_socketio import SocketIO
from flask import Flask, g, session, request, flash, render_template, redirect
from flask_openid import OpenID
import sqlite3
from config import off

app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(app, async_mode='eventlet')
oid = OpenID(app, 'tmp')

conn = sqlite3.connect('game.db')
c = conn.cursor()


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


if __name__ == '__main__':
   app.run(debug=True)
