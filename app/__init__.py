from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_basicauth import BasicAuth
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .config.glob import *
from .config.env import *

app = Flask(__name__, static_folder="static")

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ECHO'] = SQLALCHEMY_ECHO
app.config['TOKEN_LENGTH'] = TOKEN_LENGTH

app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = MAIL_USE_SSL
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD

app.config['BASIC_AUTH_USERNAME'] = BASIC_AUTH_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = BASIC_AUTH_PASSWORD
app.config['BASIC_AUTH_FORCE'] = BASIC_AUTH_FORCE

app.config['REGISTER_KEY'] = REGISTER_KEY
app.config['ADMIN_KEY'] = ADMIN_KEY

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['ROOT_URL'] = ROOT_URL

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

mail = Mail(app)
migrate = Migrate(app, db)

from .models import User, Country, Basket, PurchasingPowerParity, ExchangeRate

basic_auth = BasicAuth(app)
from .views import UserView

admin = Admin(app, url=f"/admin/{app.config['ADMIN_KEY']}")
admin.add_view(UserView(User, db.session))

from app import routes
