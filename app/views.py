# Функции маршрутизации и представления веб-приложения
# Разработал студент группы А-07-16 Бахтин Евгений
# Версия 1.0
import secrets
import uuid
from datetime import datetime

import flask_excel as excel
from flask import request, url_for, flash, render_template, Response
from flask_login import login_required, logout_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect

from app import app
from app.models import Users, TemperatureSensor, PressureSensor
from app.utils import authorize, load_xlsx, chart_value_generator


@app.route('/', methods=['GET', 'POST'])
def auth():
    login = request.form.get('login')
    password = request.form.get('password')
    if login and password:
        if authorize(login, password):
            if login == "admin":
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('staff'))
        else:
            flash('Неверный логин или пароль')
            return render_template("auth_page.html")
    else:
        flash('Введите логин и пароль')
    return render_template("auth_page.html")


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    users = list(Users.objects.values_list('id', 'login'))
    temperature_sensors = list(TemperatureSensor.objects.distinct().values_list('sensor_id', flat=True))
    pressure_sensors = list(PressureSensor.objects.distinct().values_list('sensor_id', flat=True))
    if request.method == 'POST':
        sensor_form = request.form.get('sensor')
        user_form = request.form.get('user')
        if sensor_form == 'add':
            if request.form.get('sensor_type') == 'temperature':
                TemperatureSensor.create(sensor_id=uuid.uuid4(), measure_timestamp=datetime.utcnow(), value=0)
                return redirect(url_for('admin'))
            elif request.form.get('sensor_type') == 'pressure':
                PressureSensor.create(sensor_id=uuid.uuid4(), measure_timestamp=datetime.utcnow(), value=0)
                return redirect(url_for('admin'))
        elif sensor_form == 'drop':
            id_for_drop = request.form.get('id_for_drop')
            if (request.form.get('sensor_type') == 'temperature') and id_for_drop:
                TemperatureSensor(sensor_id=uuid.UUID(id_for_drop)).delete()
                return redirect(url_for('admin'))
            elif (request.form.get('sensor_type') == 'pressure') and id_for_drop:
                PressureSensor(sensor_id=uuid.UUID(id_for_drop)).delete()
                return redirect(url_for('admin'))
        login = request.form.get('login')
        if (user_form == 'add') and login:
            user = Users.objects(Users.login == login).allow_filtering().first()
            if user:
                flash('Пользователь с таким логином уже существует, введите другой логин')
            else:
                password = secrets.token_hex(4)
                Users.create(id=uuid.uuid4(), login=login, password=generate_password_hash(password))
                flash('Добавлен пользователь ' + login + ' пароль: ' + str(password))
                return redirect(url_for('admin'))
        elif (user_form == 'drop') and login:
            user = Users.objects(Users.login == login).allow_filtering().first()
            if user:
                Users(id=user.id).delete()
                return redirect(url_for('admin'))
            else:
                flash('Пользователя с таким логином не существует')
    return render_template("admin_page.html", users=users, temperature_sensors=temperature_sensors
                           , pressure_sensors=pressure_sensors)


@app.route('/staff', methods=['GET', 'POST'])
@login_required
def staff():
    if request.method == 'GET':
        return render_template("staff_page.html")
    if request.method == 'POST':
        load_xlsx_type = request.form.get('load_xlsx')

        if load_xlsx_type == 'temperature':
            xlsx_data = load_xlsx(request.form.get('temp_datetime_from'), request.form.get('temp_datetime_to')
                                  , TemperatureSensor)
            if xlsx_data[2]:
                return excel.make_response_from_array(xlsx_data[2], "xlsx", file_name="Показания датчика температуры с "
                                                                              + str(xlsx_data[0])
                                                                              + ' по ' + str(xlsx_data[1]))
            else:
                flash(u"Данные за указанный период не были найдены", "temperature")
        elif load_xlsx_type == 'pressure':
            xlsx_data = load_xlsx(request.form.get('press_datetime_from'), request.form.get('press_datetime_to')
                                  , PressureSensor)
            if xlsx_data[2]:
                return excel.make_response_from_array(xlsx_data[2], "xlsx", file_name="Показания датчика температуры с "
                                                                                  + str(xlsx_data[0])
                                                                                  + ' по ' + str(xlsx_data[1]))
            else:
                flash(u"Данные за указанный период не были найдены", "pressure")
    return render_template("staff_page.html")


@app.route('/temperature-chart-data')
def temperature_chart_data():
    return Response(chart_value_generator(TemperatureSensor), mimetype='text/event-stream')


@app.route('/pressure-chart-data')
def pressure_chart_data():
    return Response(chart_value_generator(PressureSensor), mimetype='text/event-stream')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth'))
