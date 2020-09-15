from os import remove
from pathlib import Path

from secrets import token_urlsafe
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from app import app, db, bcrypt, mail
from app.forms import RegistrationForm, LoginForm, ResendEmailVerificationRequestForm, ResetPasswordRequestForm, ResetPasswordForm, UploadForm
from app.models import User, EmailVerificationToken, PasswordResetToken, Country, Basket, PurchasingPowerParity, ExchangeRate
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import requests
from requests.auth import HTTPBasicAuth

from app.extract import extract_data


def generate_token():
    token = token_urlsafe(app.config['TOKEN_LENGTH'])
    hashed_token = bcrypt.generate_password_hash(token).decode('utf-8')
    return token, hashed_token

def send_email_verification_email(user, token):
    email_subject = "Purchasing Power Parities Calculator Registration"
    email_body = render_template('email/verify_email.html',
        root_url=app.config['ROOT_URL'],
        user=user,
        email_verification_token=token)
    message = Message(sender=app.config["MAIL_USERNAME"],
        recipients=[user.email_address],
        subject=email_subject,
        html=email_body)
    mail.send(message)

def send_password_reset_email(user, token):
    email_subject = "Purchasing Power Parities Calculator Password Reset"
    email_body = render_template('email/reset_password.html',
        root_url=app.config['ROOT_URL'],
        user=user,
        password_reset_token=token)
    message = Message(sender=app.config["MAIL_USERNAME"],
        recipients=[user.email_address],
        subject=email_subject,
        html=email_body)
    mail.send(message)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('calculator'))
    param_email_address = request.args.get("email")
    if param_email_address is not None:
        form = LoginForm(email_address=param_email_address)
    else:
        form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user and user.verified and user.approved and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('calculator'))
        else:
            flash('Login unsuccessful. Please check the entered Email address and password. Alternatively, ensure that you have verified your Email address and that you have been approved by the administrator.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/register/<key>", methods=['GET', 'POST'])
def register(key):
    if key != app.config['REGISTER_KEY']:
        abort(404)
    if current_user.is_authenticated:
        return redirect(url_for('calculator'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        token, hashed_token = generate_token()
        
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email_address=form.email_address.data,
            password=hashed_password)
        
        EmailVerificationToken(user=user, token=hashed_token)
        
        db.session.add(user)
        db.session.commit()
        
        send_email_verification_email(user, token)
        
        flash('Your account has been created! Please check your inbox / spam folder for your verification Email.', 'success')
        return redirect(url_for('login', email=form.email_address.data))
    return render_template('register.html', title='Register', form=form)

@app.route("/lost", methods=['GET', 'POST'])
def lost_verification_email():
    form = ResendEmailVerificationRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user and not user.verified:
            token, hashed_token = generate_token()
            user.email_verification_token.token = hashed_token
            db.session.commit()
            send_email_verification_email(user, token)
        
        flash('Please check your inbox / spam folder for your verification Email.', 'success')
        return redirect(url_for('login', email=form.email_address.data))
    return render_template('lost.html', form=form)

@app.route("/forgot", methods=['GET', 'POST'])
def forgot_password():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user:
            token, hashed_token = generate_token()
            token_obj = PasswordResetToken(token=hashed_token, user=user)
            db.session.add(token_obj)
            db.session.commit()
            send_password_reset_email(user, token)
        
        flash('Please check your inbox / spam folder for your password reset Email.', 'success')
    return render_template('forgot.html', form=form)

@app.route("/verify", methods=['GET'])
def verify():
    param_email_address = request.args.get("email")
    param_email_verification_token = request.args.get("token")
    user = User.query.filter_by(email_address=param_email_address).first()
    if user:
        if not user.verified:
            if bcrypt.check_password_hash(user.email_verification_token.token, param_email_verification_token):
                user.verified = True
                db.session.delete(user.email_verification_token)
                db.session.commit()
                flash("Email address successfully verified.", 'success')
    return redirect(url_for('login', email=param_email_address))

@app.route("/reset", methods=['GET', 'POST'])
def reset():
    param_email_address = request.args.get("email")
    param_password_reset_token = request.args.get("token")
    user = User.query.filter_by(email_address=param_email_address).first()
    form = ResetPasswordForm(email_address=param_email_address)
    if user and user.password_reset_token and bcrypt.check_password_hash(user.password_reset_token.token, param_password_reset_token):
        if form.validate_on_submit():
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            db.session.delete(user.password_reset_token)
            db.session.commit()
            flash("Password successfully reset.", 'success')
            return redirect(url_for('login', email=param_email_address))
        return render_template('reset.html', form=form)
    return redirect(url_for('login', email=param_email_address))

@login_required
@app.route("/logout")
def logout():
    email_address = current_user.email_address
    logout_user()
    return redirect(url_for('login', email=email_address))

@login_required
@app.route("/upload", methods=['GET', 'POST'])
def upload_spreadsheet():
    if current_user.is_authenticated:
        form = UploadForm()
        if form.validate_on_submit():
            ppp_spreadsheet_filepath = Path("app", app.config["UPLOAD_FOLDER"], form.ppp_spreadsheet.data.filename)
            xr_spreadsheet_filepath = Path("app", app.config["UPLOAD_FOLDER"], form.xr_spreadsheet.data.filename)
            countries_json_filepath = Path("app", app.config["UPLOAD_FOLDER"], form.countries_json.data.filename)
            
            form.ppp_spreadsheet.data.save(ppp_spreadsheet_filepath)
            form.xr_spreadsheet.data.save(xr_spreadsheet_filepath)
            form.countries_json.data.save(countries_json_filepath)

            try:
                extract_data(ppp_spreadsheet_filepath, xr_spreadsheet_filepath, countries_json_filepath)
                db.session.commit()
                success = True
            except Exception as e:
                print(e)
                db.session.rollback()
                flash("Failed to extract data from uploaded files. Please ensure the files have the appropriate structure.", 'danger')
                success = False            
            
            remove(ppp_spreadsheet_filepath)
            remove(xr_spreadsheet_filepath)
            remove(countries_json_filepath)
            
            if success:
                flash("Successfully extracted data from uploaded files.", 'success')
                return redirect(url_for('calculator'))
        return render_template('upload.html', form=form)
    return redirect(url_for('calculator'))

@app.route("/")
def calculator():
    return render_template('calculator.html')

@login_required
@app.route("/fetch/init", methods=['GET'])
def fetch_init():
    version = 43
    years = [row[0] for row in db.session.query(PurchasingPowerParity.year).distinct(PurchasingPowerParity.year).all()]
    data = {"version": version, "years": years}
    return jsonify(data)

@login_required
@app.route("/fetch/country", methods=['GET'])
def fetch_country():
    version = 43
    year = request.args.get("year")
    countries = db.session.query(Country.id, Country.name, Country.currency_code).distinct(Country.id).order_by(Country.id).join(PurchasingPowerParity).filter_by(year=year).all()
    baskets = db.session.query(Basket.id, Basket.name).distinct(Basket.id).order_by(Basket.id).join(PurchasingPowerParity).filter_by(year=year).all()
    data = {
        "version": version,
        "countries": countries,
        "baskets": baskets
    }
    return jsonify(data)

@login_required
@app.route("/fetch/convert", methods=['GET'])
def fetch_convert():
    version = 43
    year = request.args.get("year")
    origin_id = request.args.get("origin")
    destination_id = request.args.get("destination")
    basket_id = request.args.get("basket")
    
    origin_ppp, = db.session.query(PurchasingPowerParity.value).filter_by(
        year=year,country_id=origin_id, basket_id=basket_id).first()
    destination_ppp, = db.session.query(PurchasingPowerParity.value).filter_by(
        year=year,country_id=destination_id, basket_id=basket_id).first()
    origin_exchange_rate, = db.session.query(ExchangeRate.value).filter_by(
        year=year,country_id=origin_id).first()
    destination_exchange_rate, = db.session.query(ExchangeRate.value).filter_by(
        year=year,country_id=destination_id).first()
    
    ppp = destination_ppp / origin_ppp
    exchange_rate = origin_exchange_rate / destination_exchange_rate
    data = {"version": version, "ppp": ppp, "exchange_rate": exchange_rate}
    return jsonify(data)

@app.route("/faq")
def faq():
    return render_template("faq.html")
