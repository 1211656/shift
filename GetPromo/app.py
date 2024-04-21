import string
from random import random, choices
from sqlite3 import Date

import flask


from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
from flask_sqlalchemy.query import Query
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.testing.plugin.plugin_base import warnings
from jinja2 import Environment

app = Flask(__name__)
app.config["DEBUG"] = True
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'dados.db')
db = SQLAlchemy(app)
env = Environment()
env.globals.update(enumerate=enumerate)




class Email(db.TypeDecorator):
    impl = db.String(120)

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return value


class Password(db.TypeDecorator):
    impl = db.String(80)

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return value
class Client(db.Model):
    __tablename__ = "Client"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(Email, unique=True, nullable=False)
    password = db.Column(Password, unique=True, nullable=False)
    advertises = relationship('Advertise', back_populates='client')

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(90), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)  # Assuming Email is a String type
    password = db.Column(db.String, nullable=False)  # Assuming Password is a String type
    respostas = relationship('Resposta', back_populates='user')
    advertises = relationship('Advertise', secondary='user_advertise', back_populates='users')
    prizes = db.Column(db.String, nullable=True)


user_advertise = db.Table('user_advertise',
    db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True),
    db.Column('advertise_id', db.Integer, db.ForeignKey('Advertise.id'), primary_key=True)
)


class Advertise(db.Model):
    __tablename__ = "Advertise"
    id = db.Column(db.Integer, primary_key=True)
    url_main = db.Column(db.String(200), unique=True, nullable=False)
    url_secondary = db.Column(db.String(200), unique=False, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    expirationDate = db.Column(DateTime, nullable=False)  # Import Date from sqlalchemy
    code = db.Column(db.String(100), unique=True, nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('Client.id'))
    client = relationship('Client', back_populates='advertises')
    questionarios = relationship('Questionario', back_populates='advertises')
    users = relationship('User', secondary='user_advertise', back_populates='advertises')




class Questionario(db.Model):
    __tablename__ = "Questionario"
    id = db.Column(db.Integer, primary_key=True)
    advertise_id = db.Column(db.Integer, db.ForeignKey('Advertise.id'))
    advertises = relationship('Advertise', back_populates='questionarios')
    questoes = relationship('Questao', back_populates='questionario')

class Questao(db.Model):
    __tablename__ = "Questao"
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255))
    questionario_id = db.Column(db.Integer, db.ForeignKey('Questionario.id'))
    questionario = relationship('Questionario', back_populates='questoes')
    respostas = relationship('Resposta', back_populates='questao')
class Resposta(db.Model):
    __tablename__ = "Resposta"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    resposta = db.Column(db.Integer)
    questao_id = db.Column(db.Integer, db.ForeignKey('Questao.id'), nullable=True)
    questao = relationship('Questao',back_populates='respostas')
    user_id = db.Column(db.Integer, ForeignKey('User.id'), nullable = True)

    user = relationship('User', back_populates='respostas')



images_path = ['1.jpg']
def custom_enumerate(iterable):
    return zip(range(len(iterable)), iterable)
@app.route('/',methods =['GET'])
def home():
    return render_template("login_page.html", images_path=images_path)
@app.route('/questionario/<int:advertise_id>/<username>', methods=['GET'])
def questionario(advertise_id, username):

    questionario = Questionario.query.filter_by(advertise_id=advertise_id).first()

    if questionario:
        questoes = [{'texto': questao.texto} for questao in questionario.questoes]
        return render_template('questionario.html', questionario=questionario, questoes=questoes, username=username, cont=0, enumerate=custom_enumerate)
    else:
        return "Questionário não encontrado"

@app.route('/submit_question/<questionario_id>/<username>/<cont>/', methods=['GET'])
def submit_question(questionario_id, username,cont):
    questionario = Questionario.query.get(questionario_id)
    print(cont)
    if int(cont) == len(questionario.questoes) :
        cont = 0
    if int(cont) < 0:
        cont = len(questionario.questoes) -1


    if questionario:
        questoes = [{'texto': questao.texto} for questao in questionario.questoes]
        return render_template('questionario.html', questionario=questionario,questoes=questoes, username=username, cont= int(cont), enumerate=custom_enumerate)
    else:
        return "Questionário não encontrado"

