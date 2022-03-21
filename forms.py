from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL


##WTForm

class RegisterForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    name = StringField(label="Name", validators=[DataRequired()])
    submit = SubmitField(label='Register')


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label='Login')


