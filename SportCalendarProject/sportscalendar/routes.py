from sportscalendar.models import *
from sportscalendar.forms import RegistrationForm, LoginForm, RequestResetPasswordForm, ResetPasswordForm,UpdateAccountForm
from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import locale
import urllib.parse
from sportscalendar import app, mail
from flask_mail import Message
from sqlalchemy import and_, or_, any_, extract
import secrets
import os

def get_followers():
    events_data = Event.query.all()
    followers_list = []
    for event in events_data:
        i = 0
        for race in event.races:
            i += len(race.followers)
        followers_list.append(i)
    return followers_list

def get_races_data(year, **kwargs):
    year = year
    for key, value in kwargs.items():
        if key == "distance" and value == 5:
            races = Race.query.order_by(Race.start_date.asc()).filter(and_(
                extract('year', Race.start_date)==year,
                Race.distance <= 9,
                Race.distance >= 5
                )
            )
            break
        elif key == "distance" and value == 10:
            races = Race.query.order_by(Race.start_date.asc()).filter(and_(
                extract('year', Race.start_date)==year,
                Race.distance <= 15,
                Race.distance >= 9
                )
            )
            break
        elif key == "distance" and value == 21:
            races = Race.query.order_by(Race.start_date.asc()).filter(and_(
                extract('year', Race.start_date)==year,
                Race.distance <= 30,
                Race.distance >= 15
                )
            )
            break
        elif key == "distance" and value == 42:
            races = Race.query.order_by(Race.start_date.asc()).filter(and_(
                extract('year', Race.start_date)==year,
                Race.distance <= 45,
                Race.distance >= 30
                )
            )
            break
        elif key == "type" and value == "Ultra":
            races = Race.query.order_by(Race.start_date.asc()).filter(and_(
                extract('year', Race.start_date)==year,
                Race.type == "Ultra",
                )
            )
            break
        elif key == "type" and value == "Road":
            races = Race.query.order_by(Race.start_date.asc()).filter(and_(
                extract('year', Race.start_date)==year,
                Race.type == "Road",
                )
            )
            break
        elif key == "type" and value == "Trail":
            races = Race.query.order_by(Race.start_date.asc()).filter(and_(
                extract('year', Race.start_date)==year,
                Race.type == "Trail",
                )
            )
            break
        elif key == "type" and value == "Obstacle":
            races = Race.query.order_by(Race.start_date.asc()).filter(and_(
                extract('year', Race.start_date)==year,
                Race.type == "Obstacle",
                )
            )
            break
        elif key == "type" and value == "Relay":
            races = Race.query.order_by(Race.start_date.asc()).filter(and_(
                extract('year', Race.start_date)==year,
                Race.type == "Relay",
                )
            )
            break
        else:
            races = Race.query.order_by(Race.start_date.asc()).filter(
                extract('year', Race.start_date)==year)

    return races

def get_events(country, year, month):
    year = year
    country = country
    month = month
    events = Event.query.order_by(Event.start_date.asc()).filter(and_(
                extract('year', Event.start_date)==year,
                extract('month', Event.start_date) == month,
                Event.country == country,
                )
            )
    return events

locale.setlocale(locale.LC_TIME, 'hu_HU')

@app.route("/", defaults={'year': datetime.now().strftime("%Y")}, methods=["GET", "POST"])
@app.route("/<year>", methods=["GET", "POST"])
def home(year):
    country = request.args.get('country', 'Hungary')
    year = year
    month = request.args.get('month', datetime.now().strftime("%m"))
    print(country, month)
    followers = get_followers()
    if month == 'all':
        events_data = Event.query.all()
    else:
        events_data = get_events(country=country, year=year, month=month)

    return render_template("index.html",
                           events_data=events_data,
                           followers=followers,
                           country=country,
                           year=year,
                           month = month

                           )

@app.route("/search", methods=["GET", "POST"])
def search():
    followers = get_followers()
    year = datetime.now().strftime("%Y")
    if request.method == "POST":
        form = request.form
        search_value = form['search_string']
        search = "%{}%".format(search_value)
        events_data = Event.query.order_by(Event.start_date.asc()).filter(and_(
                extract('year', Event.start_date)==year,
                or_(Event.name.like(search), Event.race_types.like(search), Event.city.like(search), Event.organizer.like(search))
                )
            ).all()
        return render_template("index.html",
                           events_data=events_data,
                           followers=followers,
                           year=year,
                           search_value=search_value
                           )
    else:
        redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    loginform = LoginForm()
    regform = RegistrationForm()
    if loginform.validate_on_submit():
        # Find user by email entered.
        user = User.query.filter_by(email=loginform.email.data).first()
        if not user:
            flash("That email does not exist, please try again.", "danger")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, loginform.password.data):
            flash("Password incorrect, please try again.", "danger")
            return redirect(url_for('login'))
            # Email exists and password correct
        else:
            login_user(user, remember=loginform.remember.data)
            flash("Successful login", "success")
            return redirect(url_for('home'))

    return render_template("sign-in.html",
                           loginform=loginform,
                           regform=regform
                           )

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    loginform = LoginForm()
    regform = RegistrationForm()
    if regform.validate_on_submit():
        if regform.terms.data == True:
            hashed_password =generate_password_hash(regform.password.data, method='pbkdf2:sha256', salt_length=8)
            flash(f"Account created for {regform.lastname.data}", "success")
            new_user = User(firstname=regform.firstname.data,
                            lastname=regform.lastname.data,
                            email=regform.email.data,
                            password=hashed_password,
                            newsletter=True,
                            reg_date=datetime.date.today(),
                            is_premium=False)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('home', user=new_user))


    return render_template("sign-in.html",
                           regform=regform,
                           loginform=loginform
                           )

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/event", methods=["GET", "POST"])
def event():
    event_id = request.args.get('id')
    event = Event.query.get(event_id)
    followers = get_followers()
    event_gps = urllib.parse.quote_plus(event.gps)
    races = event.races
    return render_template("event.html",
                           event=event,
                           races=races,
                           followers=followers,
                           event_gps=event_gps
                           )
