from flask import Flask, session, redirect, url_for, escape, request, render_template
from hashlib import md5
import MySQLdb
from config import *


app = Flask(__name__)

if __name__ == '__main__':
    db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, port=DB_PORT, db=DB_NAME)
    cur = db.cursor()
    # app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


class ServerError(Exception):
    pass


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('login'))

    username_session = escape(session['username']).capitalize()
    return render_template('index.html', session_user_name=username_session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    error = None
    try:
        if request.method == 'POST':
            username_form = request.form['username']
            cur.execute("SELECT COUNT(1) FROM users WHERE name = {};"
                        .format(username_form))

            if not cur.fetchone()[0]:
                raise ServerError('Invalid username')

            password_form = request.form['password']
            cur.execute("SELECT pass FROM users WHERE name = {};"
                        .format(username_form))

            for row in cur.fetchall():
                if md5(password_form).hexdigest() == row[0]:
                    session['username'] = request.form['username']
                    return redirect(url_for('index'))

            raise ServerError('Invalid password')
    except ServerError as e:
        error = str(e)

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
    # app.run(debug=True)
