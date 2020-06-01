# Инициализация веб-приложения
# Разработал студент группы А-07-16 Бахтин Евгений
# Версия 1.0
import flask_excel as excel
from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'secretkey'
login_manager = LoginManager(app)
login_manager.login_view = 'auth'
excel.init_excel(app)

from app import models, views, utils
