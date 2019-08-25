from flask import Flask, json, jsonify, request
import Helper.InputHandler as inp
import modle.response_model as modelRes
import random
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import psycopg2

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address) # config flask limiter with flask app

#connect to data using psycopg2 library
conn = psycopg2.connect("host='localhost' port='5432' dbname='postgres' user='postgres' password='root'")
import sys
import os



if sys.version_info >= (3,):
    import urllib.request as urllib2
    import urllib.parse as urlparse
else:
    import urllib2
    import urlparse
cur = conn.cursor()

cwd = os.getcwd()
fields = ["speed","status","total_size","eta","left_size"]

APIs = {}
APIs['download file'] = "http://127.0.0.1:5000/get_using_postgres?url=https://buildmedia.readthedocs.org/media/pdf/flask-limiter/latest/flask-limiter.pdf"
APIs["check status"] = "http://127.0.0.1:5000/status?id=76667"
APIs['test limiter'] = "http://127.0.0.1:5000/limiter_testing"


@app.route("/")
def home():
    return jsonify(APIs)

@app.route('/get_using_postgres', methods=['GET', 'POST'])
def get_using_postgres():
    error = {"error": "invalid params", "msg": ""}
    try:
        params = request.args;
        err_msg, inputs = inp.getUrlInput(params)
    except Exception as  e:
        #print(e)
        error['msg'] = "please provide valid params"
        return jsonify(error)
    if err_msg:
        error['msg'] = err_msg
        return jsonify(error)
    if "url" in inputs:

        scheme, netloc, path, query, fragment = urlparse.urlsplit(inputs["url"])
        filename = os.path.basename(path)
        if modelRes.fileExist(filename):
            return jsonify({filename:"file already downloaded"})
        else:
            # allocate id to download file
            id = random.randint(1,1000000)
            if modelRes.checkid(id):
                id +=random.randint(10, 10000)

            thread_a = modelRes.Compute(request.__copy__(), inputs["url"], id)
            thread_a.start()
            return jsonify({"file_id":id})


@app.route('/status', methods=["GET"])
def status():
    error = {"error": "invalid params", "msg": ""}
    try:
        params = request.args;
        err_msg, inputs = inp.getid(params) # this used for handling user url
    except Exception as  e:
        error['msg'] = "please provide valid params"
        return jsonify(error)
    if err_msg:
        error['msg'] = err_msg
        return jsonify(error)

    if "id" in inputs:
        response_id = modelRes.status(inputs["id"])

        if len(response_id) !=0:

            return jsonify({"total file size":response_id[0][1], "Downloaded file size":response_id[0][2], "Remaining": response_id[0][3], "status":response_id[0][4]}) # this return status response for id
        else:
            return jsonify({"Error":"Enter valid id"})  # if id not in database

"""
we cam apply limiter to any router
1. configure limiter to app
2. call to limit method and set limit
3. show the limit message through error_message argument
"""
@app.route("/limiter_testing")
@limiter.limit("3 per day", error_message="You Cross the limits 3 per day")
def tester():
    return "this is limiter testing"


if __name__=='__main__':
	app.run(debug = True)


