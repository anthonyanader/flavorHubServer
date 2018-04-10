import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
POSTGRES = {
    'user': 'filipslatinac',
    'pw': 'password',
    'db': 'flavorhub',
    'url':'127.0.0.1:5432'
}
app.config['SECRET_KEY'] = 'changeThisPlease'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES['user'],pw=POSTGRES['pw'],url=POSTGRES['url'],db=POSTGRES['db'])
db = SQLAlchemy(app)