@app.route('/submit_answer/<questionario_id>/<username>/<cont>/', methods=['GET'])
def submit_answer(questionario_id, username,cont):
    questionario = Questionario.query.get(questionario_id)
    opcao = request.args.get('opcao')

    if int(cont) == len(questionario.questoes):
        cont = 0
    if int(cont) < 0:
        cont = len(questionario.questoes) - 1

    questao = questionario.questoes[int(cont)]

    inserir_resposta(questao.id,opcao,username)

    if check_if_user_responded_to_all_questions(questionario_id,username):
        # prize
        advertise = Advertise.query.filter_by(id=questionario.advertise_id).first()
        user = User.query.filter_by(username=username).first()
        user.advertises.remove(advertise)
        if user.prizes!=None:
            user.prizes += generate_prize(advertise)
        else:
            user.prizes = generate_prize(advertise)
        print(user.prizes)
        db.session.commit()

        return redirect(url_for('home_page',username=username))

    if questionario:
        questoes = [{'texto': questao.texto} for questao in questionario.questoes]
        return redirect(url_for('submit_question', questionario_id=questionario_id, username=username, cont= int(cont)+1))
    else:
        return "Questionário não encontrado"

def generate_prize(advertise):
    return f"{concatenate_string(advertise)}|"
def generate_random_code():
    return ''.join(choices(string.ascii_letters, k=9))


def concatenate_string(advertise):
    random_code = generate_random_code()
    return f"{advertise.title}//{advertise.description}//CODE: {random_code}"

@app.route('/register_page')
def register_page():
    return render_template('register_page.html')
@app.route('/profile_page/<username>',methods = ['GET'])
def profile_page(username):

    user = User.query.filter_by(username=username).first()
    return render_template('profile_page.html',user=user)
@app.route('/home_page/<username>',methods=['GET'])
def home_page(username):
    user = User.query.filter_by(username=username).first()
    lista_advertises = user.advertises
    prizes = count_prizes(username)

    if prizes==0:
        return render_template('home_page.html',username=username,lista_advertises=lista_advertises,prizes=prizes)

    else:
        arr = user.prizes.split('|')
        return render_template('home_page.html', username=username, lista_advertises=lista_advertises, prizes=prizes, arr=arr )


@app.route('/home_page_category/<username>/',methods=['GET'])
def home_page_category(username):
    category = request.args.get('option')
    user = User.query.filter_by(username=username).first()
    lista_advertises = filter_advertises_by_category(user.advertises,category)
    prizes = count_prizes(username)

    if prizes==0:
        return render_template('home_page.html',username=username,lista_advertises=lista_advertises,prizes=prizes)

    else:
        arr = user.prizes.split('|')
        return render_template('home_page.html', username=username, lista_advertises=lista_advertises, prizes=prizes, arr=arr )


@app.route('/home_page_filtered/<username>/<lista>',methods=['GET'])
def home_page_filtered(username,lista):

    user = User.query.filter_by(username=username).first()

    prizes = count_prizes(username)

    if prizes==0:
        return render_template('home_page.html',username=username,lista_advertises=lista,prizes=prizes)

    else:
        arr = user.prizes.split('|')
        return render_template('home_page.html', username=username, lista_advertises=lista, prizes=prizes, arr=arr )

def filter_advertises_by_category(advertises, category):
    new_advertises = []
    if category==None:
        return advertises

    for advertise in advertises:
        if advertise.category.lower() == category.lower():
            new_advertises.append(advertise)
    return new_advertises

@app.route('/search/<username>', methods=['GET'])
def search(username):
    result = request.args.get('query')
    clients = Client.query.all()
    advertises = Advertise.query.all()
    advertises_new = []
    clients_new = []

    if result:
        if len(result) > 3:
            result = result[:3]  # Ajuste para os primeiros 3 caracteres

        for client in clients:
            result_client = client.email[:3]
            if result_client == result:
                clients_new.append(client)
    else:
        # Caso não haja resultado, redirecione de volta à página inicial ou mostre uma mensagem de erro
        return redirect(url_for('home_page', username=username))

    for client in clients_new:
        for advertise in advertises:
            if client.id == advertise.client_id:
                advertises_new.append(advertise)

    return redirect(url_for('home_page_filtered', username=username, lista=advertises_new))



def count_prizes(username):
    user = User.query.filter_by(username=username).first()
    if user.prizes==None:
        return 0
    else:
        arr = user.prizes.split('|')
        return len(arr) -1

@app.route('/redirecionar_register_page',methods=['POST'])
def redirecionar_register_page():
    return redirect(url_for('register_page'))
