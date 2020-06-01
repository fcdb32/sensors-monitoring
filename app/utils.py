# Дополнительные функции веб-приложения (авторизация, выгрузка файла в формате XLSX, отправка данных для графиков)
# Разработал студент группы А-07-16 Бахтин Евгений
# Версия 1.0
import json
import time
import uuid
from datetime import datetime
from flask_login import login_user
from werkzeug.security import check_password_hash

from app.models import Users, connect_cassandra


def authorize(login, password):
    connect_cassandra('admin')
    user = Users.objects(Users.login == login).allow_filtering().first()
    if user:
        if check_password_hash(user.password, password):
            login_user(user)
            return True
    else:
        return False


def load_xlsx(datetime_from, datetime_to, sensor):
    response = []
    if datetime_from and datetime_to:
        datetime_from = datetime.strptime(datetime_from, '%Y-%m-%dT%H:%M')
        datetime_to = datetime.strptime(datetime_to, '%Y-%m-%dT%H:%M')
        sensor_data = sensor.objects(sensor_id=uuid.UUID('7994c456-92d5-11ea-bb37-0242ac130002'))
        sensor_data = list(sensor_data.filter(measure_timestamp__gte=datetime_from
                                                                  , measure_timestamp__lte=datetime_to))
        for row in sensor_data:
            response.append([str(row.measure_timestamp), row.value])
    return [datetime_from, datetime_to, response]


def chart_value_generator(sensor):
    while True:
        sensor_plot_data = sensor.objects(
            sensor_id=uuid.UUID('7994c456-92d5-11ea-bb37-0242ac130002')).order_by('-measure_timestamp').values_list(
            'measure_timestamp', 'value')
        json_data = json.dumps(
            {'time': sensor_plot_data[0][0].strftime('%H:%M:%S'), 'value': sensor_plot_data[0][1]})
        yield f"data:{json_data}\n\n"
        time.sleep(1)
