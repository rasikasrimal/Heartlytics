"""WTForms classes for authentication views."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class LoginForm(FlaskForm):
    """Form used on the login page."""

    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class SignupForm(FlaskForm):
    """Form used for both public sign-up and admin user creation."""

    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    nickname = StringField("Nickname", validators=[Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8),
            Regexp(
                r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).+$",
                message="Password must include upper, lower, number and special character",
            ),
        ],
    )
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    role = SelectField(
        "Role",
        choices=[
            ("User", "User"),
            ("Doctor", "Doctor"),
            ("Admin", "Admin"),
            ("SuperAdmin", "Super Admin"),
        ],
        default="User",
    )
    submit = SubmitField("Submit")

