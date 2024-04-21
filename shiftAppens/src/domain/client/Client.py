class Client(db.Model):
   __tablename__ = "Client"
   id = db.Column(db.Integer, primary_key=True)
   email = db.Column(Email, unique=True, nullable=False)
   password = db.Column(Password, unique=True, nullable=False)
