from config.db import app, db, ma 

class Category(db.Model):
    __tablename__ = "tblcategory"

    id = db.Column(db.Integer, primary_key = True)
    namecategory = db.Column(db.String(50))

    def __init__(self,namecategory , email):
        self.namecategory = namecategory
        self.email = email

with app.app_context():
    db.create_all()

class UsersSchema(ma.Schema):
    class Meta:
        fields =('id' ,'namecategory')