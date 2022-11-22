To setup a test system on a `t2.medium`, one can manually follow the instructions below to prepare
the OS and run the app in debug mode.

```bash
sudo setfacl -R -m u:ec2-user:rwx /var/app
sudo setfacl -R -m u:webapp:rwx /var/app
sudo yum install git
sudo pip3 install git+https://github.com/agronholm/apscheduler.git
sudo /var/app/venv/staging-LQM1lest/bin/pip3 install git+https://github.com/agronholm/apscheduler.git
source /var/app/venv/staging-LQM1lest/bin/activate
cd /var/app/current/
sudo /var/app/venv/staging-LQM1lest/bin/pip3 install -r requirements.txt

mkdir /var/app/current/pkg; cd /var/app/current/pkg
git clone https://github.com/shayanfazeli/fame.git
cd fame
sudo /var/app/venv/staging-LQM1lest/bin/pip3 install -e .
cd /var/app/current/

# set up nltk: 
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
sudo /var/app/venv/staging-LQM1lest/bin/pip3 install --upgrade apscheduler
sudo systemctl stop web.service
gunicorn --bind 127.0.0.1:8000 --workers=1 --threads=15 application
```