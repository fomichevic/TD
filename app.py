import eventlet

eventlet.monkey_patch()

from flask_socketio import SocketIO
from flask import Flask, g, session, request, flash, render_template, redirect
from flask_openid import OpenID
from config import off
from db import create_db, create_user, update_score, top, return_inf, all_db, return_status



app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(app, async_mode='eventlet')
oid = OpenID(app, 'tmp')


def login_required(func):
    def before_request(*args, **kwargs):
        if g.user is None:
            return redirect('login')
        return func(*args, **kwargs)
    before_request.__name__ = func.__name__
    return before_request


@app.route('/top')
@login_required
def top():
    amount=request.args.get('amount')
    start=request.args.get('start')
    return render_template('top10.html', rating=enumerate(top(amount, start), 1))



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
        return redirect('profile') 
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['nickname'])
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())

@oid.after_login
def create_or_login(resp): 
    create_user(resp.identity_url, resp.nickname, 'client')
    session['user_id'] = resp.identity_url
    inf=return_inf(session['user_id'])    
    return render_template('profile.html', nickname=inf[0][1], score=inf[0][2]) 


@app.route('/profile')
@login_required
def profile():
    if g.user is None:
       return redirect('login') 
    inf=return_inf(session['user_id']) 
    return render_template('profile.html', nickname=inf[0][1], score=inf[1][2])

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    g.user = None
    return redirect('login')
   
@app.route('/database')
@login_required
def database():
   amount=request.args.get('amount')
   start=request.args.get('start')
   return render_template('database.html', rating=all_db(amount, start))
   

if __name__ == '__main__':
    create_db()
    create_user('id', 'nick', 'admin')
    app.run(debug=True)


