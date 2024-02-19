from flask import Flask, request, jsonify, make_response, Response
from threading import Thread
from init import app
from flask_sqlalchemy import SQLAlchemy 
from authToken import token_required
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from init import db, cors
from model.user import Users, initUserTable
import datetime



@app.route('/')
def home():
    return "VividFusion's Server"

@app.route('/signup', methods=['POST'])
def signup():  
    data = request.get_json() 
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user = Users(userID = data["userID"], password=hashed_password,name = data["name"], username=data["username"],role="Creator",pfp=data["pfp"]) 
    db.session.add(user)  
    db.session.commit()    
    token = jwt.encode({'userID' : user.userID, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'], algorithm="HS256")
    resp = Response('{"jwt":"'+token+'"}')
    resp.set_cookie("jwt", token,
                                max_age=3600,
                                secure=True,
                                httponly=True,
                                path='/',
                                samesite='None',  # This is the key part for cross-site requests
                                domain="172.27.233.236"
                                )
    return resp

@app.route('/login', methods=['POST'])  
def login_user(): 
    data = request.get_json()
    loginID = data["userID"]
    loginPW = data["password"]

    user = Users.query.filter_by(userID=loginID).first()   
     
    if check_password_hash(user.password, loginPW):

        token = jwt.encode({'userID' : user.userID, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'], algorithm="HS256")
        resp = Response('{"jwt":"'+token+'"}')
        resp.set_cookie("jwt", token,
                                max_age=3600,
                                secure=True,
                                httponly=True,
                                path='/',
                                samesite='None',  # This is the key part for cross-site requests
                                domain="172.27.233.236"
                                )
        return resp


    return make_response('could not verify',  401, {'Authentication': '"login required"'})

@app.route('/checkAuth', methods=['GET'])
@token_required
def checkAuth(current_user):
    
    return jsonify({'pfp': current_user.pfp,
                    'name': current_user.name,
                    "username":current_user.username,
                    "userID":current_user.userID,
                    "role":current_user.role})

@app.route("/updateUser",methods=["POST"])
@token_required
def updateUser(current_user):
    data = request.get_json()
    user = Users.query.filter_by(userID=current_user.userID).first()
    return user.update(data["oldPW"],data["newPW"],data["name"],data["username"],data["pfp"])

@app.before_request
def before_request():
    # Check if the request came from a specific origin
    allowed_origin = request.headers.get('Origin')
    if allowed_origin in ['http://localhost:4100', 'http://172.27.233.236:3000', 'https://spooketti.github.io']:
        cors._origins = allowed_origin

def run():
  app.run(host='0.0.0.0',port=8086)

initUserTable()
run()