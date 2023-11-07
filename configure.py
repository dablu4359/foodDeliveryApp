import yaml
from flask_mysqldb import MySQL
def config(app):
    # Configure db
    db = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)
    app.config['MYSQL_HOST'] = db['mysql_host']
    app.config['MYSQL_USER'] = db['mysql_user']
    app.config['MYSQL_PASSWORD'] = db['mysql_password']
    app.config['MYSQL_DB'] = db['mysql_db']
    app.secret_key = 'your secret key'
    return MySQL(app)

