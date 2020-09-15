from datetime import datetime

from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), unique=False, nullable=False)
    last_name = db.Column(db.String(100), unique=False, nullable=False)
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    approved = db.Column(db.Boolean, nullable=False, default=False)
    
    email_verification_token = db.relationship('EmailVerificationToken', backref=db.backref('user', lazy=True), uselist=False)
    password_reset_token = db.relationship('PasswordResetToken', backref=db.backref('user', lazy=True), uselist=False)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


class EmailVerificationToken(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    token = db.Column(db.String(60), unique=False, nullable=False)


class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    token = db.Column(db.String(60), unique=False, nullable=False)


class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    currency_code = db.Column(db.String(3), unique=True, nullable=False)

    def __repr__(self):
        return f"<Country: {self.name}, {self.currency_code}>"


class Basket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<Basket: {self.name}>"


class PurchasingPowerParity(db.Model):
    year = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), primary_key=True)
    basket_id = db.Column(db.Integer, db.ForeignKey('basket.id'), primary_key=True)
    value = db.Column(db.Float, unique=False, nullable=False)

    country = db.relationship('Country', backref=db.backref('purchasing_power_parities', lazy=True))
    basket = db.relationship('Basket', backref=db.backref('purchasing_power_parities', lazy=True))


class ExchangeRate(db.Model):
    year = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), primary_key=True)
    value = db.Column(db.Float, unique=False, nullable=False)

    country = db.relationship('Country', backref=db.backref('exchange_rates', lazy=True))
