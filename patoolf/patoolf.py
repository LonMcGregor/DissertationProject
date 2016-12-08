from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from flask import Flask, request, session, url_for, redirect, render_template, g, flash


app = Flask(__name__)
app.secret_key = 'Ll9rPXJ7_qhH-YvYNES11verTbHw3JyQxBcis0ZFwjL1LI41'
app.debug = True


def get_db():
    return sqlite3.connect('C:\GitHub\DissertationProject\patoolf\patoolf.db')


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def index():
    global session
    if 'user_id' not in session:
        return """you need to <a href='login'>log in</a>"""
    return render_template('index.html', user=session['user_id'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    global session
    if 'user_id' in session:
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            username = ?''', [request.form['username']], one=True)
        passwd = request.form['password'].encode('utf-8')
        if user is None or not user[2] == md5(passwd).hexdigest():
            error = 'Invalid username / password'
        else:
            flash('You were logged in')
            session['user_id'] = user[0]
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    global session
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
