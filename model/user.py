from init import db, app

class Users(db.Model):
    userID = db.Column(db.Text, unique=True)
    id = db.Column(db.Integer,primary_key=True)
    password = db.Column(db.Text)
    name = db.Column(db.Text)
    username = db.Column(db.Text)
    role = db.Column(db.Text)
    
def initUserTable():
    with app.app_context():
        db.create_all()
    