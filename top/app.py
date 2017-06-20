from flask_socketio import SocketIO
from flask import Flask, g, session, request, flash, render_template, redirect
from flask_openid import OpenID
from config import off
from functions.py import create_table, execute, fetchmany, add_user, add_result, create_top

app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(app, async_mode='eventlet')
oid = OpenID(app, 'tmp')

@app.route('/top')
def top():
   return render_template('top10.html', create_top)

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
    add_user() 
    session['user_id'] = resp.identity_url    
    return redirect('static/profile.html')



if __name__ == '__main__':
   app.run(debug=True)
   create_table()


