import os

class Config:
    SECRET_KEY = 'fb11f6814c14dac8b6a38d44819f0b26'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'sunejack1@gmail.com'  # os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = 'sunebari'  # os.environ.get('EMAIL_PASS')
    ELASTICSEARCH_URL = 'http://localhost:9200'  ## os.environ.get('ELASTICSEARCH_URL')
    BOOTSTRAP_SERVE_LOCAL = True
    #FLASK_ADMIN_SWATCH = 'cerulean'
    #WHOOSH_BASE = os.path.join(basedir, 'search.db')
