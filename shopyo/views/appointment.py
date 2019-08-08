from flask import (
        Blueprint, 
        render_template, 
        request, 
        redirect, 
        jsonify
)
from flask_login import login_required, current_user
from flask_marshmallow import Marshmallow

from addon import db, ma
from models import Appointments
#from app import  app
from settings import get_value


appointment_blueprint = Blueprint('appointment', __name__, url_prefix='/appointment')

#ma = Marshmallow(app)

class AppointmentSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'name', 'date', 'time', 'active')

appointment_schema = AppointmentSchema()
appointment_schema = AppointmentSchema(many=True)

@appointment_blueprint.route("/")
@login_required
def appointment_main():
    return render_template('appointment/index.html', 
                            appointments=Appointments.query.all(),
                            OUR_APP_NAME=get_value('OUR_APP_NAME'), 
                            SECTION_NAME=get_value('SECTION_NAME')
                        )


@appointment_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def appointment_add():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        active = request.form['active']
        time = request.form['time']
        m = Appointments(name=name, date=date, time=time, active=active)
        db.session.add(m)
        db.session.commit()
        return redirect('/appointment/add')
    return render_template('appointment/add.html', OUR_APP_NAME=get_value('OUR_APP_NAME'))


@appointment_blueprint.route('/delete/<ids>', methods=['GET', 'POST'])
@login_required
def appointment_delete(ids):
    Appointments.query.filter(Appointments.id == ids).delete()
    db.session.commit()
    return redirect('/appointment')


@appointment_blueprint.route('/edit/<ids>', methods=['GET', 'POST'])
@login_required
def appointment_edit(ids):
    a = Appointments.query.get(ids)
    return render_template('appointment/edit.html', id=a.id,
                           name=a.name, date=a.date,
                           time=a.time, active=a.active,
                           OUR_APP_NAME=get_value('OUR_APP_NAME'), 
                           SECTION_ITEMS=get_value('SECTION_ITEMS')
                        )


@appointment_blueprint.route('/update', methods=['GET', 'POST'])
@login_required
def appointment_update():
    appointment_name = request.form['appointment_name']
    appointment_date = request.form['appointment_date']
    appointment_time = request.form['appointment_time']
    appointment_id = request.form['appointment_id']
    appointment_active = request.form['appointment_active']
    s = Appointments.query.get(appointment_id)
    s.name = appointment_name
    s.date = appointment_date
    s.time = appointment_time
    s.active = appointment_active
    db.session.commit()
    return redirect('/appointment')


@appointment_blueprint.route('/active/<ids>', methods=['GET', 'POST'])
@login_required
def active(ids):
    s = Appointments.query.get(ids)
    s.active = "active"
    db.session.commit()
    return redirect('/appointment')


@appointment_blueprint.route('/inactive/<ids>', methods=['GET', 'POST'])
@login_required
def deactive(ids):
    s = Appointments.query.get(ids)
    s.active = "inactive"
    db.session.commit()
    return redirect('/appointment')

@appointment_blueprint.route('/lookup', methods=['GET', 'POST'])
@login_required
def lookup():
    return render_template('appointment/lookup.html', 
                           OUR_APP_NAME=get_value('OUR_APP_NAME'), 
                           SECTION_ITEMS=get_value('SECTION_ITEMS'))

# api
@appointment_blueprint.route('/search/name/<name>', methods=['GET', 'POST'])
@login_required
def search_name(name):
    all_a = Appointments.query.filter(Appointments.name.like('%'+name+'%')).all()
    result = appointment_schema.dump(all_a)
    return jsonify(result.data)