@app.route('/redirecionar_login_page',methods=['POST'])
def redirecionar_login_page():
    return redirect(url_for('home'))
@app.route('/redirecionar_home_page_from_register',methods=['GET'])
def redirecionar_home_page_from_register():
    username = request.args.get('username')
    email = request.args.get('email')
    password1 = request.args.get('password1')
    password2 = request.args.get('password2')
    if register_verification(username,email,password1,password2) and user_insert(username,email,password1):
        return redirect(url_for('home_page', username=username))
    else:

        return redirect(url_for('redirecionar_register_page'))
@app.route('/redirecionar_home_page',methods=['GET'])
def redirecionar_home_page():
    email1 = request.args.get('email')
    password = request.args.get('password')
    if login_verification(email1,password):
        user_with_email = User.query.filter_by(email=email1).first()

        return redirect(url_for('home_page',username=user_with_email.username))
    else:

        return redirect(url_for('home'))
@app.route('/redirecionar_profile_page/<username>',methods=['GET'])
def redirecionar_profile_page(username):
    print(username)
    return redirect(url_for('profile_page',username=username))
@app.route('/redirecionar_questionario/<ad_id>/<username>', methods=['GET'])
def redirecionar_questionario(ad_id, username):
    questionario = Questionario.query.filter_by(advertise_id=ad_id).first()
    if questionario:
        return redirect(url_for('questionario', questionario_id=questionario.id, username=username))
    else:

        return "Questionário não encontrado"

def register_verification(username,email,password1,password2):

    if username==None:
        return False
    if email==None:
        return False
    if password1==None:
        return False
    if password2==None:
        return False

    user_with_username = User.query.filter_by(username=username).first()

    if user_with_username:
        return False
    user_with_email = User.query.filter_by(email=email).first()
    if user_with_email:
        return False
    if password1!=password2:
        return False

    return True
def login_verification(email,password):

    user_with_email = User.query.filter_by(email=email).first()
    if user_with_email.password==password:
        return True
    else:
        return False
def user_insert(username,email,password):
    try:
        # Cria um novo usuário
        new_user = User(email=email, password=password, username=username)


        # Obtém todos os anúncios existentes
        advertises = Advertise.query.all()



        # Associa os anúncios ao novo usuário
        for ad in advertises:
            new_user.advertises.append(ad)

        db.session.add(new_user)
        db.session.commit()

        return True
    except Exception as e:
        db.session.rollback()
        print("Erro ao inserir usuário:", str(e))
        return False

@app.route('/altera_valores/<user_id>', methods=['POST'])
def altera_valores(user_id):
    user = User.query.filter_by(id=user_id).first()

    if request.method == 'POST':
        username = request.form['username']
        print(username)
        password = request.form['password']
        email = request.form['email']

        if user:
            user.username = username
            user.email = email
            user.password = password
            db.session.commit()
            return redirect(url_for('profile_page',username=username))

    return redirect(url_for('profile_page',username=user.username))
@app.route('/apagar_conta/<user_id>', methods=['POST'])
def apagar_conta(user_id):
    user = User.query.filter_by(id=user_id).first()
    respostas = Resposta.query.all()
    for resposta in respostas:
        if resposta.user_id==user.id:
            db.session.delete(resposta)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('home'))

def inserir_resposta(questao_id, valor, username):
    user = User.query.filter_by(username=username).first()

    questao = Questao.query.get(questao_id)
    if questao:
        resposta = questao.respostas
        if resposta:
            for r in resposta:
                if r.user_id == user.id:

                    r.resposta = valor
                    db.session.commit()
                    return True

    nova_resposta = Resposta(resposta=valor, user_id=user.id, questao_id=questao_id)

    db.session.add(nova_resposta)
    db.session.commit()
    return True


def check_if_user_responded_to_all_questions(questionario_id,username):
    questionario = Questionario.query.filter_by(id=questionario_id).first()

    user = User.query.filter_by(username=username).first()
    cont = 0
    contQuestoes = 0
    for questao in questionario.questoes:
        contQuestoes +=1
        for resposta in questao.respostas:
            if resposta.user_id==user.id:
                cont +=1

    if contQuestoes == cont:
        return True
    else:
        return False




def criar_tabelas():
    with app.app_context():
        db.create_all()
        db.session.commit()





if __name__ == '__main__':

    criar_tabelas()

    app.run(debug=True)

