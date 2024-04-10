#!/usr/bin/env python3

from flask import Flask, request, make_response,jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes')
def get_all_heroes():
    heroes = Hero.query.all()
    if heroes:
        return jsonify([hero.to_dict() for hero in heroes]), 200
    else:
        return jsonify([]), 200

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_details(id):
    hero = Hero.query.get(id)
    if hero:
        return make_response(hero.to_dict(), 200)
    else:
        return make_response({"error": "Hero not found"}, 404)

@app.route('/powers')
def get_all_powers():
    powers = Power.query.all()
    if powers:
        return jsonify([power.to_dict() for power in powers]), 200
    else:
        return jsonify([]), 200

@app.route('/powers/<int:id>', methods=['GET'])
def get_power_details(id):
    
    power = Power.query.get(id)
    if power:
        return jsonify(power.to_dict()), 200
    else:
        return jsonify({"error": "Power not found"}), 404

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power_details(id):
    power = Power.query.get(id)
    if power:
        data = request.get_json()
        new_description = data.get('description')
        if new_description:
            power.description = new_description
            try:
                db.session.commit()
                return jsonify(power.to_dict()), 200
            except Exception as e:
                return jsonify({"errors": [str(e)]}), 400
        else:
            return jsonify({"error": "Invalid request"}), 400
    else:
        return jsonify({"error": "Power not found"}), 404

@app.route('/hero_powers', methods=['POST'])
def create_hero_power_association():
    data = request.get_json()
    strength = data.get('strength')
    power_id = data.get('power_id')
    hero_id = data.get('hero_id')
    if not all([strength, power_id, hero_id]):
        return jsonify({"errors": ["Missing required fields"]}), 400
    if strength not in ['Strong', 'Weak', 'Average']:
        return jsonify({"errors": ["Validation errors"]}), 400
    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)
    if not hero or not power:
        return jsonify({"errors": ["Hero or Power not found"]}), 404
    hero_power = HeroPower(strength=strength, hero=hero, power=power)
    try:
        db.session.add(hero_power)
        db.session.commit()
        response_data = {
            "id": hero_power.id,
            "hero_id": hero_power.hero_id,
            "power_id": hero_power.power_id,
            "strength": hero_power.strength,
            "hero": hero.to_dict(),
            "power": power.to_dict()
        }
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
