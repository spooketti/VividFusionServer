from flask import Flask, request, jsonify, make_response, Response
from threading import Thread
from init import app
from flask_sqlalchemy import SQLAlchemy 
from authToken import token_required
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from init import db
from model.user import Users, initUserTable
import datetime



@app.route('/')
def home():
    return "VividFusion's Server"

@app.route('/signup', methods=['POST'])
def signup():  
    data = request.get_json()  
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = Users(userID = data["userID"], password=hashed_password,name = data["name"], username=data["username"],role="Creator") 
    db.session.add(new_user)  
    db.session.commit()    
    return jsonify({'message': 'registeration successfully'})

@app.route('/login', methods=['POST'])  
def login_user(): 
    data = request.get_json()
    loginID = data["userID"]
    loginPW = data["password"]

    user = Users.query.filter_by(userID=loginID).first()   
     
    if check_password_hash(user.password, loginPW):

        token = jwt.encode({'userID' : user.userID, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'], "HS256")
        resp = Response(f"Authentication Successful for {user.userID}")
        resp.set_cookie("jwt", token,
                                max_age=3600,
                                secure=True,
                                httponly=True,
                                path='/',
                                samesite='None'  # This is the key part for cross-site requests

                                # domain="frontend.com"
                                )
        return resp


    return make_response('could not verify',  401, {'Authentication': '"login required"'})


def run():
  app.run(host='0.0.0.0',port=8086)

initUserTable()
run()