

# Monitoring website - Guillaume HANOTEL

## Installation


	sudo apt install mysql-server mysql-client
	sudo apt-get install python-pip python3-pip
	git clone https://github.com/guillaumehanotel/monitoring-website	
	
**Environnement Virtuel :**

	pip install virtualenv
	sudo /usr/bin/easy_install virtualenv
	virtualenv -p python3 venv
	source ./venv/bin/activate
	
**Dépendances :**
	
	pip3 install mysql-connector
	pip3 install flask
	pip3 install passlib
	pip3 install apscheduler
	pip3 install requests
	pip3 install argon2_cffi

	
	cd ..
	git clone https://github.com/slackapi/python-slackclient.git
	cd python-slackclient
	pip install -r requirements.txt
	
	cd ../monitoring-website
	
## Base de données

Executez le fichier monitoring_website.sql pour créer la base de données.
Puis renseignez le fichier secret_config.py

	#Database config
	DATABASE_HOST = 'localhost'
	DATABASE_USER = '<your_user>'
	DATABASE_PASSWORD = '<your_password>'
	DATABASE_NAME = 'monitoring_website'
	SECRET_KEY = 'some random string w17h n|_|m83r5'

## Usage

Renseignez votre host dans config.py :

	VM_HOST = '10.0.2.15'
	
Puis lancez l'app :

	./app.py
	
### Creditentials :
Admin :
login : **admin@gmail.com**
  mdp : **password**
  
User :
  login : **user@gmail.com**
  mdp : **password**
