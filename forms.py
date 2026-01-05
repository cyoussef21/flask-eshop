from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField, IntegerField, DecimalField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email, URL, NumberRange

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign-In')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign-Up')

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    discount = DecimalField('Discount', validators=[DataRequired(), NumberRange(min=0.01, max=0.99, message='Discount must be between 0.01 and 0.99')])
    thumbnail = StringField('Thumbnail', validators=[DataRequired(), URL()])
    image = StringField('Image', validators=[DataRequired(), URL()])
    category = SelectField('Category', validators=[DataRequired()])
    stock = IntegerField('Stock', validators=[DataRequired()])
    submit = SubmitField('Submit Product')



