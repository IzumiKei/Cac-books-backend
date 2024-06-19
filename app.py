from flask import Flask ,jsonify ,request
# del modulo flask importar la clase Flask y los métodos jsonify,request
from flask_cors import CORS       # del modulo flask_cors importar CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json

app=Flask(__name__)  # crear el objeto app de la clase Flask
CORS(app) #modulo cors es para que me permita acceder desde el frontend al backend


# configuro la base de datos, con el nombre el usuario y la clave
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost/cacbooks'
# URI de la BBDD                          driver de la BD  user:clave@URLBBDD/nombreBBDD
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False #none
db= SQLAlchemy(app)   #crea el objeto db de la clase SQLAlquemy
ma=Marshmallow(app)   #crea el objeto ma de de la clase Marshmallow



class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(50))
    email = db.Column(db.String(200))
    name = db.Column(db.String(50))
    lastName = db.Column(db.String(50))
    age = db.Column(db.Integer)
    
    def __init__(self, userName, email, name, lastName, age):
        self.userName = userName
        self.email = email
        self.name = name
        self.lastName = lastName
        self.age = age


class Log(db.Model):
    email = db.Column(db.String(200), primary_key=True)
    userId = db.Column(db.Integer)
    userName = db.Column(db.String(50))
    password = db.Column(db.String(20))

    def __init__(self, email, userName, userId, password):
        self.userId = userId
        self.userName = userName
        self.email = email
        self.password = password


class Favorites(db.Model):
    favId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer)
    name = db.Column(db.String(20))
    books = db.Column(db.String(500))

    def __init__(self, userId, name, books):
        self.userId = userId
        self.name = name
        self.books = books
        
class Profile(db.Model):
    profileId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer)
    favId = db.Column(db.Integer)
    cart = db.Column(db.String(500))

    def __init__(self, userId, favId, cart):
        self.userId = userId
        self.favId = favId
        self.cart = cart



    #  si hay que crear mas tablas , se hace aqui



with app.app_context():
    db.create_all()  # aqui crea todas las tablas si es que no estan creadas

#  ************************************************************


class UserSchema(ma.Schema):
    class Meta:
        fields = ("userId", "userName", "email", "name", "lastName", "age")

class LogSchema(ma.Schema):
    class Meta:
        fields = ("email", "userName", "userId", "password")

class FavoriteSchema(ma.Schema):
    class Meta:
        fields = ("favId", "userId", "name", "books")

class ProfileSchema(ma.Schema):
    class Meta:
        fields = ("profileId", "userId", "favId", "cart")



user_schema = UserSchema()
users_schema = UserSchema(many=True)

login_schema = LogSchema()
logins_schema = LogSchema(many = True)

favorite_schema = FavoriteSchema()
favorites_schema = FavoriteSchema(many = True)

profile_schema = ProfileSchema()
profiles_schema = ProfileSchema(many = True)





# ------------------ Creacion de los endpoint (json) ------------------

#@app.route('/productos',methods=['GET'])
#def get_Productos():
#    all_productos=Producto.query.all() # el metodo query.all() lo hereda de db.Model
#    result=productos_schema.dump(all_productos)  #el metodo dump() lo hereda de ma.schema y
#                                                 # trae todos los registros de la tabla
#    return jsonify(result)     # retorna un JSON de todos los registros de la tabla



@app.route("/user/<id>", methods=['GET'])
def get_user(id):
    """Devuelve la información de un usuario dado un cierto Id."""

    user = User.query.get(id)

    return user_schema.jsonify(user)


@app.route("/user/<id>", methods=["DELETE"])
def delete_user(id):
    """Borra toda la información de un usuario. Incluido login, favoritos y perfil."""

    minus_id = str(int(id) - 1)

    user = User.query.get(id)
    login = Log.query.get(user.email)
    profile = Profile.query.get(id)
    favs = Favorites.query.get(id)

    db.session.delete(login)
    db.session.delete(favs)
    db.session.delete(profile)
    db.session.delete(user)
    
    db.session.commit()

    return user_schema.jsonify(user)


@app.route("/user", methods=["POST"])
def create_user():
    """ Recibe toda la información del registro, y crea la información del usuario en
        la base de datos. Incluida su información de login, sus favoritos y su perfil. """
    
    data = request.json

    userName = data["userName"]
    email = data["email"]
    password = data["password"]
    name = data["name"]
    lastName = data["lastName"]
    age = data["age"]

    user = User(userName, email, name, lastName, age)
    db.session.add(user)
    db.session.commit()
    print(user.userId)
    print(user.userName)
    favs = Favorites(user.userId, "Favorites", "")
    db.session.add(favs)
    db.session.commit()
    login = Log(email, userName, user.userId, password)
    profile = Profile(user.userId, favs.favId, "")
    
    db.session.add(login)
    db.session.add(profile)
    db.session.commit()
    
    return user_schema.jsonify(user)



@app.route("/user/<id>", methods=["PUT"])
def update_user(id):
    """Modifica la información de un usuario con nueva información."""
    data = request.json
    user = User.query.get(id)

    user.userName = data.userName
    user.email = data.email
    user.password = data.password
    user.name = data.name
    user.lastName = data.lastName
    user.age = data.age

    db.session.commit()

    return user_schema.jsonify(user)


 # ---- Login ----

@app.route("/user/login/email", methods=["GET"])
def authentication(email):
    data = request.json
    responseData = {
        "mailFound": False,
        "passwordCorrect": False,
        "userId": -1
    }

    login = Log.query.get(email)

    if login:
        # Existe el mail
        responseData["mailFound"] = True
        print("Mail exists")

        if login.password == data.password:
            # La contraseña es correcta
            responseData["passwordCorrect"] = True
            responseData["userId"] = login.userId # Devuelve el Id del usuario
        
    else:
        print("Mail doesn't exist")
    
    return jsonify(responseData)

# ---- Favoritos ----
@app.route("/user/favs/<id>", methods=["GET"])
def getFavorites(id):
    favs = Favorites.query.get(id)

    return favorite_schema.jsonify(favs)

@app.route("/user/favs/<userId>", methods=["POST"])
def addFavorite(userId):
    """Recibe un bookId que agregar a la lista de libros favoritos."""
    
    data = request.json
    favs = Favorites.query.get(userId)

    bookList = json.loads(favs.books)
    bookList.append(data.bookId)
    favs.books = json.dumps(bookList)
    
    return favorite_schema.jsonify(favs)

@app.route("/user/favs/<userId>", methods=["PUT"])
def removeFavorite(userId):
    """Recibe un bookId que eliminar de la lista de libros favoritos."""
    
    data = request.json
    favs = Favorites.query.get(userId)

    bookList = json.loads(favs.books)
    bookList.remove(data.bookId)
    favs.books = json.dumps(bookList)
    
    return favorite_schema.jsonify(favs)

# ---- Profile ----


# ******* Trabajo en progreso. Hacer aquí toda las peticiones de agregar o quitar libros del carrito. ******






# ------------------ programa principal ------------------

if __name__=='__main__':  
    app.run(debug=True, port=5000)   # ejecuta el servidor Flask en el puerto 5000
