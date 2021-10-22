from flask import render_template, session, redirect, url_for,Flask, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from azure_librarian import Librarian
from azure_sentinel import Sentinel
from db_guardian import Guardian
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, length,DataRequired
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import db_god
import flask
import random
#from .models import Administrador
from sendgrid_dove import Dove
import requests
import datetime

API_KEY = 'AIzaSyAfkJTKOo-_TMG-mCW42Cy0jUXLQAq46xo'

# LESSONS
# https://www.restapitutorial.com/lessons/httpmethods.html
# return of every API call
# JSON, status code
# return flask.jsonify(result), 404

app = flask.Flask(__name__)
god = db_god.God()

app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)



@login_manager.user_loader
def load_user(admin_id):
    #sql_query="""SELECT * FROM Administrador WHERE id=?"""
    """sql_params=[admin_id]
    result = god.run_query(sql_query, sql_params)
    datos=result[0]
    correo=datos.correo
    nombre=datos.nombre"""
    admin=Administrador("mail","name")
    
    return admin
    #id logic for current user


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(),length(min=4,max=15)])
    password = PasswordField('password', validators=[InputRequired(),length(min=8,max=80)])

    submit = SubmitField("Login")

class AdminForm(FlaskForm):
    comentario = SelectField('Comentario', choices=["Ine incorrecto","CURP Incorrecto","Acta de nacimiento Incorrecta"])
    submitir_comentario = SubmitField("subir comentario")

    validar = SubmitField("Validar")
    bloquear = SubmitField("Bloquear")

    desbloquear = SubmitField("Desbloquear")
    invalidar = SubmitField("Invalidar")

    servicios_recibidos = SubmitField("Reporte Servicios Recibidos")
    servicios_ofrecidos = SubmitField("Reporte Servicios Ofrecidos")



class Administrador( UserMixin):
    def __init__(self,correo, nombre):
        self.correo=correo
        self.nombre=nombre
        
    def is_active(self):
        return(True)
    def get_id(self):
        sql_query="""SELECT * FROM Administrador WHERE correo=?"""
        sql_params=[self.correo]
        result = god.run_query(sql_query, sql_params)
        return result[0].id
    def is_authenticated(self):
        return 1
         

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500




@app.route("/enviaCodigoUsuario", methods=["POST"])
def enviaCodigoUsuario():
    json_data = flask.request.json
    correo = json_data['correo']
    verificacion = json_data['verificacion']
    
    # Generate 4-digit code
    code = random.randrange(1000, 10000, 4)
    code = str(code)
    
    # Look for the user
    sql_query = """SELECT * FROM Usuario WHERE correo = ?"""

    sql_params = [correo]

    result = god.run_query(sql_query, sql_params)

    # There's no registry
    if len(result) == 0:
        result = {"mensaje": "Usuario no encontrado!"}
        return flask.jsonify(result), 404
    
    db = result[0]
    db_nombre = db.nombre

    # Add code to database
    sql_query="""UPDATE Usuario SET codigo = ? WHERE correo = ?"""

    sql_params = [correo, code]
    print(sql_params)

    mensaje, status = god.run_insert(sql_query, sql_params)

    # Send code
    d = Dove()
    if verificacion == "correo":
        d.send_code_signup(correo, db_nombre, code)
    if verificacion == "contrasena":
        d.send_code_password(correo, db_nombre, code)
    
    result = {"mensaje": "Codigo enviado! Revisa tu bandeja de entrada/SPAM"}

    return flask.jsonify(result), 201

@app.route("/actualizarUsuario", methods=["POST"])
def actualizarUsuario():
    json_data = flask.request.json
    correo_anterior = json_data['correo_anterior']
    correo_nuevo = json_data['correo_nuevo']
    nombre = json_data['nombre']

    sql_query="""UPDATE Usuario SET nombre = ?, correo = ? WHERE correo = ?"""
    sql_params = [nombre, correo_nuevo, correo_anterior]
    print(sql_params)
    mensaje, status = god.run_insert(sql_query, sql_params)

    return flask.jsonify(mensaje), status


@app.route("/enviaCodigoPreusuario/<nombre>/<correo>", methods=["GET"])
def enviaCodigoPreusuario(nombre, correo):

    # Generate 4-digit code
    code = random.randrange(1000, 10000, 4)
    code = str(code)
    
    # Add temp user & code to database
    sql_query="""INSERT INTO Preusuario (correo, codigo) VALUES (?, ?)"""
    sql_params = [correo, code]
    print(sql_params)

    mensaje, status = god.run_insert(sql_query, sql_params)

    if status != 201:
        # Ya habia intentado registrarse antes
        sql_query="""UPDATE Preusuario SET codigo=? WHERE correo=?"""
        sql_params = [code, correo]
        print(sql_params)
        mensaje, status = god.run_insert(sql_query, sql_params)
        

    # Send code
    d = Dove()
    d.send_code_signup(correo, nombre, code)
    result = {"mensaje": "Codigo enviado! Revisa tu bandeja de entrada/SPAM"}
    
    return flask.jsonify(result), 201


@app.route("/verificaCodigo/<verificacion>/<correo>/<codigo>", methods=["GET"])
def verificaCodigo(verificacion, correo, codigo):

    if verificacion == "correo":
        sql_query = """SELECT * FROM Preusuario WHERE correo = ?"""
    
    if verificacion == "contrasena":
        sql_query = """SELECT * FROM Usuario WHERE correo = ?"""

    sql_params = [correo]

    result = god.run_query(sql_query, sql_params)

    # There's no registry
    if len(result) == 0:
        result = {"mensaje": "Usuario no encontrado!"}
        return flask.jsonify(result), 404
    
    db = result[0]
    db_codigo = db.codigo

    if db_codigo == codigo:
        result = {"mensaje": "Codigo valido!"}
        # TODO
        # if verificacion == 'correo'
        # eliminar preusuario
        return flask.jsonify(result), 200
    
    result = {"mensaje": "Codigo NO valido!"}
    return flask.jsonify(result), 404
    



