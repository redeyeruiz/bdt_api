import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import asyncio

# TODO
# Make mail async

class Dove:
    def __init__(self):
        self.__key = "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"

    def send_code_signup(self, to_email, user_name, code):
        code = code[0] + " " + code[1] + " " + code[2] + " " + code[3]
        message = Mail(
        from_email='soporte.tulio@outlook.com',
        to_emails=to_email)
        message.dynamic_template_data = {
            "Sender_Name": "Soporte Tulio MX",
            "Sender_Address" : "Dirección X",
            "Sender_City" : "Toluca",
            "Sender_State": "Edo. de México",
            "Sender_Zip": "50120",
            "user_name": user_name,
            "code": code
        }
        message.template_id = 'd-7f41450e233a4bc4b13cd3a305c885c9'
        try:
            sendgrid_client = SendGridAPIClient(self.__key)
            response = sendgrid_client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)
        pass
    
    def send_file_confirm(self, to_email, user_name, file_type, file_url):
        message = Mail(
        from_email='soporte.tulio@outlook.com',
        to_emails=to_email)
        message.dynamic_template_data = {
            "Sender_Name": "Soporte Tulio MX",
            "Sender_Address" : "Dirección X",
            "Sender_City" : "Toluca",
            "Sender_State": "Edo. de México",
            "Sender_Zip": "50120",
            "user_name": user_name,
            "type": file_type,
        }
        message.template_id = 'd-7f41450e233a4bc4b13cd3a305c885c9'
        try:
            sendgrid_client = SendGridAPIClient(self.__key)
            response = sendgrid_client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)

    def send_code_password(self, to_email, user_name, code):
        code = code[0] + " " + code[1] + " " + code[2] + " " + code[3]
        message = Mail(
        from_email='soporte.tulio@outlook.com',
        to_emails=to_email)
        message.dynamic_template_data = {
            "Sender_Name": "Soporte Tulio MX",
            "Sender_Address" : "Dirección X",
            "Sender_City" : "Toluca",
            "Sender_State": "Edo. de México",
            "Sender_Zip": "50120",
            "user_name": user_name,
            "code": code
        }
        message.template_id = 'd-7c4c20ccb32c4b57b7e7e65e166f2455'
        try:
            sendgrid_client = SendGridAPIClient(self.__key)
            response = sendgrid_client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)

    
    def send_bad_file_message(self, to_email, user_name, message_admin, fyle_type):
        message = Mail(
        from_email='soporte.tulio@outlook.com',
        to_emails=to_email)
        message.dynamic_template_data = {
            "Sender_Name": "Soporte Tulio MX",
            "Sender_Address" : "Dirección X",
            "Sender_City" : "Toluca",
            "Sender_State": "Edo. de México",
            "Sender_Zip": "50120",
            "user_name": user_name,
            "message_admin": message_admin,
            "file_type":fyle_type
        }
        message.template_id = 'd-d14f24ebd62945e4bfacd0f66243415e'
        try:
            sendgrid_client = SendGridAPIClient('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')
            response = sendgrid_client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.body)

    
    def send_good_file_message(self, to_email, user_name):
        message = Mail(
        from_email='soporte.tulio@outlook.com',
        to_emails=to_email)
        message.dynamic_template_data = {
            "Sender_Name": "Soporte Tulio MX",
            "Sender_Address" : "Dirección X",
            "Sender_City" : "Toluca",
            "Sender_State": "Edo. de México",
            "Sender_Zip": "50120",
            "user_name": user_name,
        }
        message.template_id = 'd-267e9aba285b43e8990c11adb42c377c'
        try:
            sendgrid_client = SendGridAPIClient(self.__key)
            response = sendgrid_client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)
        pass
    
    def send_confirm_ofrecio(self, to_email, user_name, cliente, fecha_hora, map_url, mod, image_url, celular):
        message = Mail(
        from_email='soporte.tulio@outlook.com',
        to_emails=to_email)
        message.dynamic_template_data = {
            "Sender_Name": "Soporte Tulio MX",
            "Sender_Address" : "Dirección X",
            "Sender_City" : "Toluca",
            "Sender_State": "Edo. de México",
            "Sender_Zip": "50120",
            "user_name": user_name,
            "cliente": cliente,
            "fecha_hora": fecha_hora,
            "map": map_url,
            "mod":mod,
            "imageURI": image_url,
            "celular" : celular,
        }
        message.template_id = 'd-5ff1fc3dc9544d28ae9f349a11f36a81'
        try:
            sendgrid_client = SendGridAPIClient(self.__key)
            response = sendgrid_client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)


    def send_confirm_agendo(self, to_email, user_name, usuario, fecha_hora, map_url, mod, image_url, celular):
        message = Mail(
        from_email='soporte.tulio@outlook.com',
        to_emails=to_email,)
        message.dynamic_template_data = {
            "Sender_Name": "Soporte Tulio MX",
            "Sender_Address" : "Dirección X",
            "Sender_City" : "Toluca",
            "Sender_State": "Edo. de México",
            "Sender_Zip": "50120",
            "user_name": user_name,
            "usuario": usuario,
            "fecha_hora": fecha_hora,
            "map": map_url,
            "mod":mod,
            "imageURI": image_url,
            "celular" : celular,
        }
        message.template_id = 'd-e21c73f24f6e4e588f2dcbb7b4d7ed32'
        try:
            sendgrid_client = SendGridAPIClient(self.__key)
            response = sendgrid_client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.body)

d = Dove()
d.send_bad_file_message('george.flores@tec.mx', 'jj', 'bad', 'INE')