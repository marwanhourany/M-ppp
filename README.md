Usage
-----
1) Edit settings in app/config/env.py

2) Run the following commands:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

sudo -iu postgres psql

>>> CREATE DATABASE ppp_test;
>>> quit

flask db upgrade
export FLASK_ENV=development
flask run
```
