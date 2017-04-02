# #/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, Response, send_from_directory, jsonify
from functools import wraps
import functions as fct
import yaml


app = Flask(__name__)
app.debug = True


with open('param.yml', 'r') as stream:
    try:
        param = yaml.load(stream)
    except yaml.YAMLError as e:
        print(e)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    password = fct.hash(password)
    return username == param['user']['login'] and password == param['user']['password']


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/')
@requires_auth
def accueil():
    return render_template('index.html')


@app.route('/hash/<word>')
def hashword(word):
    hashword = fct.hash(word)
    return hashword


@app.route('/gpx/<path:path>')
def send_gpx(path):
    return send_from_directory('gpx', path)


@app.route('/images/<path:path>')
def send_img(path):
    return send_from_directory('images', path)


@app.route('/get_gpxinfo/<path:path>')
@requires_auth
def get_gpxinfo(path):
    # dev in progress - for test
    gpx_info = fct.gpx_info(path)
    print(gpx_info)
    return jsonify(result=gpx_info)


if __name__ == '__main__':
    app.run()
