from flask import Flask, request, make_response
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

#  creating a route that Gets all the heroes
@app.route("/heroes", methods = ["GET"])
def heroes():
    #  creating a list comprehension to get all heroes using the to_dict() method
    heroes_list = [hero.to_dict() for hero in Hero.query.all()]
    #  creating a response
    response = make_response(heroes_list, 200)
    return response

# creating a route that gets the heroes by id
@app.route("/heroes/<int:id>", methods = ["GET"])
def get_hero_by_id(id):
    # querying the table to get the hero by the id
    hero = Hero.query.filter_by(id = id).first()
    if hero:
        # querying the HeroPower model. 
        hero_powers = HeroPower.query.filter_by(hero_id = id).all()
        # creating a dictionary for the hero using the to_dict()
        hero_dict = hero.to_dict()
        # creating a list that will hold the hero powers
        hero_dict["hero_powers"] = [hero_power.to_dict() for hero_power in hero_powers ]
            
        #  creating a response
        response = make_response(hero_dict, 200)
        return response
    else:
        response_body = {
            "error": "Hero not found"
        }
        response = make_response(response_body, 404)

        return response

# creating a route that Gets all powers
@app.route("/powers", methods = ["GET"])
def powers():
    #  creating a list comprehension to get all powers using the to_dict() method
    powers = [power.to_dict() for power in Power.query.all()]
    #  creating a response
    response = make_response(powers, 200)
    return response

# creating a route that gets the powers by id
@app.route("/powers/<int:id>", methods = ["GET", "PATCH"])
def get_powers_by_id(id):
    # querying the Power model and filtering it by the id
    power = Power.query.filter_by(id = id).first()
    if power == None:
        response_body = {
            "error": "Power not found"
        }
        response = make_response(response_body, 404)
        return response
    else:
        if request.method == "GET":
            # creating a dictionary using to_dict() method
            power_dict = power.to_dict()
            # creating a response
            response = make_response(power_dict, 200)
            return response
        elif request.method == "PATCH":
            # getting data from the request
            data = request.get_json()
            # getting the description
            description = data.get("description")
            # checking if the description has a minimum length of 20 characters- if not so then raise an error
            if len(description) < 20:
                response_body = {
                "errors": ["validation errors"]
                }
                response = make_response(response_body, 400)
                return response
            else:
                power.description = description
            # commiting to the database if the power has been updated and throwing an error if it has not been updated
            if power:
                db.session.add(power)
                db.session.commit()
                # creating a dictionary
                power_dict = power.to_dict()

                # creating a response 
                response = make_response(power_dict, 200)
                return response
            else:
                response_body = {
                "errors": ["validation errors"]
                }
                response = make_response(response_body, 400)
                return response


# creating a method that posts the heroes
@app.route("/hero_powers", methods = ["POST"])
def hero_powers():
    # getting data from the request
    data = request.get_json()

    # Giving the acceptable lists of strengths in a dictionary since data will be in json format
    strenghts = {"Strong", "Weak", "Average"}
    #  checking if the strengths exist in the strengths list
    if "strength" not in data or data["strength"] not in strenghts:
        response_body = {
            "errors": ["validation errors"]
            }
        response = make_response(response_body, 400)
        return response
    
    # creating a new hero power instance witn the data provided
    new_power = HeroPower(
        strength =data["strength"],
        power_id=data["power_id"],
        hero_id=data["hero_id"],
    )

    #  validating the new power before adding 
    if new_power:
        # add and commit to the database
        db.session.add(new_power)
        db.session.commit()

        # creating a dictionary
        hero_power_dict = new_power.to_dict()

        # creating a response 
        response = make_response(hero_power_dict, 200)
        return response
    else:
        response_body = {
            "errors": ["validation errors"]
            }
        response = make_response(response_body, 400)
        return response

    
if __name__ == '__main__':
    app.run(port=5555, debug=True)