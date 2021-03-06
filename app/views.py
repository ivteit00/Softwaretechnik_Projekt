# Standard libary imports
from datetime import datetime, timedelta, date
import time

# Third pary imports
from flask import render_template, session, redirect, url_for, request, Blueprint, flash
from flask_login import login_required, current_user
from workdays import networkdays


# Local application imports
from .models import User, Vacation, Illness, Notification
from . import db


views = Blueprint('views', __name__)

# MA-home-viewfunction


@views.route('/home', methods=['GET', 'POST'])
@login_required
def home() -> 'html':
    """viewfunction for home view"""
    if request.method == 'POST':
        # check if the http request was a post request

        # the following if statements check which of the close buttons was clicked
        # in order to delete the notification
        if request.form.get('close-vacation'):
            req_id = request.form.get('close-vacation')
            req = Vacation.query.filter_by(id=req_id).first()
            req.notify = False
            db.session.add(req)
            db.session.commit()
            return redirect(url_for('views.home'))
        if request.form.get('close-case'):
            case_id = request.form.get('close-case')
            req = Illness.query.filter_by(id=case_id).first()
            req.notify = False
            db.session.add(req)
            db.session.commit()
            return redirect(url_for('views.home'))
        if request.form.get('close-notification'):
            noti_id = request.form.get('close-notification')
            Notification.query.filter_by(id=noti_id).delete()
            db.session.commit()
            return redirect(url_for('views.home'))

    # code executed if the http request is not a POST request
    # return the rendered template which the user can see

    user = User.query.filter_by(id=session.get('user_id')).first()
    today = date.today()
    first_date = date.today().replace(day=1)
    hours_till_today = networkdays(first_date, today) * 8
    requests = Vacation.query.filter_by(user_id=user.id, approved=True).all()
    cases = Illness.query.filter_by(user_id=user.id, approved=True).all()
    notifications = Notification.query.filter_by(user_id=user.id).all()
    # till this point the code above querys the database in order to display all the relevant
    # informations about the user
    return (render_template('home.html',
                            full_name=session.get('full_name'),
                            user=current_user,
                            roles_id=session.get('roles_id'),
                            user_data=user,
                            hours_till_today=hours_till_today,
                            requests=requests,
                            cases=cases,
                            notifications=notifications),
            200,
            {'location': '/home'})
