#!flask/bin/python
import pymongo
from flask import Flask, request , jsonify, abort, make_response, render_template
from flask_pymongo import PyMongo
import json
from bson import json_util
from urllib.parse import unquote_plus
from random import randint

app = Flask(__name__)
client = pymongo.MongoClient("mongodb+srv://jawkly:jawklypassword@cluster0-sj7sy.mongodb.net/test?retryWrites=true&w=majority")
db = client["Jackson_DB"]

@app.route('/')
def index():
    return "hello"
    
@app.route('/player', methods=['POST'])
def add_player():
    playercol = db.PC
    name = request.json['name']
    player_id = playercol.insert_one({'name': name})
    return jsonify({'name' : name})

@app.route('/player', methods=['GET'])
def get_players():
    playercol = db.PC
    mylist = []
    for x in playercol.find():
        mylist.append({'name' : x['name']})
    return  json.dumps(mylist)

@app.route("/player/<name>", methods=["DELETE"])
def delete_player(name):
    name = unquote_plus(name)
    playercol = db.PC
    myquery = { "name": name }
    playercol.delete_one(myquery)
    return jsonify(myquery)

@app.route('/encounter', methods=['POST'])
def add_encounter():
    enccol = db.Encounter
    name = request.json['name']
    try:
        id = enccol.find().sort("id", -1)[0]["id"] + 1
    except:
        id = 1
    object_id = enccol.insert_one({'name': name, 'id':id})
    return jsonify({'name': name, 'id':id})

@app.route('/encounter', methods=['GET'])
def get_encounters():
    enccol = db.Encounter
    mylist = []
    for x in enccol.find():
        mylist.append({'name' : x['name'], 'id' : x['id']})
    return  json.dumps(mylist)

@app.route('/encounter/<id>', methods=['GET'])
def get_encounter(id):
    enccol = db.Encounter
    myquery = { "id": int(id) }
    res = enccol.find_one(myquery)
    return jsonify({"id":res["id"], "name":res["name"]})

@app.route('/encounter/<id>', methods=['POST'])#only used for edit name for now
def edit_encounter(id):
    enccol = db.Encounter
    name = request.json['name']
    myquery = { "id": int(id) }
    newvalues = { "$set": {"name": name }}
    object_id = enccol.update_one(myquery, newvalues)
    return jsonify({'name': name, 'id':id})

@app.route("/encounter/<id>", methods=["DELETE"])
def delete_encounter(id):
    enccol = db.Encounter
    myquery = { "id": int(id) }
    enccol.delete_one(myquery)
    emcol = db.Encounter_Monster
    myquery = {"encounter_id": int(id)}
    emcol.delete_many(myquery)
    statuscol = db.Status
    myquery = {"encounter_id": int(id)}
    statuscol.delete_many(myquery)
    return jsonify(myquery)#will have to also delete all related encounter_monster files
    
@app.route("/encounter_monster/<encounter_id>", methods=['POST'])
def add_monsters_to_encounter(encounter_id):
    encounter_id = int(encounter_id)
    emcol = db.Encounter_Monster
    try:
        id = emcol.find().sort("id", -1)[0]["id"] + 1
    except:
        id = 1
    monster_id = request.json['monster_id']
    quantity = request.json['quantity']
    try:
        AC = request.json['AC']
    except:
        AC = None
    try:
        HP = request.json['HP']
    except:
        HP = None
    try:
        DEX = request.json['DEX']
    except:
        DEX = None
    try:
        WIS = request.json['WIS']
    except:
        WIS = None
    object_id = emcol.insert_one({'id':id, 'encounter_id': encounter_id, 'monster_id':monster_id, 'quantity':quantity, 'AC':AC, 'HP':HP, 'DEX':DEX, 'WIS':WIS})
    return jsonify({'id':id, 'encounter_id': encounter_id, 'monster_id':monster_id, 'quantity':quantity, 'AC':AC, 'HP':HP, 'DEX':DEX, 'WIS':WIS})

