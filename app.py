#! /usr/bin/python3.4
# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, g, session, redirect, url_for
import mysql.connector
from passlib.hash import argon2
from passlib.context import CryptContext

app = Flask(__name__)

app.config.from_object('config')
app.config.from_object('secret_config')

host = app.config['VM_HOST']

pwd_context = CryptContext(
	schemes=["pbkdf2_sha256"],
	default="pbkdf2_sha256",
	pbkdf2_sha256__default_rounds=30000
)

'''
=== ROUTES === 
'''




@app.route('/')
def homepage():
	query = "select w.id, link, status from historique h, website w where h.website_id = w.id group by link, status having max(date)"
	db = get_db()
	db.execute(query)
	websites = db.fetchall()
	return render_template('index.html', websites=websites)


@app.route('/login/', methods=['GET', 'POST'])
def login():
	return render_template('login.html')


@app.route('/logout/')
def logout():
	session.clear()
	return redirect(url_for('login'))


@app.route('/admin/')
def admin():
	if not session.get('user') or not session.get('user')[2]:
		return redirect(url_for('login'))

	return render_template('admin.html', user=session['user'])


@app.route('/show/<id>/')
def show(id):
	db = get_db()
	query = 'select link, status, date from website, historique where website.id = historique.website_id and website.id= %(website.id)s'
	db.execute(query, {'website.id': id})
	historics = db.fetchall()
	return render_template('show.html', historics=historics)






def connect_db():
	g.mysql_connection = mysql.connector.connect(
		host=app.config['DATABASE_HOST'],
		user=app.config['DATABASE_USER'],
		password=app.config['DATABASE_PASSWORD'],
		database=app.config['DATABASE_NAME']
	)

	g.mysql_cursor = g.mysql_connection.cursor()
	return g.mysql_cursor


def get_db():
	if not hasattr(g, 'db'):
		g.db = connect_db()
	return g.db


@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'db'):
		g.db.close()


def encrypt_password(password):
	return pwd_context.encrypt(password)


def check_encrypted_password(password, hashed):
	return pwd_context.verify(password, hashed)


if __name__ == '__main__':
	app.run(debug=True, host=host)
