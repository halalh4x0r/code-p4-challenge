from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