@app.route('/encounter_monster/<encounter_id>', methods=['GET'])
def get_monsters_from_encounter(encounter_id):
    emcol = db.Encounter_Monster
    emquery = { "encounter_id": int(encounter_id) }
    emres = emcol.find(emquery)
    monscol = db.Monster
    mylist = []
    for x in emres:
        monsquery = { "id": x['monster_id'] }
        monster_data = monscol.find_one(monsquery)
        if x['AC'] is None:
            AC = monster_data['AC']
        else:
            AC = x['AC']
        if x['HP'] is None:
            HP = monster_data['HP']
        else:
            HP = x['HP']
        if x['DEX'] is None:
            DEX = monster_data['DEX']
        else:
            DEX = x['DEX']
        if x['WIS'] is None:
            WIS = monster_data['WIS']
        else:
            WIS = x['WIS']
        mylist.append({'id' : x['id'], 'monster_id' : x['monster_id'], 'monster_name' : monster_data['name'], 'quantity' : x['quantity'], 'AC' : AC, 'HP' : HP, 'DEX' : DEX, 'WIS' : WIS})
    return  json.dumps(mylist)

@app.route("/encounter_monster/<id>", methods=["DELETE"])
def delete_encounter_monster(id):
    emcol = db.Encounter_Monster
    myquery = {"id": int(id)}
    emcol.delete_one(myquery)
    return jsonify(myquery)

@app.route('/encounter_import/<id>', methods=['POST'])
def import_from_encounter(id):
    enccol = db.Encounter
    emcol = db.Encounter_Monster
    base_encounter_id = int(id)#id is the base encounter id not the imported one's
    imported_encounter_name = request.json['import_name']
    
    encquery = { "name": imported_encounter_name }
    imported_encounter_id = enccol.find_one(encquery)['id']
    
    emquery = { "encounter_id": int(imported_encounter_id) }
    imported_encounter_monsters = emcol.find(emquery)#all monsters in the imported encounter
    mylist = []
    try:
        id = emcol.find().sort("id", -1)[0]["id"] + 1
    except:
        id = 1
    for x in imported_encounter_monsters:#adding imported monsters
        mylist.append({'id' : id, 'encounter_id' : base_encounter_id, 'monster_id' : x['monster_id'], 'quantity' : x['quantity'], 'AC' : x['AC'], 'HP' : x['HP'], 'DEX' : x['DEX'], 'WIS': x['WIS']})
        id = id + 1
    object_id = emcol.insert_many(mylist)
    return  jsonify({'status':'success'})

@app.route('/monster', methods=['POST'])
def add_monster():
    monscol = db.Monster
    name = request.json['name']
    AC = int(request.json['AC'])
    HP = int(request.json['HP'])
    DEX = int(request.json['DEX'])
    WIS = int(request.json['WIS'])
    try:
        id = monscol.find().sort("id", -1)[0]["id"] + 1
    except:
        id = 1
    monster_id = monscol.insert_one({'id':id, 'name': name, 'AC':AC, 'HP': HP, 'DEX': DEX, 'WIS': WIS})
    return jsonify({'id':id, 'name': name, 'AC':AC, 'HP': HP, 'DEX': DEX, 'WIS': WIS})

@app.route('/monster', methods=['GET'])
def get_monsters():
    monscol = db.Monster
    mylist = []
    for x in monscol.find():
        mylist.append({'id':x['id'], 'name': x['name'], 'AC':x['AC'], 'HP': x['HP'], 'DEX': x['DEX'], 'WIS': x['WIS']})
    return  json.dumps(mylist)

@app.route('/monster/<name>', methods=['GET'])
def get_monster(name):
    name = unquote_plus(name)
    monscol = db.Monster
    myquery = { "name": name }
    res = monscol.find_one(myquery)
    return jsonify({"id":res["id"], "name":res["name"], "AC":res["AC"], "HP":res["HP"], "DEX":res["DEX"], "WIS":res["WIS"]})

@app.route("/monster/<id>", methods=["DELETE"])
def delete_monster(id):
    monscol = db.Monster
    myquery = { "id": int(id) }
    monscol.delete_one(myquery)
    return jsonify(myquery)

