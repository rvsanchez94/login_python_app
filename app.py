from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
from sqlalchemy import and_, or_, not_
import hashlib 
import uuid
from datetime import datetime

app = Flask(__name__)

CORS(app,supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/automl'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)


ma=Marshmallow(app)

class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(100))
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    password = db.Column(db.String(100))
    uuid = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True))

    def __init__(self,email,firstname,lastname,password,uuid,created_at):
        self.email=email
        self.firstname=firstname
        self.lastname=lastname
        self.password=password
        self.uuid=uuid
        self.created_at=created_at

class UserShema(ma.Schema):
    class Meta:
        fields=('id','email','firstname','lastname','password','uuid','created_at')   

user_shema=UserShema()
users_shema=UserShema(many=True)

@app.route('/get',methods=['GET'])
def get_users():
    all_users = Users.query.all()
    res=users_shema.dump(all_users)
    return jsonify(res)


@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = hashlib.md5(request.json['password'].encode()).hexdigest()
    query = Users.query.filter(and_(Users.email == email, Users.password == password)).first()
     
    if query is None:
        return jsonify({"error":"Unauthorized",
                        "message":'Wrong Credentials',  
                        "status":'failure'}),401

    else:
        return jsonify({
            'user':{
                'email': query.email,
                'firstname': query.firstname,     
                'lastname': query.lastname,   
                'password': query.password,    
                'uuid': query.uuid    
             }, 
            "message":'Successfully Logged In!',
            "status":'successful'
            })




@app.route('/create_user', methods =['GET', 'POST'])
def register():
    msg = ''
    status = ''
    
    regexMail = '/[a-z0-9ñ.]+@+[a-zñ]+.[a-zñ]{2,4}([.][a-zñ]{2,4})+/'
    regexPass = '/^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$/g'


    if request.method == 'POST':
        email = request.json['email']
        firstname = request.json['firstname']
        lastname = request.json['lastname']
        pws = request.json['password']
        
        if not email or not firstname or not lastname or not pws:
            msg = 'Please fill out the form!'
        if email.match(regexMail):
            msg = 'Your email is wrong!'
        password = hashlib.md5(pws.encode()).hexdigest()
        valorUnico = uuid.uuid4()
        created_at = datetime.today().strftime('%Y-%m-%d %H:%M')

        query = Users.query.filter(Users.email==email).first()
        if query is not None:
            msg = 'Account already exists !'
            status = 'failure'
        else:
            user = Users(email=email,firstname=firstname,lastname=lastname,password=password,uuid=valorUnico,created_at=created_at)
            db.session.add(user)
            db.session.commit()
            msg = 'You have successfully registered !'
            status = 'successful'
        return jsonify({"message":msg,"status":status})

if __name__ == "__main__":
    app.run(debug=True)