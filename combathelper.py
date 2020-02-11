import pymongo
from flask import Flask, request , jsonify, abort, make_response
app = Flask(__name__)

myclient = pymongo.MongoClient("mongodb+srv://jawkly:GKJP3QM9M9GeWIFA@cluster0-sj7sy.mongodb.net/test?retryWrites=true&w=majority")
mydb = myclient["Jackson_DB"]


@app.route('/')
def hello():
    return "<h1> my backend!!! </h1>"

# Get all players
@app.route('/player', methods=['GET'])
def get_players():
    mycol = mydb["PC"]
    myresult = mycol.find({}, {"_id": 0, "name": 1})
    return jsonify(myresult)

# Run Server
if __name__ == '__main__':
    app.run(debug=False)