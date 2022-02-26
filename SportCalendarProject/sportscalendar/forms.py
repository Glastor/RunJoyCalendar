from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from sportscalendar.models import *

class RegistrationForm(FlaskForm):
    lastname = StringField("Vezetéknév",
                           validators=[DataRequired(), Length(min=2, max=50)])
    firstname = StringField("Keresztnév",
                           validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email",
                        validators=[Email(), DataRequired()])
    password = PasswordField("Jelszó",
                             validators=[DataRequired(), Length(min=2, max=20)])
    confirm_password = PasswordField("Jelszó Újra",
                                     validators=[DataRequired(), Length(min=2, max=20), EqualTo("password")])
    submit = SubmitField("Sign Up")
    terms = BooleanField("Elfogadom a felhasználási feltételeket")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email cím már használt!")

    def validate_terms(self, terms):
        if terms.data == False:
            raise ValidationError("Fogadd el a feltételeket")

class LoginForm(FlaskForm):
    email = StringField("E-mail",
                        validators=[Email(), DataRequired()])
    password = PasswordField("Jelszó",
                             validators=[DataRequired()])
    remember = BooleanField("Emlékezz rám")
    submit = SubmitField("Belépés")

class RequestResetPasswordForm(FlaskForm):
    email = StringField("E-mail",
                        validators=[Email(), DataRequired()])
    submit = SubmitField("Új jelszót kérek")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("Nincs felhasználó ilyen e-mail címmel! Először regisztrálnod kell!")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Új Jelszó",
                             validators=[DataRequired(), Length(min=2, max=20)])
    confirm_password = PasswordField("Új Jelszó Újra",
                                     validators=[DataRequired(), Length(min=2, max=20), EqualTo("password")])
    submit = SubmitField("Új jelszó beállítása")

class UpdateAccountForm(FlaskForm):
    email = StringField("E-mail megváltoztatása",
                        validators=[Email(), DataRequired()])
    newsletter = BooleanField("Kérek hírlevelet")
    picture = FileField('Profilkép Feltöltése',
                        validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Változtatások mentése")


    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Email cím már használt!")

    def validate_terms(self, terms):
        if terms.data == False:
            raise ValidationError("Fogadd el a feltételeket")