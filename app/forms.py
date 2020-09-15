from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

from app.models import User


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email_address = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('REGISTER')

    def validate_email_address(self, email_address):
        user = User.query.filter_by(email_address=email_address.data).first()
        if user:
            raise ValidationError('That Email address is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email_address = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('LOGIN')


class ResendEmailVerificationRequestForm(FlaskForm):
    email_address = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('RESEND')


class ResetPasswordRequestForm(FlaskForm):
    email_address = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('SEND')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    repeat_password = PasswordField('Repeat Password', validators=[EqualTo('password', message="Passwords must match")])
    submit = SubmitField('RESET')


class UploadForm(FlaskForm):
    ppp_spreadsheet = FileField('PPP Spreadsheet', validators=[FileRequired(), FileAllowed(['xls', 'xlsx'], 'Spreadsheet Files')])
    xr_spreadsheet = FileField('XR Spreadsheet', validators=[FileRequired(), FileAllowed(['xls', 'xlsx'], 'Spreadsheet Files')])
    countries_json = FileField('Countries JSON', validators=[FileRequired(), FileAllowed(['json'], 'JSON Files')])
    submit = SubmitField('UPLOAD')
