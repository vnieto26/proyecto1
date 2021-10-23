from flask import Flask, render_template, request, session, escape, url_for
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
    comentario = db.relationship("Comentarios", backref="users")
    compra = db.relationship('Compras', backref='users')

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, default = 0.0)
    stock = db.Column(db.Integer, default=0)
    comentario = db.relationship('Comentarios', backref='products')
    compra = db.relationship('Compras', backref='products')

class Comentarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.String(300), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

class Compras(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idProducto = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    formapago = db.Column(db.String(50), nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


@ app.route('/')
def inicio():
    productos = Products.query.all()
    return render_template('index.html', productos=productos)

@ app.route('/buscar')
def buscar():
    busca=request.args.get('search')
    product=Products.query.filter_by(producto=busca).first()
    if product:
        return product.producto
    return redirect(url_for('inicio'))


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
    if request.method != 'POST':
        return redirect(url_for('inicio'))
    user=Users.query.filter_by(email=request.form['email']).first()
    if user and check_password_hash(user.password, request.form['password']):
        if user.perfil == '2':
            session['username']=user.nombre
            return redirect(url_for('home'))
        session['usercompra'] = user.nombre
        session['userid'] = user.id
        return redirect(url_for('compra'))
    return redirect(url_for('inicio'))


@ app.route('/home')
def home():
    if 'username' in session:
        productos = Products.query.all()
        users = Users.query.all()
        comentarios = Comentarios.query.all()
        return render_template('home.html', productos=productos, users=users, comentarios= comentarios)
    return redirect(url_for('inicio'))


@ app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('inicio'))

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
        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/home/edit_product/<int:id>', methods=["GET", "POST"])
def edit_product(id):
    
    return redirect(url_for('home'))

@app.route('/home/delete_product/<int:id>', methods=["get","post"])
def delete_product(id):
    producto = Products.query.get(id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/home/edit_user')
def edit_user():
    return redirect(url_for('home'))

@app.route('/home/delete_user/<int:id>', methods=["get","post"])
def delete_user(id):
    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/home/edit_comenta')
def edit_comenta():
    return redirect(url_for('home'))

@app.route('/home/delete_comenta/<int:id>', methods=["get","post"])
def delete_comenta(id):
    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/compra')
def compra():
    if 'usercompra' in session:
        userid = session['userid']
        print('usercompra')
        productos = Products.query.all()
        comentarios = Comentarios.query.filter_by(id_user=userid).all()
        return render_template('compra.html', productos=productos, comentarios=comentarios)

@app.route('/compra/comentar', methods=["get","post"])
def comentar():
    if request.method == 'POST':
        new_comentario=request.form['comentario']
        new_idproducto=request.form['idproducto']
        new_idusuario=request.form['idusuario']
        new_comentario=Comentarios(comentario=new_comentario, id_user=new_idusuario, id_producto=new_idproducto)
        db.session.add(new_comentario)
        db.session.commit()
        return redirect(url_for('compra'))


@app.route('/compra/edit_comentar/<int:id>', methods=['get','post'])
def edit_comentar(id):
    return redirect(url_for('compra'))

@app.route('/compra/del_comenta/<int:id>', methods=["get","post"])
def del_comenta(id):
    comentario = Comentarios.query.get(id)
    db.session.delete(comentario)
    db.session.commit()
    return redirect(url_for('compra'))


@app.route('/compra/carrito')
def carrito():
    return redirect(url_for('compra'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