@app.route('/run/<encounter_id>', methods=['POST'])#initiates status files containing necessary variables for playing the encounter
def intialize_encounter(encounter_id):
    statuscol = db.Status
    #already checked if there exists status for this encounter on the php side, hence we deal with a new encounter run here
    #add player statuses for all players
    playercol = db.PC
    encounter_id = int(encounter_id)
    try:
        id = statuscol.find().sort("id", -1)[0]["id"] + 1
    except:
        id = 1
    mylist = []
    for x in playercol.find():
        initiative_roll = request.json[x['name']+'_initiative_roll']
        mylist.append({'id' : id, 'encounter_id': encounter_id, 'name' : x['name'], 'initiative_roll': initiative_roll, 'isPlayer':True, 'text':""})
        id = id + 1
    #add monster statuses for all monsters
    emcol = db.Encounter_Monster
    emquery = { "encounter_id": int(encounter_id) }
    emres = emcol.find(emquery)
    monscol = db.Monster
    name_count_dictionary = {}
    
    for x in emres:#where x is a monster bundle of the same type
        monsquery = { "id": x['monster_id'] }
        monster_data = monscol.find_one(monsquery)
        if x['AC'] is None:
            AC = monster_data['AC']
        else:
            AC = x['AC']
        if x['HP'] is None:
            HP = monster_data['HP']
        else:
            HP = x['HP']
        if x['DEX'] is None:
            DEX = monster_data['DEX'] 
        else:
            DEX = x['DEX']
        if x['WIS'] is None:
            WIS = monster_data['WIS']
        else:
            WIS = x['WIS']
        #for each individual monster of that type
        if x['quantity'] is 1 and not monster_data['name'] in name_count_dictionary:
            initiative_roll = randint(1, 21)+DEX
            mylist.append({'id' : id, 'encounter_id' : int(encounter_id), 'name' : monster_data['name'], 'monster_id' : monster_data['id'], 'initiative_roll' : initiative_roll, 'isPlayer': False, 'AC' : AC, 'HP' : HP, 'WIS' : WIS, 'text': ""})  
            id = id + 1
            name_count_dictionary[monster_data['name']] = 1
        else:
            for i in range(x['quantity']):
                initiative_roll = randint(1, 21)+DEX
                if monster_data['name'] in name_count_dictionary:
                    index = name_count_dictionary[monster_data['name']] + 1
                else:
                    index = 1
                name_count_dictionary[monster_data['name']] = index
                mylist.append({'id' : id, 'encounter_id' : int(encounter_id), 'name' : monster_data['name']+" "+str(index), 'monster_id' : monster_data['id'], 'initiative_roll' : initiative_roll, 'isPlayer': False, 'AC' : AC, 'HP' : HP, 'WIS' : WIS, 'text': ""}) 
                id = id + 1

    object_id = statuscol.insert_many(mylist)
    return jsonify({'status':'success'})

@app.route('/play/<encounter_id>', methods=['GET'])#returns all status files for playing the encounter
def play_encounter(encounter_id):
    encounter_id = int(encounter_id)
    statuscol = db.Status
    myquery = { "encounter_id": encounter_id }
    statuslist = statuscol.find(myquery)
    mylist = []
    for x in statuslist:
        if x['isPlayer']:
            mylist.append({'id':x['id'], 'name': x['name'], 'initiative_roll':x['initiative_roll'], 'isPlayer': x['isPlayer'], 'text': x['text']})
        else:
            mylist.append({'id':x['id'], 'name': x['name'], 'initiative_roll':x['initiative_roll'], 'monster_id' : x['monster_id'],'isPlayer': x['isPlayer'], 'text': x['text'], 'AC':x['AC'], 'HP': x['HP'], 'WIS': x['WIS']})
    return  json.dumps(mylist)

@app.route("/status/<encounter_id>", methods=["DELETE"])
def delete_statuses(encounter_id):
    statuscol = db.Status
    myquery = {"encounter_id": int(encounter_id)}
    statuscol.delete_many(myquery)
    return jsonify(myquery)

@app.route('/status/text/<id>', methods=['POST'])#edit text
def edit_status_text(id):
    id = int(id)
    statuscol = db.Status
    text = request.json['newtext']
    myquery = { "id": id }
    newvalues = { "$set": {"text": text }}
    object_id = statuscol.update_one(myquery, newvalues)
    return jsonify(myquery)
    
@app.route('/status/HP/<id>', methods=['POST'])#edit Hp
def edit_status_HP(id):
    id = int(id)
    statuscol = db.Status
    DMG = request.json['DMG']
    myquery = { "id": id }
    res = statuscol.find_one(myquery)
    HP = res['HP'] - int(DMG)
    newvalues = { "$set": {"HP": HP }}
    object_id = statuscol.update_one(myquery, newvalues)
    return jsonify(myquery)

