from sportscalendar import db, login_manager, admin, MyModelView, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --------------------------- USER RACE MANY TO MANY RELATIONSHIP HANDLING ----------------------------------
user_race = db.Table("user_race",
            db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
            db.Column("race_id", db.Integer, db.ForeignKey("race.id"))
)
# --------------------------- USER Database table ----------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(220), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    newsletter = db.Column(db.Boolean, nullable=False, default=True)
    reg_date = db.Column(db.Date, nullable=False)
    is_premium = db.Column(db.Boolean, nullable=False)
    profile_pic = db.Column(db.String(255), default='default.png')
    following = db.relationship ("Race", secondary=user_race, backref="followers")


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

# --------------------------- EVENT Database table ----------------------------------
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    event_description = db.Column(db.String(5000), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    organizer = db.Column(db.String(120), nullable=False)
    organizer_url = db.Column(db.String(1500), nullable=True)
    gps = db.Column(db.String(5000), nullable=True)
    event_url = db.Column(db.String(1500), nullable=False)
    event_pic_url = db.Column(db.String(1500), nullable=False)
    event_face_url = db.Column(db.String(1500), nullable=True)
    medal_url = db.Column(db.String(1500), nullable=True)
    race_types = db.Column(db.String(500), nullable=True)
    banner_url = db.Column(db.String(5000))
    races = db.relationship("Race", backref="event", lazy=True)


# --------------------------- RACE Database table ----------------------------------
class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    cutoff = db.Column(db.String(50), nullable=True)
    map_url = db.Column(db.String(1500), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)


# -------------------------- Admin Page database View -----------------------------
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Event, db.session))
admin.add_view(MyModelView(Race, db.session))