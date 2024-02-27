from flask import Flask, request, jsonify, make_response, Response
from threading import Thread
from init import app
from flask_sqlalchemy import SQLAlchemy 
from authToken import token_required
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from init import db, cors
from model.user import Users, initUserTable
from model.post import Posts, initPostTable
import time
import datetime
import os
import git

repoDir = os.path.dirname(os.path.abspath(__file__))


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

@app.route("/createPost",methods=["POST"])
@token_required
def createPost(current_user):
    data = request.get_json() 
    post = Posts(userID=current_user.id,caption=data["caption"],image=data["image"],date=str(time.time()))
    db.session.add(post)
    db.session.commit()    
    return "Success"

@app.route('/updateServer', methods=['POST'])
def webhook():
        if request.method == 'POST':
            repo = git.Repo(repoDir)
            origin = repo.remotes.origin
            origin.pull()
            return 'update deployment success', 200
        else:
            return 'Wrong event type', 400

@app.route("/deletePost",methods=["DELETE"])
@token_required
def deletePost(current_user):
    data = request.get_json()
    user = Users.query.filter_by(userID=current_user.userID).first()
    post = Posts.query.get(data["id"])
    if(post.userID == user.userID or user.role == "Admin"):
        db.session.delete(post)
        db.session.commit()
        return "Success"
    return "Fail"
    
@app.route('/getPosts', methods=['GET'])
def get_posts():
    page = request.args.get("page",1,type=int)
    postsPerPage = 5
    posts = Posts.query.paginate(page=page,per_page=postsPerPage)
    post_list = []
    for post in posts.items:
        post_list.append({
            'image': post.image,
            'caption': post.caption,
            'date':post.date,
            'pfp': post.user.pfp,
            'username':post.user.username,
            'userID':post.user.userID
        })
    return jsonify({'posts': post_list, 'has_next': posts.has_next})

"""
@app.route("/editPost",methods=["POST"])
@token_required
def editPost(current_user):
    data = request.get_json()
    user = Users.query.filter_by(userID=current_user.userID).first()
    return user.update(data["oldPW"],data["newPW"],data["name"],data["username"],data["pfp"])
"""

@app.before_request
def before_request():
    # Check if the request came from a specific origin
    allowed_origin = request.headers.get('Origin')
    if allowed_origin in ['http://localhost:4100', 'http://172.27.233.236:3000', 'https://spooketti.github.io']:
        cors._origins = allowed_origin

def run():
  app.run(host='0.0.0.0',port=8086)

initUserTable()
initPostTable()
run()