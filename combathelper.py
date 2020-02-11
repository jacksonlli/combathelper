import mysql.connector
from flask import Flask, request , jsonify, abort, make_response
app = Flask(__name__)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="w4m973fy4u",
  database="game1"
)

@app.route('/')
def hello():
    return "<h1> my backend!!! </h1>"

# Get all players
@app.route('/player', methods=['GET'])
def get_players():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id, name FROM player")
   # myresult = list(mycursor.fetchall())

    myresult = [{'id':row[0], 'name':row[1]} for row in mycursor.fetchall()]


    return jsonify(myresult)