def get_races_datas(races):
    done_races_number_this_year = 0
    done_races_km_this_year = 0.0
    races_left_this_year = 0
    all_races = 0
    all_km = 0.0

    for race in races:
        if race.start_date <= datetime.now():
            all_races += 1
            all_km += float(race.distance)

        if race.start_date <= datetime.now() and race.start_date.year == datetime.now().year:
            done_races_number_this_year += 1
            done_races_km_this_year += float(race.distance)
        elif race.start_date.year == datetime.now().year:
            races_left_this_year += 1
    return done_races_number_this_year, done_races_km_this_year, races_left_this_year, all_km, all_races

def save_picture(form_pictrue):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pictrue.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/image/profile_pics', picture_fn)
    form_pictrue.save(picture_path)
    return picture_fn

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_pic = picture_file
        current_user.email = form.email.data
        current_user.newsletter = form.newsletter.data
        id = current_user.id
        db.session.commit()
        flash("Felhasználói adatok frisstve!", "success")
        return redirect(url_for("dashboard", id=id))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.newsletter.data = current_user.newsletter
    today = datetime.now()
    user_id = request.args.get('id')
    user = User.query.get(user_id)
    races = current_user.following
    datas = get_races_datas(races)
    image_file = url_for('static', filename='/image/profile_pics/' + current_user.profile_pic)
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.newsletter = form.newsletter.data
        db.session.commit()
        flash("Felhasználói adatok frisstve!", "success")
        return redirect(url_for("dashboard"))
    elif request.method == 'GET':
        form.newsletter.data = current_user.newsletter
    print(datas)
    return render_template("dashboard.html",
                           logged_in=True,
                           user=user,
                           races=races,
                           today=today,
                           races_this_year=datas[0],
                           km_this_year=datas[1],
                           races_left=datas[2],
                           all_km=datas[3],
                           all_races=datas[4],
                           image_file=image_file,
                           form=form
                           )

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Jelszó változtatási kérelem",
                  sender="gcsteszt007@gmail.com",
                  recipients=[user.email],)
    msg.body = f''' Jelszó megváltoztatásához kattints a következő linkre:
    {url_for('reset_token', token=token, _external=True)}
    
    Ha nem te kérted az új jelsző létrehozásának lehetőségét egyszerűen csak töröld a levelet. 
    Az adataid biztonságban vannak.
    '''
    mail.send(msg)

@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Email elküldve a megadott e-mail címre.', 'warning')
        return redirect(url_for('login'))

    return render_template("reset_request.html",
                           form=form,
                           )

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Érvénytelen vagy lejárt token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        user.password = hashed_password
        db.session.commit()
        flash(f"Jelsző megváltozott!", 'warning')
        return redirect(url_for('login', user=user))
    return render_template("reset_token.html",
                           form=form,
                           )


@app.route("/add_race", methods=["GET", "POST"])
@login_required
def add_race():
    race_id = request.args.get('race_id')
    race = Race.query.get(race_id)
    user = User.query.get(current_user.id)
    user.following.append(race)
    db.session.commit()
    flash('Verseny hozzáadva a sajátokhoz', 'warning')
    return redirect(request.referrer)

@app.route("/remove_race", methods=["GET", "POST"])
@login_required
def remove_race():
    race_id = request.args.get('race_id')
    race = Race.query.get(race_id)
    user = User.query.get(current_user.id)
    user.following.remove(race)
    db.session.commit()
    flash('Verseny eltávolítva', 'warning')
    return redirect(request.referrer)


@app.route("/races", defaults={'year': datetime.now().strftime("%Y")})
@app.route("/races/<year>", methods=["GET", "POST"])
def races(year):
    if request.args.get('distance') != None:
        dist = int(request.args.get('distance'))
    else:
        dist=0
    typ = request.args.get('type')
    print(dist)
    print(typ)
    year = year
    print(year)
    today_date = datetime.now()
    nextyear = today_date + relativedelta(years=1)
    yearafter = today_date + relativedelta(years=2)
    races= get_races_data(year, distance=dist, type=typ)
    # races= Race.query.order_by(Race.start_date.asc()).filter(extract('year', Race.start_date)==year)
    return render_template("races.html",
                           races=races,
                           year=year,
                           thisyear=today_date,
                           nextyear=nextyear,
                           yearafter=yearafter,
                           )



@app.route("/calendar-view")
def calendar_view():
    country = request.args.get('country', 'Hungary')
    year = datetime.now().strftime("%Y")
    month = request.args.get('month', datetime.now().strftime("%m"))
    events_data = Event.query.all()
    print(events_data)
    return render_template("calendar_view.html",
                           events_data=events_data,
                           country=country,
                           year=year,
                           month=month
                           )