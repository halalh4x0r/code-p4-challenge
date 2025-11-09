# server/app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize app & DB
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///camp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ========================
# MODELS
# ========================

class Camper(db.Model):
    __tablename__ = 'campers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    signups = db.relationship('Signup', back_populates='camper', cascade="all, delete")

    @property
    def serialize(self):
        return {"id": self.id, "name": self.name, "age": self.age}

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    signups = db.relationship('Signup', back_populates='activity', cascade="all, delete")

    @property
    def serialize(self):
        return {"id": self.id, "name": self.name, "difficulty": self.difficulty}

class Signup(db.Model):
    __tablename__ = 'signups'
    id = db.Column(db.Integer, primary_key=True)
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    time = db.Column(db.Integer, nullable=False)

    camper = db.relationship('Camper', back_populates='signups')
    activity = db.relationship('Activity', back_populates='signups')

    @property
    def serialize(self):
        return {
            "id": self.id,
            "camper_id": self.camper_id,
            "activity_id": self.activity_id,
            "time": self.time,
            "camper": self.camper.serialize,
            "activity": self.activity.serialize
        }

# ========================
# VALIDATIONS
# ========================

def validate_camper(data):
    errors = []
    if not data.get("name"):
        errors.append("name required")
    age = data.get("age")
    if not isinstance(age, int) or not (8 <= age <= 18):
        errors.append("age must be 8-18")
    return errors

def validate_signup(data):
    errors = []
    time = data.get("time")
    if not isinstance(time, int) or not (0 <= time <= 23):
        errors.append("time must be 0-23")
    return errors

# ========================
# ROUTES
# ========================

# --------- CAMPERS ---------
@app.route("/campers", methods=["GET"])
def get_campers():
    campers = [c.serialize for c in Camper.query.all()]
    return jsonify(campers), 200

@app.route("/campers/<int:id>", methods=["GET"])
def get_camper(id):
    camper = Camper.query.get(id)
    if not camper:
        return jsonify({"error": "Camper not found"}), 404
    signups = [s.serialize for s in camper.signups]
    result = camper.serialize
    result["signups"] = signups
    return jsonify(result), 200

@app.route("/campers", methods=["POST"])
def create_camper():
    data = request.get_json()
    errors = validate_camper(data)
    if errors:
        return jsonify({"errors": ["validation errors"]}), 400
    camper = Camper(name=data["name"], age=data["age"])
    db.session.add(camper)
    db.session.commit()
    return jsonify(camper.serialize), 201

@app.route("/campers/<int:id>", methods=["PATCH"])
def update_camper(id):
    camper = Camper.query.get(id)
    if not camper:
        return jsonify({"error": "Camper not found"}), 404
    data = request.get_json()
    updated_name = data.get("name")
    updated_age = data.get("age")
    temp_data = {"name": updated_name or camper.name, "age": updated_age or camper.age}
    errors = validate_camper(temp_data)
    if errors:
        return jsonify({"errors": ["validation errors"]}), 400
    camper.name = updated_name or camper.name
    camper.age = updated_age or camper.age
    db.session.commit()
    return jsonify(camper.serialize), 202

# --------- ACTIVITIES ---------
@app.route("/activities", methods=["GET"])
def get_activities():
    activities = [a.serialize for a in Activity.query.all()]
    return jsonify(activities), 200

@app.route("/activities/<int:id>", methods=["DELETE"])
def delete_activity(id):
    activity = Activity.query.get(id)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    db.session.delete(activity)
    db.session.commit()
    return "", 204

# --------- SIGNUPS ---------
@app.route("/signups", methods=["POST"])
def create_signup():
    data = request.get_json()
    errors = validate_signup(data)
    camper = Camper.query.get(data.get("camper_id"))
    activity = Activity.query.get(data.get("activity_id"))
    if not camper or not activity:
        errors.append("Invalid camper or activity")
    if errors:
        return jsonify({"errors": ["validation errors"]}), 400
    signup = Signup(camper_id=camper.id, activity_id=activity.id, time=data["time"])
    db.session.add(signup)
    db.session.commit()
    return jsonify(signup.serialize), 201

# ========================
# RUN SERVER
# ========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # creates tables automatically
    app.run(port=5555, debug=True)
