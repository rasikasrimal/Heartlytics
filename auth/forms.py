"""WTForms classes for authentication views."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class LoginForm(FlaskForm):
    """Form used on the login page."""

    identifier = StringField(
        "Email or Username", validators=[DataRequired(), Length(max=120)]
    )
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


class ForgotPasswordForm(FlaskForm):
    """Step 1: identify account by email or username."""

    identifier = StringField(
        "Email or Username", validators=[DataRequired(), Length(max=120)]
    )
    submit = SubmitField("Search")


class VerifyCodeForm(FlaskForm):
    """Step 2: enter verification code."""

    code = StringField("Verification Code", validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField("Continue")


class EmailCodeForm(FlaskForm):
    """Form for entering an email one-time code."""

    code = StringField("Verification Code", validators=[DataRequired(), Length(min=6, max=8)])
    submit = SubmitField("Verify")


class ResetPasswordForm(FlaskForm):
    """Step 3: choose a new password."""

    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8),
            Regexp(
                r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).+$",
                message="Password must include upper, lower, number and special character",
            ),
        ],
    )
    confirm = PasswordField("Repeat New Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Update Password")


class TOTPSetupForm(FlaskForm):
    """Collect the initial TOTP code when enabling MFA."""

    code = StringField("Authentication Code", validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField("Enable")


class TOTPVerifyForm(FlaskForm):
    """Validate a TOTP or recovery code during login."""

    code = StringField(
        "Authentication Code",
        validators=[DataRequired(), Length(min=6, max=16)],
    )
    submit = SubmitField("Verify")


class MFADisableForm(FlaskForm):
    """Confirm credentials to disable MFA on an account."""

    password = PasswordField("Current Password", validators=[DataRequired()])
    code = StringField(
        "Authentication or Recovery Code",
        validators=[DataRequired(), Length(min=6, max=16)],
    )
    submit = SubmitField("Disable")

