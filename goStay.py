from pymongo import MongoClient
from flask import Flask, render_template ,jsonify ,request
from flask_restful import Resource ,Api
from store import mongoprep


app  = Flask(__name__)
api = Api(app)

print(mongoprep.initiatedb())

#Creating restful_apis
class Nofilter(Resource):
    def get(self, limit): 
        out = mongoprep.getallrec(limit)
        return jsonify({"result":out})
        
class Customquery(Resource):
    def post(self,limit):
       attr = request.get_json()
       #Parsing the attrinutes
       if('bhk' in attr and 'area' in attr):
           out = mongoprep.bhkareafiler(str(attr['area']),str(attr['bhk']),str(attr['sort']),int(attr['limit']))
           return jsonify({"result":out})
       elif ('bhk' not in attr):
           out = mongoprep.bhkareafiler(str(attr['area']),None,str(attr['sort']),int(attr['limit']))
           return jsonify({"result":out})
       else:
           return("Some problem with filters.. Try again")    



@app.route("/flasked")
def trial():
    pass


api.add_resource(Nofilter,'/<string:limit>')
api.add_resource(Customquery,'/query/<string:limit>')

if __name__ == "__main__":
    app.run(debug=True)
   

