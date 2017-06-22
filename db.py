from eventlet import tpool
import threading
import sqlite3


def execute(query, args):
    tls = threading.local()
    if not hasattr(tls,'sqlite3connection'):
        tls.sqlite3connection = sqlite3.connect('game.db')
    conn = tls.sqlite3connection
    c = conn.cursor()
    ans = c.execute(query, args).fetchall()
    conn.commit()
    return ans

def create_db():
    tpool.execute(execute,'CREATE TABLE IF NOT EXISTS users (id TEXT primary key, nickname TEXT not null, score INTEGER default 0, status TEXT, CHECK (status in("admin", "client")))', [])

def update_score(uid, diff):
    tpool.execute(execute,'UPDATE users SET score=score+? WHERE id=?', [diff, uid])

def top(amount, start):
    return tpool.execute(execute,'SELECT nickname, score FROM users ORDER BY score DESC LIMIT ? OFFSET ?', [amount, start])

def create_user(uid, nick, status):
    if not tpool.execute(execute,'SELECT id FROM users WHERE id=? LIMIT 1', [uid]):
        tpool.execute(execute,'INSERT INTO users (id, nickname, status) VALUES(?, ?, ?)', [uid, nick, status])

def return_inf(uid):
    return tpool.execute(execute,'SELECT id, nickname, score, status FROM users WHERE id=? LIMIT 1', [uid])

def return_status(uid):
    return tpool.execute(execute,'SELECT status FROM users WHERE id=? LIMIT 1', [uid])

def all_db(amount, start):
    return tpool.execute(execute,'SELECT id, nickname, score, status FROM users LIMIT ? OFFSET ?', [amount, start])