@app.route("/registro", methods=["POST"])
def registro():
    json_data = flask.request.json
    correo = json_data['correo']
    contrasena = json_data['contrasena']
    nombre = json_data['nombre'] 
    edad = json_data['edad'] 
    municipio = json_data['municipio'] 
    colonia = json_data['colonia']
    genero = json_data['genero'] 
    celular = json_data['celular']
    imagen1_id = json_data['imagen1_id']
    imagen2_id = json_data['imagen2_id']
    imagen3_id = json_data['imagen3_id']
    imagen4_id = json_data['imagen4_id']

    l = Librarian()
    l.set_container("imagenes/Cara")
    l.open_connection()

    s = Sentinel()
    s.init_face()
    url = "https://filesmanager070901.blob.core.windows.net/imagenes/Cara/"

    print("URL 1: " + url+imagen1_id)
    print("URL 2: " + url+imagen2_id)
    print("URL 3: " + url+imagen3_id)
    print("URL 4: " + url+imagen4_id)

    
    result1 = s.verify_faces(url+imagen1_id, url+imagen2_id)
    result2 = s.verify_faces(url+imagen1_id, url+imagen3_id)
    result3 = s.verify_faces(url+imagen1_id, url+imagen4_id)

    if not result1 and not result2 and not result3: 
        l.delete_file(imagen1_id)
        l.delete_file(imagen2_id)
        l.delete_file(imagen3_id)
        l.delete_file(imagen4_id)

        result = {"mensaje": "Los rostros NO coinciden!"}
        return flask.jsonify(result), 409


    g = Guardian()
    hashed_password = g.hide_psw(contrasena)
    salt = g.get_salt()
    

    sql_query = """INSERT INTO Usuario (correo, contrasena, salt, nombre, edad, municipio, colonia, genero, celular, validado, bloqueado, acceso, imagen1, imagen2, imagen3, imagen4) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    sql_params = [correo, hashed_password, salt, nombre, edad, municipio, colonia, genero, celular, 0, 0, 0, url+imagen1_id, url+imagen2_id, url+imagen3_id, url+imagen4_id]
    
    print(sql_params)

    mensaje, status = god.run_insert(sql_query, sql_params)

    comentarios = "Por favor, sube tu documento!"

    sql_query = """INSERT INTO Archivo (correo_usuario, tipo, estado, comentarios) VALUES ( ?, ?, ?, ?)"""

    sql_params = [correo, "INE", 0, comentarios]
    print(sql_params)

    mensaje, status = god.run_insert(sql_query, sql_params)

    sql_params = [correo, "CURP", 0, comentarios]
    print(sql_params)

    mensaje, status = god.run_insert(sql_query, sql_params)

    sql_params = [correo, "Acta", 0, comentarios]
    print(sql_params)

    mensaje, status = god.run_insert(sql_query, sql_params)

    sql_params = [correo, "Carta", 0, comentarios]
    print(sql_params)

    mensaje, status = god.run_insert(sql_query, sql_params)

    sql_params = [correo, "Domicilio", 0, comentarios]
    print(sql_params)

    mensaje, status = god.run_insert(sql_query, sql_params)

    result={
            "mensaje":"Genial! Estas registrado!"
        }
    return flask.jsonify(result), 201

    

@app.route("/subirDoc", methods=["POST"])
def subirDoc():
    ## TODO
    # cambiar logica de archivos un boton para seleccionar y otro para enviar
    # una vez que envio se espera hasta que cambie de estado para volver a enviar

    # tipo: INE, CURP, Domicilio, Carta, Acta
    json_data = flask.request.json
    correo = json_data['correo']
    tipo = json_data['tipo']
    url = json_data['url']

    # Archivos upload!
    comentarios = "Hemos recibido tu documento! Estamos en proceso de revisión, vuelve dentro de 24h-72h para conocer más detalles."

    sql_query="""UPDATE Archivo SET link = ?, estado = ?, comentarios = ? WHERE correo_usuario = ? AND tipo = ?"""

    sql_params = [url, 1, comentarios, correo, tipo]
    print(sql_params)

    mensaje, status = god.run_insert(sql_query, sql_params)
    mensaje = {
        "mensaje" : tipo + "subido(a), espera un correo de confirmación!"
    }
    
    return flask.jsonify(mensaje), status

@app.route("/acceso", methods=["POST"])
def acceso():

    # Get user input
    json_data = flask.request.json
    correo = json_data['correo']
    contrasena = json_data['contrasena']

    # Look for the user

    sql_query = """SELECT * FROM Usuario WHERE correo = ?"""

    sql_params = [correo]

    result = god.run_query(sql_query, sql_params)

    # There's no registry
    if len(result) == 0:
        result = {"mensaje": "Usuario no encontrado!"}
        return flask.jsonify(result), 404
    
    db = result[0]
    db_contrasena = db.contrasena
    db_salt = db.salt

    guardian = Guardian()
    guardian.set_salt(db_salt)

    # Passwords match!
    if (guardian.verify_psw(contrasena, db_contrasena)):
        result = {"mensaje": "Inicio de sesion exitoso!"}
        return flask.jsonify(result), 200

    # Password did not match!
    result = {"mensaje": "Contrasena incorrecta!"}
    return flask.jsonify(result), 404

@app.route("/usuario/<correo>", methods=["GET"])
def usuario(correo):

    # Look for the user

    sql_query = """SELECT * FROM Usuario WHERE correo = ?"""

    sql_params = [correo]

    result = god.run_query(sql_query, sql_params)

    # There's no registry
    if len(result) == 0:
        result = {"mensaje": "Usuario no encontrado!"}
        return flask.jsonify(result), 404
    
    db = result[0]

    # User found!
    result = {  "correo": db.correo,
                "nombre": db.nombre,
                "edad" : db.edad,
                "municipio" : db.municipio,
                "colonia" : db.colonia,
                "validado": db.validado,
                "bloqueado": db.bloqueado,
                "acceso": db.acceso,
                "mensaje": "Usuario encontrado!",
                "imagen1": db.imagen1,
                "imagen2": db.imagen2
                }

    return flask.jsonify(result), 200

@app.route("/servicio/<id>", methods=["GET"])
def servicio(id):
    id = int(id)

    # Look for the servicio
    sql_query = """SELECT *
                    FROM Usuario
                    INNER JOIN Servicio ON Usuario.correo=Servicio.correo_ofrecio AND Servicio.id_servicio = ?"""

    sql_params = [id]

    result = god.run_query(sql_query, sql_params)

    # There's no registry
    if len(result) == 0:
        result = {"mensaje": "Ups te ganaron!"}
        return flask.jsonify(result), 404
    
    db = result[0]

    # User found!
    result = {  "nombre": db.nombre,
                "nom_servicio": db.nom_servicio,
                "mod_servicio": db.mod_servicio,
                "imagen_servicio" : db.imagen_servicio,
                "cat_servicio" : db.cat_servicio,
                "id_servicio": db.id_servicio,
                "des_servicio": db.des_servicio,
               
                }
    
    sql_query = """SELECT time_stamp
                    FROM Agenda
                    WHERE id_servicio = ? AND estado = ?"""

    sql_params = [id, 0]

    horarios = god.run_query(sql_query, sql_params)
    horarios_list = []

    # There's no registry
    if len(horarios) == 0:
        result = {"mensaje": "Ups te ganaron!"}
        return flask.jsonify(result), 404

    for h in horarios:
        horarios_list.append(h[0])
    
    print(horarios_list)

    
    result["horarios"] = horarios_list
   

    return flask.jsonify(result), 200

@app.route("/crearServicio", methods=["POST"])
def crearServicio():
    # Get user input
    json_data = flask.request.json
    correo = json_data['correo']
    categoria=json_data['categoria']
    nombre=json_data['nombre']
    descripcion=json_data['descripcion']
    modalidad=json_data['modalidad']
    id_imagen = json_data['id_imagen']

    url = "https://filesmanager070901.blob.core.windows.net/imagenes/Servicio/"
    imagen_url = url+id_imagen

    l = Librarian()
    l.set_container("imagenes/Servicio")
    l.open_connection()

    # Verificar al usuario que agenda
    sql_query="""SELECT acceso, bloqueado, validado FROM Usuario WHERE correo = ?"""
    sql_params=[correo]

    result = god.run_query(sql_query, sql_params)
    #Verificar que pueda agendar servicios
    if result[0][0]==1 or result[0][0]==2:
        result={
            "mensaje":"Usuario no puede crear servicio"
        }
        if id_imagen != "ic_servicio.png":
            l.delete_file(id_imagen)
        return flask.jsonify(result), 404
    #Verificar que no este bloqueado
    elif result[0][1]==True:
        result={
            "mensaje":"Usuario que crea está bloqueado"
        }
        if id_imagen != "ic_servicio.png":
            l.delete_file(id_imagen)
        return flask.jsonify(result), 404
    #Verificar que este validado 
    if result[0][2]==False:
        result={
            "mensaje":"Usuario que crea no está validado"
        }
        if id_imagen != "ic_servicio.png":
            l.delete_file(id_imagen)
        return flask.jsonify(result), 404



    print(imagen_url)
    s = Sentinel()
    s.init_image()
    result = s.analyze_image(imagen_url)

    if result:
        if id_imagen != "ic_servicio.png":
            l.delete_file(id_imagen)
        result = {"mensaje": "Imagen con contenido no apropiado!"}
        return flask.jsonify(result), 404

    

    # Insert service
    sql_query = """INSERT INTO Servicio (correo_ofrecio, cat_servicio, nom_servicio, des_servicio, mod_servicio, imagen_servicio) VALUES ( ?, ?, ?, ?, ?, ?)"""

    sql_params = [correo, categoria, nombre, descripcion, modalidad, imagen_url]

    mensaje, status = god.run_insert(sql_query, sql_params)

    sql_query = """SELECT * FROM Servicio WHERE correo_ofrecio = ? and cat_servicio =? and nom_servicio =? and des_servicio =? and mod_servicio =? and imagen_servicio=?"""

    sql_params = [correo,categoria,nombre,descripcion,modalidad, imagen_url]

    result = god.run_query(sql_query, sql_params)
    print(sql_params)

    mensaje = {"id": result[0][0]}

    return flask.jsonify(mensaje), 201

@app.route("/agregarHorasServicio", methods=["POST"])
def agregarHorasServicio():
    # Get user input
    json_data = flask.request.json
    id_servicio= json_data['id_servicio']
    id_servicio = int(id_servicio)
    horarios=json_data['horarios']

    print(horarios)

    for horario in horarios:
        sql_query = """INSERT INTO Agenda (id_servicio,time_stamp, estado) VALUES (?, ?, ?)"""
        sql_params = [id_servicio, horario, 0]
        mensaje, status = god.run_insert(sql_query, sql_params)
    return flask.jsonify(mensaje), status


@app.route("/listarServicio/<correo>/<categoria>/<modalidad>", methods=["GET"])
def listarServicio(correo,categoria,modalidad):

    if categoria=="Todos" and modalidad=="Todas":
        sql_query = """SELECT Agenda.id_servicio, Servicio.nom_servicio, Servicio.mod_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, MIN(Agenda.time_stamp), Servicio.correo_ofrecio
            FROM Agenda
            INNER JOIN Servicio ON Agenda.id_servicio = Servicio.id_servicio AND Agenda.estado=? AND Servicio.correo_ofrecio <> ?
            GROUP BY Agenda.id_servicio, Agenda.estado, Servicio.correo_ofrecio, Servicio.nom_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, Servicio.mod_servicio"""
        sql_params = [0, correo]
    elif categoria=="Todos":
        sql_query = """SELECT Agenda.id_servicio, Servicio.nom_servicio, Servicio.mod_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, MIN(Agenda.time_stamp), Servicio.correo_ofrecio
            FROM Agenda
            INNER JOIN Servicio ON Agenda.id_servicio = Servicio.id_servicio AND Agenda.estado=? AND Servicio.correo_ofrecio <> ? AND Servicio.mod_servicio = ?
            GROUP BY Agenda.id_servicio, Agenda.estado, Servicio.correo_ofrecio, Servicio.nom_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, Servicio.mod_servicio"""
        sql_params = [0, correo, modalidad]

    elif modalidad=="Todas":
        sql_query = """SELECT Agenda.id_servicio, Servicio.nom_servicio, Servicio.mod_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, MIN(Agenda.time_stamp), Servicio.correo_ofrecio
            FROM Agenda
            INNER JOIN Servicio ON Agenda.id_servicio = Servicio.id_servicio AND Agenda.estado=? AND Servicio.correo_ofrecio <> ? AND Servicio.cat_servicio = ?
            GROUP BY Agenda.id_servicio, Agenda.estado, Servicio.correo_ofrecio, Servicio.nom_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, Servicio.mod_servicio"""
        sql_params = [0, correo,categoria]
    else:
        sql_query = """SELECT Agenda.id_servicio, Servicio.nom_servicio, Servicio.mod_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, MIN(Agenda.time_stamp), Servicio.correo_ofrecio
            FROM Agenda
            INNER JOIN Servicio ON Agenda.id_servicio = Servicio.id_servicio AND Agenda.estado=? AND Servicio.correo_ofrecio <> ? AND Servicio.mod_servicio = ? AND Servicio.cat_servicio=?
            GROUP BY Agenda.id_servicio, Agenda.estado, Servicio.correo_ofrecio, Servicio.nom_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, Servicio.mod_servicio"""
        sql_params = [0, correo,modalidad,categoria]    


    
    rAux = []
    whole = {}

    result = god.run_query(sql_query, sql_params)
    if( len(result)==0):
        jaux={
            "id":"1",
            "nombre":"NONE",
            "modalidad":"NONE",
            "categoria":categoria,
            "img_servicio":"https://filesmanager070901.blob.core.windows.net/imagenes/Servicio/ic_servicio.png",
        }
        rAux.append(jaux)

        whole["servicios"] = rAux
        return flask.jsonify(whole), 200

    for i in result:
        jaux={
            "id":i[0],
            "nombre":i[1],
            "modalidad":i[2],
            "categoria":i[3],
            "img_servicio":i[4],
        }
        rAux.append(jaux)

   

    whole["servicios"] = rAux
    
    return flask.jsonify(whole), 200

@app.route("/agendar", methods=["PATCH"])
def agendar():
    json_data = flask.request.json
    idServicio = json_data['id_servicio']
    horario = json_data['horario']
    correoAgendo = json_data['correo_agendo']
    longitud = json_data['longitud']
    latitud = json_data['latitud']

    idServicio = int(idServicio)

    # Verificar al usuario que agenda
    sql_query="""SELECT acceso, bloqueado, validado FROM Usuario WHERE correo = ?"""
    sql_params=[correoAgendo]

    result = god.run_query(sql_query, sql_params)
    #Verificar que pueda agendar servicios
    
    #if result[0][0]==-1 or result[0][0]==2:
        #result={
        #    "mensaje":"Usuario no puede agendar servicio"
        #}
        #return flask.jsonify(result), 404
    #Verificar que no este bloqueado
    if result[0][1]==True:
        result={
            "mensaje":"Usuario que agenda está bloqueado"
        }
        return flask.jsonify(result), 404
    #Verificar que este validado 
    if result[0][2]==False:
        result={
            "mensaje":"Usuario que agenda no está validado"
        }
        return flask.jsonify(result), 404

    #Obtener correo del que ofrece
    sql_query="""SELECT correo_ofrecio FROM Servicio WHERE id_servicio = ?"""
    print(sql_query)
    sql_params=[idServicio]
    result = god.run_query(sql_query, sql_params)
    print(result)
    correo=result[0][0]

    if len(correo) == 0:
        result={
            "mensaje":"Usuario ya no ofrece el servicio!"
        }
        return flask.jsonify(result), 404


    #Verificar usuario que ofrece
    sql_query="""SELECT acceso, bloqueado, validado FROM Usuario WHERE correo = ?"""
    sql_params=[correo]

    result = god.run_query(sql_query, sql_params)
    #Verificar que pueda ofrecer servicios
    #if result[0][0]==1 or result[0][0]==2:
    #    result={
    #        "mensaje":"Usuario no puede ofrecer servicio"
    #    }
    #    return flask.jsonify(result), 404
    #Verificar que no este bloqueado
    if result[0][1]==True:
        result={
            "mensaje":"Usuario que ofrece bloqueado"
        }
        return flask.jsonify(result), 404
   #Verificar que este validado 
    if result[0][2]==False:
        result={
            "mensaje":"Usuario que ofrece no validado"
        }
        return flask.jsonify(result), 404

    #Se puede agendar servicio 
    sql_query="""UPDATE Servicio SET correo_agendo=? WHERE id_servicio=?"""
    sql_params=[correoAgendo,idServicio]

    mensaje, status = god.run_insert(sql_query, sql_params)
    
    if status==409:
        mensaje={"mensaje": "Error al agendar servicio!"}
        return flask.jsonify(mensaje), 409

    sql_query="""UPDATE Servicio SET latitud=? WHERE id_servicio=?"""
    sql_params=[latitud,idServicio]

    mensaje, status = god.run_insert(sql_query, sql_params)
    
    if status==409:
        mensaje={"mensaje": "Error al agendar servicio!"}
        return flask.jsonify(mensaje), 409

    sql_query="""UPDATE Servicio SET longitud=? WHERE id_servicio=?"""
    sql_params=[longitud,idServicio]

    mensaje, status = god.run_insert(sql_query, sql_params)
    
    if status==409:
        mensaje={"mensaje": "Error al agendar servicio!"}
        return flask.jsonify(mensaje), 409

    sql_query="""UPDATE Agenda SET estado=? WHERE id_servicio=? AND time_stamp=?"""
    sql_params=[1,idServicio, horario]

    mensaje, status = god.run_insert(sql_query, sql_params)
    
    if status==409:
        mensaje={"mensaje": "Error al agendar servicio!"}
        return flask.jsonify(mensaje), 409

    # Borrar todos los demas horarios de Agenda
    sql_query="""DELETE FROM Agenda WHERE id_servicio=? AND estado=?"""
    sql_params=[idServicio, 0]
    mensaje, status=god.run_insert(sql_query, sql_params)
    if status==409:
        mensaje={"mensaje": "Error al borrar agenda!"}
        return flask.jsonify(mensaje), 409


    #Cambiar acceso usuario que agenda
    sql_query="""UPDATE Usuario SET acceso=? WHERE correo=?"""
    sql_params=[2,correoAgendo]
    mensaje, status=god.run_insert(sql_query, sql_params)
    if status==409:
        mensaje={"mensaje": "Error al actualizar acceso del que agenda!"}
        return flask.jsonify(mensaje), 409

    #Cambiar acceso usuario que ofrece
    sql_query="""UPDATE Usuario SET acceso=? WHERE correo=?"""
    sql_params=[2,correo]
    mensaje, status=god.run_insert(sql_query, sql_params)
    if status==409:
        mensaje={"mensaje": "Error al actualizar acceso del que ofrece!"}
        return flask.jsonify(mensaje), 409

    url_map = "https://www.google.com/maps/search/?api=1&query="+str(latitud)+","+str(longitud)

    # 1. Get info OFRECIO
    
    sql_query="""SELECT * FROM Usuario WHERE correo = ?"""
    sql_params=[correo]

    result = god.run_query(sql_query, sql_params)

    db = result[0]
    nombre_ofrecio = db.nombre
    imagen_ofrecio = db.imagen1
    celular_ofrecio = db.celular

    # 1. Get info AGENDO
    
    sql_query="""SELECT * FROM Usuario WHERE correo = ?"""
    sql_params=[correoAgendo]

    result = god.run_query(sql_query, sql_params)

    db = result[0]
    nombre_agendo = db.nombre
    imagen_agendo = db.imagen1
    celular_agendo = db.celular

    # 3. Info servicio

    sql_query="""SELECT * FROM Servicio WHERE id_servicio = ?"""
    print(sql_query)
    sql_params=[idServicio]
    result = god.run_query(sql_query, sql_params)

    db = result[0]
    mod = db.mod_servicio

    sql_query="""SELECT * FROM Agenda WHERE id_servicio = ?"""
    print(sql_query)
    sql_params=[idServicio]
    result = god.run_query(sql_query, sql_params)

    db = result[0]
    fecha_hora = db.time_stamp
    int_f = int(fecha_hora) / 1000.0
    fecha_hora = datetime.datetime.fromtimestamp(int_f).strftime('%d de %B de %Y %H:%M')

    # Enviar correo

    d = Dove()

    # Enviar correo con servicio info QUIEN AGENDO
     
    d.send_confirm_agendo(correoAgendo, nombre_agendo, nombre_ofrecio, fecha_hora, url_map, mod, imagen_ofrecio, celular_ofrecio)

    # Enviar correo con servicio info QUIEN OFRECIO

    d.send_confirm_ofrecio(correo, nombre_ofrecio, nombre_agendo, fecha_hora, url_map, mod, imagen_agendo, celular_agendo)


    #Todo se ha creado correctamente
    mensaje={"mensaje": "Servicio agendado correctamente, revisa tu correo para detalles"}
    return flask.jsonify(mensaje), 200

@app.route("/validarUsuario", methods=["PATCH"])
def validarUsuario():
    json_data = flask.request.json
    correo = json_data['correo']
    #Cambiar acceso usuario que agenda
    sql_query="""UPDATE Usuario SET validado=? WHERE correo=?"""
    sql_params=[1,correo]
    mensaje, status=god.run_insert(sql_query, sql_params)
    if status==409:
        mensaje={"mensaje": "Error al actualizar validado!"}
        return flask.jsonify(mensaje), 409
    return flask.jsonify(mensaje), status

@app.route("/bloquearUsuario", methods=["PATCH"])
def bloquearUsuario():
    json_data = flask.request.json
    correo = json_data['correo']
    #Cambiar acceso usuario que agenda
    sql_query="""UPDATE Usuario SET bloqueado=? WHERE correo=?"""
    sql_params=[1,correo]
    mensaje, status=god.run_insert(sql_query, sql_params)
    if status==409:
        mensaje={"mensaje": "Error al bloquear usuario!"}
        return flask.jsonify(mensaje), 409
    return flask.jsonify(mensaje), status

@app.route("/desbloquearUsuario", methods=["PATCH"])
def desbloquearUsuario():
    json_data = flask.request.json
    correo = json_data['correo']
    #Cambiar acceso usuario que agenda
    sql_query="""UPDATE Usuario SET bloqueado=? WHERE correo=?"""
    sql_params=[0,correo]
    mensaje, status=god.run_insert(sql_query, sql_params)
    if status==409:
        mensaje={"mensaje": "Error al desbloquear usuario!"}
        return flask.jsonify(mensaje), 409
    return flask.jsonify(mensaje), status

@app.route("/cambiarAccesoUsuario", methods=["PATCH"])
def cambiarAccesoUsuario():
    json_data = flask.request.json
    correo = json_data['correo']
    acceso = json_data['acceso']
    #Cambiar acceso usuario que agenda
    sql_query="""UPDATE Usuario SET acceso=? WHERE correo=?"""
    sql_params=[acceso,correo]
    mensaje, status=god.run_insert(sql_query, sql_params)
    if status==409:
        mensaje={"mensaje": "Error al cambiar accesos!"}
        return flask.jsonify(mensaje), 409
    return flask.jsonify(mensaje), status


@app.route("/cambiarContrasena", methods=["PATCH"])
def cambiarContrasena():
    json_data = flask.request.json
    correo = json_data['correo']
    contrasena = json_data['contrasena']

    g = Guardian()
    hashed_password = g.hide_psw(contrasena)
    salt = g.get_salt()

    sql_query="""UPDATE Usuario SET contrasena = ?, salt = ? WHERE correo = ?"""
    sql_params = [hashed_password, salt, correo]
    mensaje, status = god.run_insert(sql_query, sql_params)


    if mensaje != 201:
        mensaje = {
            "mensaje" : "Ocurrió un error, intente más tarde!"
        }

    return flask.jsonify(mensaje), status

@app.route("/invalidarUsuario", methods=["PATCH"])
def invalidarUsuario():
    json_data = flask.request.json
    correo = json_data['correo']
    #Cambiar acceso usuario que agenda
    sql_query="""UPDATE Usuario SET validado=? WHERE correo=?"""
    sql_params=[0,correo]
    mensaje, status=god.run_insert(sql_query, sql_params)
    if status==409:
        mensaje={"mensaje": "Error al invalidar!"}
        return flask.jsonify(mensaje), 409
    return flask.jsonify(mensaje), status

@app.route("/buscaCategoria", methods=["POST"])
def buscaCategoria():
    json_data = flask.request.json
    categoria = json_data['categoria']
    busqueda = json_data['busqueda']
    busqueda = '%' + busqueda + '%'
    correo = json_data['correo']

    sql_query = """SELECT Agenda.id_servicio, Servicio.nom_servicio, Servicio.mod_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, MIN(Agenda.time_stamp), Servicio.correo_ofrecio
            FROM Agenda
            INNER JOIN Servicio ON Agenda.id_servicio = Servicio.id_servicio AND Agenda.estado=? AND Servicio.correo_ofrecio <> ? AND Servicio.cat_servicio=? AND Servicio.nom_servicio LIKE ?
            GROUP BY Agenda.id_servicio, Agenda.estado, Servicio.correo_ofrecio, Servicio.nom_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, Servicio.mod_servicio"""
    sql_params = [0, correo, categoria, busqueda]

    
    rAux = []
    whole = {}

    result = god.run_query(sql_query, sql_params)
    if( len(result)==0):
        jaux={
            "id":"1",
            "nombre":"NONE",
            "modalidad":"NONE",
            "categoria":categoria,
            "img_servicio":"https://filesmanager070901.blob.core.windows.net/imagenes/Servicio/ic_servicio.png",
        }
        rAux.append(jaux)

        whole["servicios"] = rAux
        return flask.jsonify(whole), 200

    for i in result:
        jaux={
            "id":i[0],
            "nombre":i[1],
            "modalidad":i[2],
            "categoria":i[3],
            "img_servicio":i[4],
        }
        rAux.append(jaux)

   

    whole["servicios"] = rAux
    
    return flask.jsonify(whole), 200



@app.route("/listarAgendadoA/<correo>", methods=["GET"])
def listarAgendadoA(correo):

    
    sql_query = """SELECT S.id_servicio, S.correo_ofrecio, S.nom_servicio, S.des_servicio, S.cat_servicio, S.mod_servicio, S.imagen_servicio, S.longitud, S.latitud, A.time_stamp, U.nombre
    FROM Servicio as S, Agenda as A, Usuario as U
    WHERE S.correo_agendo = ? and A.estado = 1 and S.id_servicio=A.id_servicio and U.correo= S.correo_ofrecio"""
    sql_params = [correo]

    result = god.run_query(sql_query, sql_params)
    if( len(result)==0):
        result={
            "mensaje":"Servicios no encontrados"
        }
        return flask.jsonify(result), 404
    rAux=[]
    for i in result:
        jaux={
            "idS":i[0],
            "correoO":i[1],
            "nombreS":i[2],
            "descripcion":i[3],
            "categoria":i[4],
            "modalidad":i[5],
            "imagen":i[6],
            "longitud":i[7],
            "latitud":i[8],
            "timeStamp":i[9],
            "nombreO":i[10],

        }
        rAux.append(jaux)

    
    return flask.jsonify(rAux), 200

@app.route("/listarAgendadoO/<correo>", methods=["GET"])
def listarAgendadoO(correo):

    
    sql_query = """SELECT S.id_servicio, S.correo_agendo, S.nom_servicio, S.des_servicio, S.cat_servicio, S.mod_servicio, S.imagen_servicio, S.longitud, S.latitud, A.time_stamp, U.nombre
    FROM Servicio as S, Agenda as A, Usuario as U
    WHERE S.correo_ofrecio = ? and A.estado = 1 and S.id_servicio=A.id_servicio and U.correo= S.correo_agendo"""
    sql_params = [correo]

    result = god.run_query(sql_query, sql_params)
    if( len(result)==0):
        result={
            "mensaje":"Servicios no encontrados"
        }
        return flask.jsonify(result), 404
    rAux=[]
    for i in result:
        jaux={
            "idS":i[0],
            "correoA":i[1],
            "nombreS":i[2],
            "descripcion":i[3],
            "categoria":i[4],
            "modalidad":i[5],
            "imagen":i[6],
            "longitud":i[7],
            "latitud":i[8],
            "timeStamp":i[9],
            "nombreA":i[10],

        }
        rAux.append(jaux)

    
    return flask.jsonify(rAux), 200

@app.route("/listarCompletadoA/<correo>", methods=["GET"])
def listarCompletadoA(correo):

    
    sql_query = """SELECT S.id_servicio, S.correo_ofrecio, S.nom_servicio, S.des_servicio, S.cat_servicio, S.mod_servicio, S.imagen_servicio, S.longitud, S.latitud, A.time_stamp, U.nombre
    FROM Servicio as S, Agenda as A, Usuario as U
    WHERE S.correo_agendo = ? and A.estado = 2 and S.id_servicio=A.id_servicio and U.correo= S.correo_ofrecio"""
    sql_params = [correo]

    result = god.run_query(sql_query, sql_params)
    if( len(result)==0):
        result={
            "mensaje":"Servicios no encontrados"
        }
        return flask.jsonify(result), 404
    rAux=[]
    for i in result:
        jaux={
            "idS":i[0],
            "correoO":i[1],
            "nombreS":i[2],
            "descripcion":i[3],
            "categoria":i[4],
            "modalidad":i[5],
            "imagen":i[6],
            "longitud":i[7],
            "latitud":i[8],
            "timeStamp":i[9],
            "nombreO":i[10],

        }
        rAux.append(jaux)

    
    return flask.jsonify(rAux), 200    

@app.route("/listarCompletadoO/<correo>", methods=["GET"])
def listarCompletadoO(correo):

    
    sql_query = """SELECT S.id_servicio, S.correo_agendo, S.nom_servicio, S.des_servicio, S.cat_servicio, S.mod_servicio, S.imagen_servicio, S.longitud, S.latitud, A.time_stamp, U.nombre
    FROM Servicio as S, Agenda as A, Usuario as U
    WHERE S.correo_ofrecio = ? and A.estado = 2 and S.id_servicio=A.id_servicio and U.correo= S.correo_agendo"""
    sql_params = [correo]

    result = god.run_query(sql_query, sql_params)
    if( len(result)==0):
        result={
            "mensaje":"Servicios no encontrados"
        }
        return flask.jsonify(result), 404
    rAux=[]
    for i in result:
        jaux={
            "idS":i[0],
            "correoA":i[1],
            "nombreS":i[2],
            "descripcion":i[3],
            "categoria":i[4],
            "modalidad":i[5],
            "imagen":i[6],
            "longitud":i[7],
            "latitud":i[8],
            "timeStamp":i[9],
            "nombreA":i[10],

        }
        rAux.append(jaux)

    
    return flask.jsonify(rAux), 200

@app.route("/obtenerQR/<idServicio>", methods=["GET"])
def obtenerQR(idServicio):
    response = {
        "link": "https://api.qrserver.com/v1/create-qr-code/?data="+ idServicio + "size=250x250"
    }
    return flask.jsonify(response), 200

@app.route("/listarAC/<correo>/<op>", methods=["GET"])
def listarAC(correo,op):
    #op 1 Agendado (Para quien agenda) -> ACTIVO
    #op 2 Agendado (Para quien ofrece) -> ACTIVO
    #op 3 Completado (Para quien agendó) -> HISTORIAL
    #op 4 Completado (Para quien ofreció) -> HISTORIAL
    if int(op)==1:
        estado = 1
        sql_query = """SELECT S.id_servicio, S.correo_ofrecio, S.nom_servicio, S.des_servicio, S.cat_servicio, S.mod_servicio, S.imagen_servicio, S.longitud, S.latitud, S.calificacion, A.time_stamp, A.estado, U.nombre
        FROM Servicio as S, Agenda as A, Usuario as U
        WHERE S.correo_agendo = ? and A.estado = ? and S.id_servicio=A.id_servicio and U.correo= S.correo_ofrecio"""
        sql_params = [correo, estado]
    elif int(op)==2:
        estado = 1
        sql_query = """SELECT S.id_servicio, S.correo_agendo, S.nom_servicio, S.des_servicio, S.cat_servicio, S.mod_servicio, S.imagen_servicio, S.longitud, S.latitud, S.calificacion, A.time_stamp, A.estado, U.nombre
        FROM Servicio as S, Agenda as A, Usuario as U
        WHERE S.correo_ofrecio = ? and A.estado = ? and S.id_servicio=A.id_servicio and U.correo= S.correo_agendo"""
        sql_params = [correo, estado]
    elif int(op)==3:
        estado = 2
        sql_query = """SELECT S.id_servicio, S.correo_ofrecio, S.nom_servicio, S.des_servicio, S.cat_servicio, S.mod_servicio, S.imagen_servicio, S.longitud, S.latitud, S.calificacion, A.time_stamp, A.estado, U.nombre
        FROM Servicio as S, Agenda as A, Usuario as U
        WHERE S.correo_agendo = ? and A.estado = ? and S.id_servicio=A.id_servicio and U.correo= S.correo_ofrecio"""
        sql_params = [correo, estado]
    elif int(op)==4:
        estado = 2
        sql_query = """SELECT S.id_servicio, S.correo_agendo, S.nom_servicio, S.des_servicio, S.cat_servicio, S.mod_servicio, S.imagen_servicio, S.longitud, S.latitud, S.calificacion, A.time_stamp, A.estado, U.nombre
        FROM Servicio as S, Agenda as A, Usuario as U
        WHERE S.correo_ofrecio = ? and A.estado = ? and S.id_servicio=A.id_servicio and U.correo= S.correo_agendo"""
        sql_params = [correo, estado]

    rAux=[]
    whole = {}

    result = god.run_query(sql_query, sql_params)

    if(len(result)==0):
        jaux={
            "id":"1",
            "nombre":"NONE",
            "modalidad":"NONE",
            "categoria":"NONE",
            "img_servicio":"https://filesmanager070901.blob.core.windows.net/imagenes/Servicio/ic_servicio.png",
            "estado":"NONE",
            "calificacion": "Calificación: NONE"
        }
        rAux.append(jaux)

        whole["servicios"] = rAux
        return flask.jsonify(whole), 200


    
    for i in result:
        jaux={
            "id":str(i[0]),
            "correo":i[1],
            "nombre":i[2],
            "descripcion":i[3],
            "categoria":i[4],
            "modalidad":i[5],
            "img_servicio":i[6],
            "longitud":i[7],
            "latitud":i[8],
            "calificacion":"Calificación: "+str(i[9]),
            "estado":op

        }
        rAux.append(jaux)


    whole["servicios"] = rAux
    return flask.jsonify(whole), 200


@app.route('/', methods=['GET','POST'])
def admin_login():
    form = LoginForm()
    if form.is_submitted():
        correo=form.username.data
        sql_query="""SELECT * FROM Administrador WHERE correo = ?"""
        sql_params=[correo]
        users = god.run_query(sql_query, sql_params)
        print("query done")
        if  len(users) > 0:
            
                

            
            contrasena=form.password.data
            user = users[0]
            user_contrasena = user.contrasena
            #correo=user.correo
            user_salt = user.salt

            guardian = Guardian()
            guardian.set_salt(user_salt)

            # Passwords match!
            if (guardian.verify_psw(contrasena, user_contrasena)):
                
                admin=Administrador(correo,"name")
                login_user(admin)
                
                return redirect(url_for('dashboard'))

            # Password did not match!
            print("Contraseña incorrecta")
        print("Usuario no encontrado")

    return render_template('login.html', form=form)




@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    
    result_aux= []
    sql_query = """SELECT correo, nombre, edad, municipio, colonia, validado, bloqueado FROM Usuario"""
    result=god.run_query(sql_query,[])

    for i in result:

        sql_query = """SELECT  count(S.id_servicio)
        FROM Servicio as S, Agenda as A
        WHERE S.correo_ofrecio = ?  and S.id_servicio=A.id_servicio """

        sql_query1 = """SELECT  count(S.id_servicio)
            FROM Servicio as S, Agenda as A
            WHERE S.correo_agendo = ?  and S.id_servicio=A.id_servicio """
        
        sql_query3="SELECT AVG(calificacion) FROM [dbo].[Servicio], [dbo].[Agenda] WHERE correo_ofrecio=? AND estado=2"
        

        sql_params = [i[0]]
        promedio = god.run_query(sql_query3,sql_params)[0][0]
        result_aux.append([god.run_query(sql_query,sql_params)[0][0],i[0],i[1],i[2],i[3],i[4],i[5],i[6],god.run_query(sql_query1,sql_params)[0][0], promedio])
        

    return render_template('dashboard.html', result=result_aux)


@app.route('/admin_logout',methods=['GET','POST'])
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))
    
@app.route('/perfil/<correo>',methods=['GET','POST'])
@login_required
def perfil(correo):
    filetype="filetype"
    form = AdminForm()
    sql_query=""" SELECT imagen1, validado, bloqueado FROM Usuario WHERE correo=?  """
    sql_params=[correo]
    result=god.run_query(sql_query,sql_params)
    imagen=result[0][0]
    validado=result[0][1]
    bloqueado=result[0][2]
    sql_query=""" SELECT link, tipo FROM Archivo WHERE correo_usuario=? AND link!='' """
    sql_params=[correo]
    archivos=god.run_query(sql_query,sql_params)

    if form.servicios_recibidos.data==1:    
        return redirect(url_for('reportes',correo=correo,tipo='recibidos'))  

    elif form.servicios_ofrecidos.data==1:    
        return redirect(url_for('reportes',correo=correo,tipo='ofrecidos'))

    elif form.validar.data == 1:
        sql_query="""SELECT nombre FROM Usuario WHERE correo = ?"""
        sql_params=[correo]
        nombre = god.run_query(sql_query,sql_params)[0][0]

        sql_query="""UPDATE Usuario SET validado = 1 WHERE correo = ?"""
        sql_params = [correo]
        mensaje, status = god.run_insert(sql_query,sql_params)
        validado=True

        d=Dove()
        d.send_good_file_message(correo, nombre)

    elif form.invalidar.data == 1:    
        sql_query="""UPDATE Usuario SET validado = 0 WHERE correo = ?"""
        sql_params = [correo]
        mensaje, status = god.run_insert(sql_query,sql_params)
        validado=False


    elif form.bloquear.data == 1:    
        sql_query="""UPDATE Usuario SET bloqueado = 1 WHERE correo = ?"""
        sql_params = [correo]
        mensaje, status = god.run_insert(sql_query,sql_params)
        bloqueado=True

    elif form.desbloquear.data == 1:    
        sql_query="""UPDATE Usuario SET bloqueado = 0 WHERE correo = ?"""
        sql_params = [correo]
        mensaje, status = god.run_insert(sql_query,sql_params)
        bloqueado=False
    
    if form.submitir_comentario.data ==1:
        
        comentario=form.comentario.data
        sql_query="""UPDATE Archivo SET comentarios = ? WHERE correo_usuario = ?"""
        sql_params=[comentario,correo]
        mensaje, status = god.run_insert(sql_query,sql_params)

        
        sql_query="""SELECT nombre FROM Usuario WHERE correo = ?"""
        sql_params=[correo]
        nombre = god.run_query(sql_query,sql_params)[0][0]

        if comentario == "Ine incorrecto":
            filetype="ine"
        elif comentario == "CURP incorrecto":
            filetype="CURP"
        elif comentario == "Acta de nacimiento incorrecta":
            filetype="Acta de nacimiento"

        print(correo, nombre, comentario, filetype)
        d=Dove()
        d.send_bad_file_message(correo,nombre,comentario,filetype, )

        

    #PIE CHART QUERY
    
    sql_query = """SELECT  count(calificacion)
    FROM Servicio as S
    WHERE S.correo_ofrecio = ?    and S.calificacion = 5 """
    sql_params=[correo]
    estrellas_5 = god.run_query(sql_query,sql_params)

    sql_query = """SELECT  count(calificacion)
    FROM Servicio as S
    WHERE S.correo_ofrecio = ?    and S.calificacion = 4 """
    sql_params=[correo]
    estrellas_4 = god.run_query(sql_query,sql_params)

    sql_query = """SELECT  count(calificacion)
    FROM Servicio as S
    WHERE S.correo_ofrecio = ?    and   S.calificacion = 3 """
    sql_params=[correo]
    estrellas_3 = god.run_query(sql_query,sql_params)

    sql_query = """SELECT  count(calificacion)
    FROM Servicio as S
    WHERE S.correo_ofrecio = ?    and S.calificacion = 2 """
    sql_params=[correo]
    estrellas_2 = god.run_query(sql_query,sql_params)

    sql_query = """SELECT  count(calificacion)
    FROM Servicio as S
    WHERE S.correo_ofrecio = ?    and S.calificacion = 1 """
    sql_params=[correo]
    estrellas_1 = god.run_query(sql_query,sql_params)

    sql_query = """SELECT  count(calificacion)
    FROM Servicio as S
    WHERE S.correo_ofrecio = ?   and S.calificacion = 0 """
    sql_params=[correo]
    estrellas_0 = god.run_query(sql_query,sql_params)

    estrellas=[estrellas_0,estrellas_1,estrellas_2 , estrellas_3, estrellas_4 , estrellas_5]
    return render_template('perfil.html', correo=correo,imagen=imagen,validado=validado,bloqueado=bloqueado,archivos=archivos,form=form, estrellas=estrellas)


@app.route('/reportes/<correo>/<tipo>',methods=['GET','POST'])
@login_required
def reportes(correo,tipo):
    promedio=""
    if tipo == "recibidos":
        sql_query="""SELECT  count(S.id_servicio)
            FROM Servicio as S, Agenda as A
            WHERE S.correo_agendo = ?  and S.id_servicio=A.id_servicio and A.estado=2"""
        sql_params=[correo]
        completados= god.run_query(sql_query,sql_params)[0][0]

        sql_query="""SELECT  count(S.id_servicio)
            FROM Servicio as S, Agenda as A
            WHERE S.correo_agendo = ?  and S.id_servicio=A.id_servicio and A.estado=3"""
        sql_params=[correo]
        cancelados= god.run_query(sql_query,sql_params)[0][0]

        sql_query="""SELECT  count(S.id_servicio)
            FROM Servicio as S, Agenda as A
            WHERE S.correo_agendo = ?  and S.id_servicio=A.id_servicio and A.estado=4"""
        sql_params=[correo]
        no_completados= god.run_query(sql_query,sql_params)[0][0]

        sql_query="""SELECT  count(S.id_servicio)
            FROM Servicio as S, Agenda as A
            WHERE S.correo_agendo = ?  and S.id_servicio=A.id_servicio and A.estado=0"""
        sql_params=[correo]
        no_agendado= god.run_query(sql_query,sql_params)[0][0]

        sql_query="""SELECT  count(S.id_servicio)
            FROM Servicio as S, Agenda as A
            WHERE S.correo_agendo = ?  and S.id_servicio=A.id_servicio and A.estado=1"""
        sql_params=[correo]
        agendado= god.run_query(sql_query,sql_params)[0][0]




    if tipo == "ofrecidos":
        sql_query="""SELECT  count(S.id_servicio)
            FROM Servicio as S, Agenda as A
            WHERE S.correo_ofrecio = ?  and S.id_servicio=A.id_servicio and A.estado=2"""
        sql_params=[correo]
        completados= god.run_query(sql_query,sql_params)[0][0]

        sql_query="""SELECT  count(S.id_servicio)
            FROM Servicio as S, Agenda as A
            WHERE S.correo_ofrecio = ?  and S.id_servicio=A.id_servicio and A.estado=3"""
        sql_params=[correo]
        cancelados= god.run_query(sql_query,sql_params)[0][0]

        sql_query="""SELECT  count(S.id_servicio)
            FROM Servicio as S, Agenda as A
            WHERE S.correo_ofrecio = ?  and S.id_servicio=A.id_servicio and A.estado=4"""
        sql_params=[correo]
        no_completados= god.run_query(sql_query,sql_params)[0][0]

        sql_query="SELECT AVG(calificacion) FROM [dbo].[Servicio], [dbo].[Agenda] WHERE correo_ofrecio=? AND estado=2"
        sql_params=[correo]
        promedio = god.run_query(sql_query,sql_params)[0][0]

        sql_query="""SELECT  count(S.id_servicio)
            FROM Servicio as S, Agenda as A
            WHERE S.correo_ofrecio = ?  and S.id_servicio=A.id_servicio and A.estado=0"""
        sql_params=[correo]
        no_agendado= god.run_query(sql_query,sql_params)[0][0]

        sql_query="""SELECT  count(S.id_servicio)
            FROM Servicio as S, Agenda as A
            WHERE S.correo_ofrecio = ?  and S.id_servicio=A.id_servicio and A.estado=1"""
        sql_params=[correo]
        agendado= god.run_query(sql_query,sql_params)[0][0]




    return render_template('reportes.html',correo=correo,tipo=tipo, completados=completados, cancelados=cancelados, no_completados=no_completados,promedio=promedio,agendado=agendado, no_agendado=no_agendado)


@app.route("/geo", methods=["POST"])
def geo():
    # Get user input
    json_data = flask.request.json
    direccion= json_data['direccion']

    
    params = {
        'key': API_KEY,
        'address': direccion.replace(' ', '+')
    }

    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(base_url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        result = data['results'][0]
        location = result['geometry']['location']

        result={"latitud " : location['lat'],
            "longitud  " : location['lng']
        }
        return flask.jsonify(result), 200
    else:
        return flask.jsonify('No se pudo encontrar la ubicación'), 404
        

    

@app.route("/buscarServicio/<correo>/<nombre>/<categoria>", methods=["GET"])
def buscarServicio(correo,nombre="",categoria=""):
    

    if nombre == "todos":
        nombre=""
    if categoria == "todas":
        categoria=""

    rAux = []
    whole = {}

    categoria = '%' + categoria + '%'
    nombre = '%' + nombre + '%'
    print(categoria,nombre)
    sql_query = """SELECT Agenda.id_servicio, Servicio.nom_servicio, Servicio.mod_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, MIN(Agenda.time_stamp), Servicio.correo_ofrecio
            FROM Agenda
            INNER JOIN Servicio ON Agenda.id_servicio = Servicio.id_servicio AND Agenda.estado=0 AND Servicio.correo_ofrecio <> ? AND Servicio.cat_servicio like ? AND Servicio.nom_servicio like ?
            GROUP BY Agenda.id_servicio, Agenda.estado, Servicio.correo_ofrecio, Servicio.nom_servicio, Servicio.cat_servicio, Servicio.imagen_servicio, Servicio.mod_servicio"""
    sql_params=[correo,categoria,nombre]
    result = god.run_query(sql_query, sql_params)
   
    

        
    if( len(result)==0):
        jaux={
            "id":"1",
            "nombre":"NONE",
            "modalidad":"NONE",
            "categoria":categoria,
            "img_servicio":"https://filesmanager070901.blob.core.windows.net/imagenes/Servicio/ic_servicio.png",
        }
        rAux.append(jaux)

        whole["servicios"] = rAux
        return flask.jsonify(whole), 200

    for i in result:
        jaux={
            "id":i[0],
            "nombre":i[1],
            "modalidad":i[2],
            "categoria":i[3],
            "img_servicio":i[4],
        }
        rAux.append(jaux)

   

    whole["servicios"] = rAux
    
    return flask.jsonify(whole), 200
    
@app.route("/terminarServicio", methods=["POST"])
def terminarServicio():
    json_data = flask.request.json
    id_servicio = json_data['id_servicio']
    id_servicio = int(id_servicio)
    calificacion = json_data['calificacion']
    comentarios = json_data['comentarios']
    estado = json_data['estado']

    s = Sentinel()
    s.init_text()
    analisis = s.analyze_text(str(comentarios))

    sql_query="""UPDATE Servicio SET calificacion = ?, comentarios = ?, analisis = ? WHERE id_servicio = ?"""
    sql_params=[calificacion, comentarios, analisis, id_servicio]

    mensaje, status = god.run_insert(sql_query,sql_params)

    if status != 201:
        print("popo cali")
    sql_query="""UPDATE Agenda SET estado = ? WHERE id_servicio = ?"""
    sql_params=[estado, id_servicio]

    mensaje, status = god.run_insert(sql_query,sql_params)

    if status != 201:
        print("popo estado")
    #Obtener correo del que ofrece
    sql_query="""SELECT * FROM Servicio WHERE id_servicio = ?"""
    sql_params=[id_servicio]
    result = god.run_query(sql_query, sql_params)

    correo_ofrecio=result[0][1]
    correo_agendo=result[0][7]

    sql_query="""UPDATE Usuario SET acceso = 1 WHERE correo = ?"""
    sql_params=[correo_ofrecio]
    mensaje, status = god.run_insert(sql_query,sql_params)

    sql_query="""UPDATE Usuario SET acceso = -1 WHERE correo = ?"""
    sql_params=[correo_agendo]
    mensaje, status = god.run_insert(sql_query,sql_params)

    return flask.jsonify(mensaje), status
