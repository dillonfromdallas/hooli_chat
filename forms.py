from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import (DataRequired, Email, Regexp, ValidationError,
                                Length, EqualTo)
from Models import User


def nameExists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError("User with that name already exists.")

def emailExists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError("User with that email already exists.")

class RegisterForm(Form):
    username = StringField('Username',
                           validators=[
                               DataRequired(),
                               Regexp(
                                   r'^[a-zA-z0-9_]+$',
                                   message = ("Username should be one word, letters, "
                                             "numbers, and underscores only.")
                               ),
                               nameExists
                           ])

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            emailExists
        ])

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=4),
            EqualTo('password2', message = "Passwords must match")
        ])

    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class PostForm(Form):
    content = TextAreaField("What's goin' on?", validators=[DataRequired()])