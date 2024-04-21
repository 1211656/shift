import sqlite3
from datetime import datetime, timedelta

import flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

import os

from flask_sqlalchemy.query import Query
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.testing.plugin.plugin_base import warnings

from src.domain.auth.Email import Email
from src.domain.auth.Password import Password

app = Flask(__name__) # Na app encontra-se o nosso servidor web de Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/dados.db'
db = SQLAlchemy(app)





class Client(db.Model):
    __tablename__ = "Client"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(Email, unique=True, nullable=False)
    password = db.Column(Password, unique=True, nullable=False)







# Main
if __name__ == '__main__':
    db.create_all()
    # criar_tabelas()
    app.run()


