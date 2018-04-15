#! /usr/bin/env python3.4
# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, g, session, redirect, url_for
import mysql.connector
from passlib.hash import argon2
from passlib.context import CryptContext
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
import atexit
import requests
import datetime
from slackclient import SlackClient


app = Flask(__name__)

app.config.from_object('config')
app.config.from_object('secret_config')

host = app.config['VM_HOST']

SLACK_TOKEN = app.config['SLACK_TOKEN']
sc = SlackClient(SLACK_TOKEN)


pwd_context = CryptContext(
	schemes=["pbkdf2_sha256"],
	default="pbkdf2_sha256",
	pbkdf2_sha256__default_rounds=30000
)




def get_status(url):
	status_code = 999
	try:
		r = requests.get(url, timeout=3)
		r.raise_for_status()
		status_code = r.status_code
	except requests.exceptions.HTTPError as errh:
		status_code = r.status_code
	except requests.exceptions.ConnectionError as errc:
		pass
	except requests.exceptions.Timeout as errt:
		pass
	except requests.exceptions.RequestException as err:
		pass
	return str(status_code)


def checkEqual(iterator):
	return len(set(iterator)) <= 1


def send_message(status_code, link):
	sc.api_call(
		"chat.postMessage",
		channel="général",
		text="Error " + str(status_code) + " on " + str(link)
	)


def insert_histo(status_code, date, id):
	db = get_db()
	query_data = {'status': status_code, 'date': date, 'website_id': id}
	db.execute('INSERT INTO historique (status, date, website_id) VALUES (%(status)s, %(date)s, %(website_id)s)',
			   query_data)


def is_down(website_id):
	db = get_db()
	query_data = {'website_id': website_id}
	db.execute('SELECT status FROM historique WHERE website_id = %(website_id)s order by date DESC LIMIT 3', query_data)
	last_status = db.fetchall()
	isDown = False
	list_last_status = []
	for status in last_status:
		list_last_status.append(int(status[0]))
	if checkEqual(list_last_status) and 200 not in list_last_status:
		isDown = True

	return isDown


def check_status():
	with app.app_context():
		db = get_db()
		db.execute('SELECT id, link FROM website')
		urls = db.fetchall()
		f = '%Y-%m-%d %H:%M:%S'

		for url in urls:
			id = url[0]
			link = url[1]
			status_code = get_status(link)
			now = datetime.datetime.now()
			date = now.strftime(f)

			insert_histo(status_code, date, id)
			if is_down(id):
				send_message(status_code, link)

		commit()


scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
	func=check_status,
	trigger=IntervalTrigger(seconds=120),
	id='check_status',
	name='Insert website status',
	replace_existing=True)
atexit.register(lambda: scheduler.shutdown())

'''
=== ROUTES === 
'''


@app.route('/')
def homepage():
	query = "select w.id, link, status from historique h, website w where h.website_id = w.id group by link having max(date)"
	db = get_db()
	db.execute(query)
	websites = db.fetchall()
	return render_template('index.html', websites=websites)


@app.route('/show/<int:id>/')
def show(id):
	db = get_db()
	query = 'select link, status, date from website, historique where website.id = historique.website_id and website.id= %(website.id)s ORDER BY date DESC'
	db.execute(query, {'website.id': id})
	historics = db.fetchall()
	return render_template('show.html', historics=historics)


@app.route('/login/', methods=['GET', 'POST'])
def login():
	email = str(request.form.get('login'))
	password = str(request.form.get('password'))

	db = get_db()
	db.execute('SELECT email, password, is_admin FROM user WHERE email = %(email)s', {'email': email})
	users = db.fetchall()

	valid_user = False
	for user in users:
		if argon2.verify(password, user[1]):
		# if password == user[1]:
			valid_user = user

	if valid_user:
		session['user'] = valid_user
		return redirect(url_for('admin'))

	return render_template('login.html')


@app.route('/logout/')
def logout():
	session.clear()
	return redirect(url_for('login'))


@app.route('/admin/')
def admin():
	if not session.get('user') or not session.get('user')[2]:
		return redirect(url_for('login'))

	db = get_db()
	db.execute('SELECT id, link FROM website')
	websites = db.fetchall()

	return render_template('admin.html', user=session['user'], websites=websites)


@app.route('/admin/add/website', methods=['GET', 'POST'])
def add_website():
	if request.method == 'POST':
		db = get_db()
		link = str(request.form.get('link'))
		query_data = {'link': link}
		db.execute('INSERT INTO website (link) VALUES (%(link)s)', query_data)
		commit()
		return redirect(url_for('admin'))

	else:
		return render_template('add_website.html')


@app.route('/admin/edit/website/<int:id>', methods=['GET', 'POST'])
def edit_website(id):
	db = get_db()
	if request.method == 'POST':
		link = str(request.form.get('link'))
		query_data = {'link': link, 'id': id}
		db.execute('UPDATE website SET link = %(link)s WHERE id = %(id)s', query_data)
		commit()
		return redirect(url_for('admin'))

	else:
		query = 'select id, link from website where website.id = %(website.id)s'
		db.execute(query, {'website.id': id})
		website = db.fetchone()
		return render_template('edit_website.html', website=website)


@app.route('/admin/confirm_delete/website/<int:id>', methods=['GET', 'POST'])
def delete_website(id):
	db = get_db()
	if request.method == 'POST':

		db.execute('DELETE FROM website WHERE id = %(id)s', {'id': id})
		commit()
		return redirect(url_for('admin'))

	else:

		query = 'select id, link from website where website.id = %(website.id)s'
		db.execute(query, {'website.id': id})
		website = db.fetchone()
		print(website)
		return render_template('confirm_delete.html', website=website)


def connect_db():
	g.mysql_connection = mysql.connector.connect(
		host=app.config['DATABASE_HOST'],
		user=app.config['DATABASE_USER'],
		password=app.config['DATABASE_PASSWORD'],
		database=app.config['DATABASE_NAME']
	)

	g.mysql_cursor = g.mysql_connection.cursor()
	return g.mysql_cursor


def commit():
	g.mysql_connection.commit()


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
	app.run(debug=True, host=host, use_reloader=False)