@app.route('/run_import/<base_encounter_id>', methods=['POST'])
def import_from_encounter_during_run(base_encounter_id):
    enccol = db.Encounter
    emcol = db.Encounter_Monster
    monscol = db.Monster
    statuscol = db.Status
    base_encounter_id = int(base_encounter_id)#id is the base encounter id not the imported one's
    imported_encounter_name = request.json['import_name']
    
    encquery = { "name": imported_encounter_name }
    imported_encounter_id = enccol.find_one(encquery)['id']
    
    emquery = { "encounter_id": int(imported_encounter_id) }
    imported_encounter_monsters = emcol.find(emquery)#all monsters in the imported encounter
    mystatuslist = []
    try:
        id = statuscol.find().sort("id", -1)[0]["id"] + 1
    except:
        id = 1
    for em in imported_encounter_monsters:#adding imported monsters
        myquery = {'monster_id':em['monster_id'], 'encounter_id':base_encounter_id}
        naming_index = statuscol.count(myquery) + 1
        myquery = {'id' : em['monster_id']}
        monster_data = monscol.find_one(myquery)
        monster_name = monster_data['name']
        if em['AC'] is None:
            AC = monster_data['AC']
        else:
            AC = em['AC']
        if em['HP'] is None:
            HP = monster_data['HP']
        else:
            HP = em['HP']
        if em['DEX'] is None:
            DEX = monster_data['DEX'] 
        else:
            DEX = em['DEX']
        if em['WIS'] is None:
            WIS = monster_data['WIS']
        else:
            WIS = em['WIS']
        if em['quantity'] is 1 and naming_index is 1:
                name = monster_name
                initiative_roll = randint(1,21) + DEX
                mystatuslist.append({'id' : id, 'encounter_id' : base_encounter_id, 'name' : name, 'monster_id' : em['monster_id'], 'initiative_roll' : initiative_roll, 'isPlayer' : False, 'AC' : AC, 'HP' : HP, 'WIS': WIS, 'text': "Imported"})
                id = id + 1
        else:
            for i in range(em['quantity']):
                name = monster_name + ' ' + str(naming_index)
                initiative_roll = randint(1,21) + DEX
                mystatuslist.append({'id' : id, 'encounter_id' : base_encounter_id, 'name' : name, 'monster_id' : em['monster_id'], 'initiative_roll' : initiative_roll, 'isPlayer' : False, 'AC' : AC, 'HP' : HP, 'WIS': WIS, 'text': "Imported"})
                id = id + 1
                naming_index = naming_index + 1
    object_id = statuscol.insert_many(mystatuslist)
    return  jsonify({'status':'success'})

@app.route("/run_monster/<encounter_id>", methods=['POST'])
def add_monsters_to_run(encounter_id):
    encounter_id = int(encounter_id)
    monscol = db.Monster
    statuscol = db.Status
    try:
        id = emcol.find().sort("id", -1)[0]["id"] + 1
    except:
        id = 1
    monster_id = request.json['monster_id']#php sends id back not monster name
    quantity = request.json['quantity']
    monster_data = monscol.find_one({'id': monster_id})
    try:
        AC = request.json['AC']
    except:
        AC = monster_data['AC']
    try:
        HP = request.json['HP']
    except:
        HP = monster_data['HP']
    try:
        DEX = request.json['DEX']
    except:
        DEX = monster_data['DEX']
    try:
        WIS = request.json['WIS']
    except:
        WIS = monster_data['WIS']
    mystatuslist = []
    myquery = {'monster_id': monster_id, 'encounter_id':encounter_id}
    naming_index = statuscol.count(myquery) + 1
    try:
        id = statuscol.find().sort("id", -1)[0]["id"] + 1
    except:
        id = 1
    if quantity is 1 and naming_index is 1:
        name = monster_data['name']
        initiative_roll = randint(1,21) + DEX
        mystatuslist.append({'id' : id, 'encounter_id' : encounter_id, 'name' : name, 'monster_id' : monster_id, 'initiative_roll' : initiative_roll, 'isPlayer' : False, 'AC' : AC, 'HP' : HP, 'WIS': WIS, 'text': "Added"})
        id = id + 1
    else:
        for i in range(quantity):
            name = monster_data['name'] + ' ' + str(naming_index)
            initiative_roll = randint(1,21) + DEX
            mystatuslist.append({'id' : id, 'encounter_id' : encounter_id, 'name' : name, 'monster_id' : monster_id, 'initiative_roll' : initiative_roll, 'isPlayer' : False, 'AC' : AC, 'HP' : HP, 'WIS': WIS, 'text': "Added"})
            id = id + 1
            naming_index = naming_index + 1
    object_id = statuscol.insert_many(mystatuslist)
   
    return jsonify({"status":"success"})



if __name__ == '__main__':
    app.run(degug=False)

