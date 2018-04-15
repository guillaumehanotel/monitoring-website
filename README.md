
# Monitoring website - Guillaume HANOTEL

## Installation


	sudo apt install mysql-server mysql-client
	sudo apt-get install python-pip python3-pip
	
	pip install virtualenv
	sudo /usr/bin/easy_install virtualenv
	virtualenv -p python3 venv
	source ./venv/bin/activate
	
	pip3 install mysql-connector
	pip3 install flask
	pip3 install passlib
	pip3 install apscheduler
	pip3 install requests
	
	cd ..
	git clone https://github.com/slackapi/python-slackclient.git
	cd python-slackclient
	pip install -r requirements.txt
	
	cd ../monitoring-website
	
## Usage

	./app.py
	
Creditentials :
Admin :
  login : **admin@gmail.com**
  mdp : **password**
User :
  login : **user@gmail.com**
  mdp : **password**
