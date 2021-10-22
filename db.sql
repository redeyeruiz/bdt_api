    
    -- TABLAS COMPLEMENTARIAS
    
    CREATE TABLE Categoria( nombre          VARCHAR(50)     NOT NULL,
                            descripcion     VARCHAR(250)    NOT NULL,
                            PRIMARY KEY(nombre));
                        

    CREATE TABLE Tipo_Archivo(  nombre          VARCHAR(50)     NOT NULL,
                                descripcion     VARCHAR(250)    NOT NULL,
                                PRIMARY KEY(nombre));
    

    -- TABLAS PRINCIPALES
    
    
    CREATE TABLE Usuario(   correo          VARCHAR(50)     NOT NULL,
                            contrasena      VARCHAR(500)    NOT NULL,
                            salt            BINARY(16)      NOT NULL,
                            nombre          VARCHAR(100)    NOT NULL,
                            edad            INT             NOT NULL,
                            municipio       VARCHAR(50)     NOT NULL,
                            colonia         VARCHAR(50)     NOT NULL,
                            genero          VARCHAR(50)     NOT NULL,
                            celular         VARCHAR(50)     NOT NULL,
                            validado        BIT             NOT NULL,
                            bloqueado       BIT             NOT NULL,
                            --correo_v        BIT             NOT NULL,
                            acceso          INT             NOT NULL,
                            codigo          VARCHAR(4),
                            imagen1         VARCHAR(500),
                            imagen2         VARCHAR(500),
                            imagen3         VARCHAR(500),
                            imagen4         VARCHAR(500),
                            PRIMARY KEY(correo));

    CREATE TABLE Administrador( correo          VARCHAR(50)     NOT NULL,
                                contrasena      VARCHAR(500)    NOT NULL,
                                salt            BINARY(16)      NOT NULL,
                                nombre          VARCHAR(100)    NOT NULL,
                                id              INT             NOT NULL IDENTITY,
                                PRIMARY KEY(id));


    CREATE TABLE Archivo(   correo_usuario  VARCHAR(50)     NOT NULL,
                            tipo            VARCHAR(50)     NOT NULL,
                            link            VARCHAR(300),
                            estado          INT             NOT NULL,
                            comentarios     VARCHAR(300)    NOT NULL,
                            FOREIGN KEY (correo_usuario)    REFERENCES Usuario(correo),
                            FOREIGN KEY (tipo)              REFERENCES Tipo_Archivo(nombre),
                            PRIMARY KEY(correo_usuario, tipo));

    CREATE TABLE Servicio(  id_servicio     INT             NOT NULL IDENTITY,
                            correo_ofrecio  VARCHAR(50)     NOT NULL,
                            nom_servicio    VARCHAR(50)     NOT NULL,
                            des_servicio    VARCHAR(100)    NOT NULL,
                            cat_servicio    VARCHAR(50)     NOT NULL,
                            mod_servicio    VARCHAR(50)     NOT NULL,
                            imagen_servicio VARCHAR(500),
                            correo_agendo   VARCHAR(50),
                            longitud        VARCHAR(100),
                            latitud         VARCHAR(100),
                            calificacion    INT,
                            comentarios     VARCHAR(300),
                            analisis        VARCHAR(20), -- Sentiment analysis
                            UNIQUE(id_servicio),
                            FOREIGN KEY (correo_ofrecio)    REFERENCES Usuario(correo),
                            FOREIGN KEY (correo_agendo)     REFERENCES Usuario(correo),
                            FOREIGN KEY (cat_servicio)      REFERENCES Categoria(nombre),
                            PRIMARY KEY(id_servicio));

    CREATE TABLE Agenda(    id_servicio     INT             NOT NULL,
                            time_stamp      VARCHAR(50)     NOT NULL,
                            estado          INT             NOT NULL,
                            FOREIGN KEY (id_servicio)       REFERENCES Servicio(id_servicio),
                            PRIMARY KEY(id_servicio, time_stamp, estado));

    CREATE TABLE Preusuario(    correo          VARCHAR(50)     NOT NULL,
                                codigo          VARCHAR(4)      NOT NULL,
                                PRIMARY KEY(correo));

    
INSERT INTO Categoria (nombre, descripcion) VALUES ('Educación', 'Disfruta de ayudas para tus tareas, asesorías, e-learning y mucho más')
INSERT INTO Categoria (nombre, descripcion) VALUES ('Limpieza', '¿Necesitas ayuda para lavar tu patio? ¿No tienes quien te lave tu ropa? Limpieza a la orden.')
INSERT INTO Categoria (nombre, descripcion) VALUES ('Jardinería', '¿Cuanto llevas sin regar las plantas? ¿Necesitas ayuda con tu jardí? Jardinería a la orden.')

INSERT INTO Tipo_Archivo(nombre, descripcion) VALUES ('INE', '--desc--');

INSERT INTO Tipo_Archivo(nombre, descripcion) VALUES ('Carta', '--desc--');

INSERT INTO Tipo_Archivo(nombre, descripcion) VALUES ('Acta', '--desc--');

INSERT INTO Tipo_Archivo(nombre, descripcion) VALUES ('Domicilio', '--desc--');

INSERT INTO Tipo_Archivo(nombre, descripcion) VALUES ('CURP', '--desc--');


DROP TABLE [dbo].[Agenda]
DROP TABLE [dbo].[Administrador]
DROP TABLE [dbo].[Archivo]
DROP TABLE [dbo].[Tipo_Archivo]
DROP TABLE [dbo].[Servicio]
DROP TABLE [dbo].[Usuario]
DROP TABLE [dbo].[Categoria]
DROP TABLE [dbo].[Preusuario]