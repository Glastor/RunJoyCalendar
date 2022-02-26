import os
from flask import Flask, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail

os.environ['EMAIL_USER'] = "gcsteszt007@gmail.com"
os.environ['EMAIL_PASS'] = "kngxgvulgrihbudr"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MySecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = True
app.config["MAIL_USERNAME"] = os.environ.get('EMAIL_USER')
app.config["MAIL_PASSWORD"] = os.environ.get('EMAIL_PASS')


mail = Mail(app)


login_manager = LoginManager()
login_manager.init_app(app)

# -------------------- ADMIN Page authentication handling --------------------------------
class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.firstname == "Admin":
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.firstname == "Admin":
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))

admin = Admin(app, index_view=MyAdminIndexView())

from sportscalendar import routes