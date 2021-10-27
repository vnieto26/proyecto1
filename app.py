from flask import Flask, render_template, request, session, url_for, flash, current_app
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

#Modelos Bases de datos
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    perfil = db.Column(db.String(1), default='1')
    comentario = db.relationship("Comentarios", backref="users")
    compra = db.relationship('Compras', backref='users')
    deseo = db.relationship('ListaDeseos', backref='users')

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, default = 0.0)
    stock = db.Column(db.Integer, default=0)
    comentario = db.relationship('Comentarios', backref='products')
    compra = db.relationship('Compras', backref='products')
    deseo = db.relationship('ListaDeseos', backref='products')

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


class ListaDeseos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)


# Rutas
@ app.route('/')
def inicio():
    productos = Products.query.all()
    return render_template('index.html', productos=productos)


@ app.route('/signup',  methods=["GET", "POST"])
def signup():
    try:
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
            return redirect('/home')
    except Exception as e:
        print(e)
    return render_template('index.html')

@ app.route('/login',  methods=['GET', 'POST'])
def login():
    try:
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
    except Exception as e:
        print(e)
    return redirect(url_for('inicio'))


@ app.route('/home')
def home():
    if 'username' in session:
        productos = Products.query.all()
        users = Users.query.all()
        comentarios = Comentarios.query.all()
        ldeseos = ListaDeseos.query.all()
        return render_template('home.html', productos=productos, users=users, comentarios= comentarios, ldeseos=ldeseos)
    return redirect(url_for('inicio'))


@ app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('Carritocompra', None)
    return redirect(url_for('inicio'))

@app.route('/crear_producto',  methods=["GET", "POST"])
def crear_producto():
    try:
        if request.method == 'POST':
            producto=request.form['producto']
            categoria=request.form['categoria']
            precio=request.form['precio']
            stock=request.form['stock']
            new_producto=Products(producto=producto, categoria=categoria, precio=precio, stock=stock)
            db.session.add(new_producto)
            db.session.commit()
            return redirect(url_for('home'))
    except Exception as e:
        print(e)
    return redirect(url_for('home'))

@app.route('/home/edit_product', methods=["GET", "POST"])
def edit_product():
    try:
        if request.method == 'POST':
            idp = request.form['editprodid']
            prod=request.form['editproducto']
            cat=request.form['editcat']
            pre=request.form['editprecio']
            stock=request.form['editstock']
            Products.query.filter_by(id=idp).update(dict(producto=prod, categoria=cat, precio=pre, stock=stock))
            db.session.commit()
            return redirect(url_for('home'))
    except Exception as e:
        print(e)
    return redirect(url_for('home'))

@app.route('/home/delete_product/<int:id>', methods=["get","post"])
def delete_product(id):
    try:
        producto = Products.query.get(id)
        db.session.delete(producto)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        print(e)
    return redirect(url_for('home'))
    

@app.route('/home/edit_user', methods=["GET", "POST"])
def edit_user():
    try:
        if request.method == 'POST':
            idu = request.form['id']
            new_nombre=request.form['nombre']
            new_telefono=request.form['telefono']
            new_password=generate_password_hash(request.form['password'], method='sha256')
            new_email=request.form['email']
            new_perfil=request.form['perfil']
            Users.query.filter_by(id=idu).update(dict(nombre=new_nombre, telefono=new_telefono,
                        email=new_email, password=new_password, perfil=new_perfil))
            db.session.commit()
    except Exception as e:
        print(e)
    return redirect(url_for('home'))

@app.route('/home/delete_user/<int:id>', methods=["get","post"])
def delete_user(id):
    try:
        user = Users.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        print(e)
    return redirect(url_for('home'))

@app.route('/home/delete_comenta/<int:id>', methods=["get","post"])
def delete_comenta(id):
    try:
        comentario = Comentarios.query.get(id)
        db.session.delete(comentario)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        print(e)
    return redirect(url_for('home'))

@app.route('/compra')
def compra():
    try:
        if 'usercompra' in session:
            userid = session['userid']
            productos = Products.query.all()
            comentarios = Comentarios.query.filter_by(id_user=userid).all()
            ldeseos = ListaDeseos.query.filter_by(id_user=userid).all()
    except Exception as e:
        print(e)
    return render_template('compra.html', productos=productos, comentarios=comentarios, ldeseos= ldeseos)

