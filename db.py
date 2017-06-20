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
    tpool.execute(execute,'CREATE TABLE IF NOT EXISTS users (id TEXT primary key, nickname TEXT not null, score INTEGER)', [])

def update_score(uid, diff):
    tpool.execute(execute,'UPDATE users SET score=score+? WHERE id=?', [diff, uid])

def top10():
    return tpool.execute(execute,'SELECT TOP 10 nickname, result FROM results ORDER BY result DESC', [])

def create_user(uid, nick):
    if not tpool.execute(execute,'SELECT TOP 1 id FROM users WHERE id=?', [uid]):
        tpool.execute(execute,'INSERT INTO users VALUES(?, ?)', [uid, nick])
