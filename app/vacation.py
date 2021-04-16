# Standard libary imports
from datetime import datetime, timedelta, date
import time

# Third pary imports
from flask import render_template, session, redirect, url_for, request, Blueprint, flash
from flask_login import login_required, current_user

# Local application imports
from .models import User, Vacation, Illness
from . import db


vac = Blueprint('vac', __name__)


@vac.route('/vacation', methods=['GET', 'POST'])
@login_required
def vacation():
    if request.method == 'POST':
        start_date = datetime.strptime(
            request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(
            request.form.get('end_date'), '%Y-%m-%d')
        dif = get_workdays(start_date, end_date)
        user = User.query.filter_by(
            id=session.get('user_id')).first()
        vacation_days = user.vacation_days
        vacation_days_taken = user.vacation_days_taken
        vacation_days_available = vacation_days - vacation_days_taken
        if start_date > end_date:
            flash(
                'You selected a start date before your end date! Please try again.', category='danger')
            return redirect(url_for('vac.vacation'))
        else:
            if dif <= vacation_days_available:
                user = User.query.filter_by(id=session.get('user_id')).first()
                req = Vacation(start_date=start_date,
                               end_date=end_date, user=user)
                db.session.add(req)
                db.session.commit()
                flash('Successfully handed in your vacation request.',
                      category='success')
                return redirect(url_for('vac.vacation'))
            else:
                flash(
                    'You selected a period that exceeds your available vacation days!', category='danger')
                return redirect(url_for('vac.vacation'))
    user = User.query.filter_by(id=session.get('user_id')).first()
    requests = Vacation.query.filter_by(user_id=user.id).all()
    return render_template('vacation.html', user=current_user, requests=requests, roles_id=session.get('roles_id'))


@vac.route('/vacation_requests', methods=['GET', 'POST'])
@login_required
def vacation_requests():
    if request.method == 'POST':
        if request.form.get('accept-button'):
            request_id = request.form.get('accept-button')
            req = Vacation.query.filter_by(id=request_id).first()
            req.approved = True
            db.session.add(req)
            db.session.commit()
            flash('You successfully accepted the Vacation Request.',
                  category='success')
            return redirect(url_for('vac.vacation_requests'))
        elif request.form.get('reject-button'):
            request_id = request.form.get('reject-button')
            Vacation.query.filter_by(id=request_id).delete()
            db.session.commit()
            flash('You succesfully rejected the Vacation request. The employee is getting notified.', category='warning')
            return redirect(url_for('vac.vacation_requests'))

    requests = Vacation.query.all()
    users = User.query.all()
    return render_template('vacation_requests.html', requests=requests, user=current_user,  users=users, User=User, roles_id=session.get('roles_id'))


def get_workdays(from_date: datetime, to_date: datetime):
    # if the start date is on a weekend, forward the date to next Monday
    if from_date.weekday() > 4:
        from_date = from_date + timedelta(days=7 - from_date.weekday())
    # if the end date is on a weekend, rewind the date to the previous Friday
    if to_date.weekday() > 4:
        to_date = to_date - timedelta(days=to_date.weekday() - 4)
    if from_date > to_date:
        return 0
    # that makes the difference easy, no remainders etc
    diff_days = (to_date - from_date).days + 1
    weeks = int(diff_days / 7)
    return weeks * 5 + (to_date.weekday() - from_date.weekday()) + 1
