from flask_restful import reqparse , Api , Resource , marshal_with , fields
from models import db , user , admin , subject , chapter ,scores , quiz , questions 
from datetime import datetime



class adduser(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email" , type=str , required=True , help="email is required")
        parser.add_argument("name" , type=str , required=True , help="name is required")
        parser.add_argument("passwo" , type=str , required=True , help="password is required")
        parser.add_argument("qual" , type=str , required=True , help="qualification is required")
        parser.add_argument("dat" , type= lambda x: datetime.strptime(x,"%Y-%m-%d").date()  , required=True , help="date is required")
        args = parser.parse_args()
        if user.query.filter_by(username=args["email"]).first():
            return {"message": "User already exists"}, 409
        if admin.query.filter_by(adminname=args["email"]).first():
            return {"message": "User already exists as admins"}, 409
        new_user = user(username = args["email"] ,password = args["passwo"], uname = args["name"] , qualification = args["qual"] , dob = args["dat"])
        db.session.add(new_user)
        db.session.commit()
        return 201
api = Api()
api.add_resource(adduser,"/api/registration")