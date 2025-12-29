from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign-In')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign-Up')



