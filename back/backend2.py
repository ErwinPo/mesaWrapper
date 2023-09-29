import flask
from flask.json import jsonify
import uuid
from robot import Floor
from robot import Bot
from robot import Trash
from robot import Incinerador
games = {}

app = flask.Flask(__name__)

@app.route("/games", methods=["POST"])
def create():
    global games
    id = str(uuid.uuid4())
    model = games[id] = Floor()
    bots = []
    trash = []
    incinerador = []
    for ghost in model.schedule.agents:
        if isinstance(ghost, Bot):
            bots.append({"id": int(ghost.unique_id), "x": ghost.pos[0], "z": ghost.pos[1], "type": "bot"})
        elif isinstance(ghost, Trash):
            trash.append({"id": int(ghost.unique_id), "x": ghost.pos[0], "z": ghost.pos[1],  "type": "trash"})
        elif isinstance(ghost, Incinerador):
            incinerador.append({"id": int(ghost.unique_id), "x": ghost.pos[0], "z": ghost.pos[1],  "type": "incinerador"})
    return jsonify({"bots": bots, "trash": trash, "incinerador": incinerador, 'location': f"/games/{id}"}) , 201, {'location': f"/games/{id}"}

@app.route("/games/<id>", methods=["GET"])
def queryState(id):
    global model
    model = games[id]
    model.step()
    bots = []
    trash = []
    incinerador = []
    for ghost in model.schedule.agents:
        if isinstance(ghost, Bot):
            bots.append({"id": int(ghost.unique_id), "x": ghost.pos[0], "z": ghost.pos[1], "type": "bot"})
        elif isinstance(ghost, Trash):
            trash.append({"id": int(ghost.unique_id), "x": ghost.pos[0], "z": ghost.pos[1],  "type": "trash"})
        elif isinstance(ghost, Incinerador):
            incinerador.append({"id": int(ghost.unique_id), "x": ghost.pos[0], "z": ghost.pos[1],  "type": "incinerador"})
    return jsonify({"bots": bots, "trash": trash, "incinerador": incinerador})
app.run()