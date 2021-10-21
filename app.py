from flask import Flask, render_template, request, session, escape
from werkzeug.utils import redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

dbdir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.secret_key = "1a2b3c4d5e6f7g8h9i"


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    perfil = db.Column(db.String(1), default='1')


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, default = 0.0)
    stock = db.Column(db.Integer, default=0)

@ app.route('/')
def inicio():
    return render_template('index.html')

@ app.route('/buscar')
def buscar():
    busca=request.args.get('search')
    user=Users.query.filter_by(email=busca).first()
    if user:
        return user.email
    return 'El usuario no existe'


@ app.route('/signup',  methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        new_nombre=request.form['nombre']
        new_telefono=request.form['telefono']
        new_password=generate_password_hash(
            request.form['password'], method='sha256')
        new_email=request.form['email']
        new_perfil=1
        new_user=Users(nombre=new_nombre, telefono=new_telefono,
                       email=new_email, password=new_password, perfil=new_perfil)
        db.session.add(new_user)
        db.session.commit()
        # db.create_all()

        return redirect('/home')
    return render_template('index.html')

@ app.route('/login',  methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user=Users.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['username']=user.nombre
            return redirect('/home')
        return redirect('/')

    return render_template('index.html')

@ app.route('/home')
def home():
    if 'username' in session:
        productos = Products.query.all()
        users = Users.query.all()
        return render_template('home.html', productos=productos, users=users)
    return redirect('/')

@ app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/crear_producto',  methods=["GET", "POST"])
def crear_producto():
    if request.method == 'POST':
        producto=request.form['producto']
        categoria=request.form['categoria']
        precio=request.form['precio']
        stock=request.form['stock']
        new_producto=Products(producto=producto, categoria=categoria, precio=precio, stock=stock)
        db.session.add(new_producto)
        db.session.commit()
        return redirect('/home')
    return redirect('/home')

@app.route('/home/edit_product')
def edit_product():
    return redirect('/home')

@app.route('/home/delete_product/<int:id>', methods=["get","post"])
def delete_product(id):
    producto = Products.query.get(id)
    db.session.delete(producto)
    db.session.commit()
    return redirect('/home')

@app.route('/home/edit_user')
def edit_user():
    return redirect('/home')

@app.route('/home/delete_user/<int:id>', methods=["get","post"])
def delete_user(id):
    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/home')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
