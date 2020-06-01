# Классы веб-приложения для работы с базой данных
# Разработал студент группы А-07-16 Бахтин Евгений
# Версия 1.0
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import columns, connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
from flask_login import UserMixin

from app import login_manager


@login_manager.user_loader
def load_user(user_id):
    connect_cassandra('admin')
    return Users.objects(Users.id == user_id).get()


class Users(Model, UserMixin):
    id = columns.UUID(primary_key=True)
    login = columns.Text(primary_key=True)
    password = columns.Text()


class TemperatureSensor(Model):
    sensor_id = columns.UUID(primary_key=True)
    measure_timestamp = columns.DateTime(primary_key=True)
    value = columns.Double()


class PressureSensor(Model):
    sensor_id = columns.UUID(primary_key=True)
    measure_timestamp = columns.DateTime(primary_key=True)
    value = columns.Double()


def connect_cassandra(role):
    auth_provider = PlainTextAuthProvider(username=str(role), password=str(role))
    connection.setup(['127.0.0.1'], "sensors", auth_provider=auth_provider, protocol_version=3)
    sync_table(Users)
    sync_table(TemperatureSensor)
    sync_table(PressureSensor)
    return True