@app.route('/compra/comentar', methods=["get","post"])
def comentar():
    try:
        if request.method == 'POST':
            new_comentario=request.form['comentario']
            new_idproducto=request.form['idproducto']
            new_idusuario=request.form['idusuario']
            new_comentario=Comentarios(comentario=new_comentario, id_user=new_idusuario, id_producto=new_idproducto)
            db.session.add(new_comentario)
            db.session.commit()
            return redirect(url_for('compra'))
    except Exception as e:
        print(e)
    return redirect(url_for('compra'))


@app.route('/compra/edit_comentar', methods=['get','post'])
def edit_comentar():
    try:
        if request.method == 'POST':
            idc = request.form['id']
            com = request.form['comentario']
            Comentarios.query.filter_by(id=idc).update(dict(comentario=com))
            db.session.commit()
            return redirect(url_for('compra'))
    except Exception as e:
        print(e)
    return redirect(url_for('compra'))
    

@app.route('/compra/del_comenta/<int:id>', methods=["get","post"])
def del_comenta(id):
    try:
        comentario = Comentarios.query.get(id)
        db.session.delete(comentario)
        db.session.commit()
        return redirect(url_for('compra'))
    except Exception as e:
        print(e)
    return redirect(url_for('compra'))

# Carrito de Compra
def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


@app.route('/compra/addcar', methods=["post"])
def addcar():
    try:
        idp = request.form['idp']
        prod = request.form['prod']
        cantidad = request.form['cantidad']
        formap = request.form['formap']
        idu = request.form['idu']
        product = Products.query.filter_by(id=idp).first()
        if idp and prod and cantidad and formap and idu and request.method == "POST":
            DictItems = {idp:{'nombre':product.producto, 'precio': product.precio, 
            'cantidad': cantidad, 'formap': formap, 'id_user': idu}}
            if 'Carritocompra' in session:
                print(session['Carritocompra'])
                if idp in session['Carritocompra']:
                    for key, item in session['Carritocompra'].items():
                        if int(key) == int(idp):
                            session.modified = True
                            item['cantidad'] += 1
                else:
                    session['Carritocompra'] = MagerDicts(session['Carritocompra'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Carritocompra'] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    return redirect(request.referrer)
    
@app.route('/compra/carts')
def getCart():
    try:
        if 'Carritocompra' not in session or len(session['Carritocompra'])<= 0:
            return redirect(url_for('compra'))
        grantotal = sum(
            float(prod['precio']) * int(prod['cantidad'])
            for key, prod in session['Carritocompra'].items()
        )
        print(grantotal)
        return redirect(url_for('compra', grantotal=grantotal))
    except Exception as e:
        print(e)

@app.route('/compra/deleteitem/<int:id>')
def deleteitem(id):
    if 'Carritocompra' not in session:
        return redirect(url_for('compra'))
    try:
        session.modified= True
        for key, item in session['Carritocompra'].items():
            if int(key)== id:
                session['Carritocompra'].pop(key, None)
                return redirect(url_for('compra'))
    except Exception as e:
        print(e)
    return redirect(url_for('compra'))

@app.route('/compra/clearcart')
def clearcart():
    try:
        session.pop('Carritocompra', None)
        return redirect(url_for('compra'))
    except Exception as e:
        print(e)


@app.route('/compra/addldeseo', methods=["get","post"])
def addldeseo():
    try:
        if request.method == 'POST':
            new_idproducto=request.form['idproducto']
            new_idusuario=request.form['idusuario']
            new_ldeseo = ListaDeseos(id_user=new_idusuario, id_producto=new_idproducto)
            db.session.add(new_ldeseo)
            db.session.commit()
            return redirect(url_for('compra'))
    except Exception as e:
        print(e)
    return redirect(url_for('compra'))


@app.route('/compra/del_ldeseo/<int:id>', methods=["get","post"])
def del_ldeseo(id):
    try:
        ldeseo = ListaDeseos.query.get(id)
        db.session.delete(ldeseo)
        db.session.commit()
        return redirect(url_for('compra'))
    except Exception as e:
        print(e)
    return redirect(url_for('compra'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)