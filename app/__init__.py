import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.openid import OpenID
from config import basedir


#start app
app = Flask(__name__)

#load config
app.config.from_object('config')

#open db conection
db = SQLAlchemy(app)

#start Open ID handler
oid = OpenID(app, os.path.join(basedir, 'tmp'))

#import Views and Models
from app import views, models, forms