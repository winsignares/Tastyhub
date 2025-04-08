from config.db import app, db, ma 

class Category(db.Model):
    __tablename__ = "tbltaks"

    id = db.Column(db.Integer, primary_key = True)
    nametaks = db.Column(db.String(50))
    id_user_fk = db.Column(db.Integer , db.ForeignKey('tblsusers.id'))
    id_category_fk = db.Column(db.Integer , db.ForeignKey('tblcategory.id'))

    def __init__(self, nametaks , id_user_fk , id_category_fk ):
        self.nametaks = nametaks
        self.id_user_fk = id_user_fk
        id_category_fk = id_category_fk


with app.app_context():
    db.create_all()

class UsersSchema(ma.Schema):
    class Meta:
        fields =('id' ,'nametask' ,'id_user_fk', 'id_caqtegory_fk')