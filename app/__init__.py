from flask import Flask

USERS = []  # list of all users
POSTS = []  # list of all posts

app = Flask(__name__)

from app import views
