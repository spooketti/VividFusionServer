from init import db, app
from werkzeug.security import check_password_hash,generate_password_hash

class Posts(db.Model):
    userID = db.Column(db.Integer,db.ForeignKey('users.id'))
    id = db.Column(db.Integer,primary_key=True)
    caption = db.Column(db.Text)
    image = db.Column(db.Text)
    date = db.Column(db.Text)
    user = db.relationship('Users', backref=db.backref('posts'))
    """
    def update(self, newImg ,caption, username,pfp):
        if not check_password_hash(self.password, oldPW):
            return "Password does not match"
        
        if not newPW.isspace() and newPW != "":
            self.password = generate_password_hash(newPW,method='sha256')
        
        if not name.isspace() and name != "":
            self.name = name
        
        if not username.isspace() and username != "":
            self.username = username
        
        if not pfp.isspace() and pfp != "":
            self.pfp = pfp
            
        db.session.commit()
        
        return "Success"
    """
    
def initPostTable():
    with app.app_context():
        db.create_all()
    
