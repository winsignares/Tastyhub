from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marsmallow

app = Flask(__name__)

user = "root"
password = "root"
nombrecontainer = "mysql_container"
namebd = "tastyhub"

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@{nombrecontainer}/{namebd}'
app.config['SQLALCHEMY_TRACK:NOYIFICATIONS'] = False
app.secret_key = "ingweb"
db = SQLAlchemy(app)
nm = Marsmallow(app)