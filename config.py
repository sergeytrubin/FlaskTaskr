import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

USERNAME = 'admin'
PASSWORD = 'admin'
WTF_CSRF_ENABLED = True

# Enable debug mode.
DEBUG = True

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'postgres://dbuser:zubur1@localhost:5432/taskr'
SQLALCHEMY_TRACK_MODIFICATIONS = False