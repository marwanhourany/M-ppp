with open('app/config/secret', 'rb') as secret_file:
	SECRET_KEY = secret_file.read()

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False

BASIC_AUTH_USERNAME = "admin"

UPLOAD_FOLDER = "upload"
