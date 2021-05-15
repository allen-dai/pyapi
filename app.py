from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import pymongo, json, string, random, os, datetime, jwt



app = Flask(__name__)
api = Api(app)
URL = "mongodb://"+os.getenv("DB_URL")+":27017"
client = pymongo.MongoClient(URL)
project = os.getenv("PROJECT")


class Bug(Resource):
        
    def get(self):
        username = request.args.get("username")
        cursor = client[project]["bug"].find({"username":username},{"_id": False})
        
        if cursor.count()==0:
            return 404

        bugs = []
        for bug in cursor:
            bugs.append(bug)
        #bugs array contains all the bug json object
        return bugs, 200


    def post(self):
        username = request.args.get("username")
        data = request.form.to_dict()
        data["bug_id"] = (''.join(random.choice(string.ascii_letters + string.digits) for _ in range(40)))
        data["username"] = username
        client[project]["bug"].insert_one(data)
        return {"message":"succeed"}, 200


    def put(self, bug_id):
        client[project]["bug"].update_one({"bug_id" : bug_id},{"$set" : request.form}) 
        return {"message":"succeed"}, 200

    def delete(self, bug_id):
        client[project]["bug"].delete_one({"bug_id":bug_id})
        return {"message":"succeed"}, 200

class Login(Resource):
    def post(self):
        user = request.form.to_dict()

        try:
            username = user["username"]
            password = user["password"]
            if (len(username) == 0 or len(password) == 0):
                return {"message":"Invalid inputs"}
        except:
            return {"message":"Invalid inputs"}

        cursor = client[project]["user"].find(user)

        if cursor.count()==0:
            return {"message":"Invalid username/password"}, 200
            
        access_token = jwt.encode(
                {"exp": datetime.datetime.utcnow()+datetime.timedelta(minutes=5),
                 "iat": datetime.datetime.utcnow()},
                os.getenv("ACCESS_SECRET"), 
                headers = {"alg": "HS256", "typ": "JWT"},
                algorithm="HS256")

        refresh_token = jwt.encode(
                {"exp": datetime.datetime.utcnow()+datetime.timedelta(days=7),
                 "iat": datetime.datetime.utcnow()},
                os.getenv("REFRESH_SECRET")+user["password"], 
                headers = {"alg": "HS256", "typ": "JWT"},
                algorithm="HS256")

        
        return {"message":"ok", "access":access_token.decode("utf-8"), "refresh":refresh_token.decode("utf-8")}, 200


class RefreshService(Resource):
    def get(self):
        access_token = 1


class Register(Resource):

    def post(self):
        user = request.form.to_dict()
        client[project]["user"].insert_one(user)

        return {"message":"Registered"}, 200


api.add_resource(Bug, "/bug")
api.add_resource(Login, "/login")
api.add_resource(RefreshService, "/refreshservice")
api.add_resource(Register, "/Register")

if __name__ == "__main__":
    app.run(debug=True)
