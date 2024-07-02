#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, jsonify,request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db,render_as_batch=True)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants',methods=['GET','DELETE'])
def restaurants():
    if request.method=='GET':
        restaurants=[]
        for restaurant in Restaurant.query.all():
            restaurant_dict={
                "address":restaurant.address,
                "id":restaurant.id,
                "name":restaurant.name
            }
            restaurants.append(restaurant_dict)
            response=make_response(
                jsonify(restaurants),
                200
            )
        return response
    
    elif request.method == 'DELETE':
        restaurant_id = request.args.get('id')

        if not restaurant_id:
            return jsonify({"error": "Missing restaurant ID"}), 400

        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404    

if __name__ == "__main__":
    app.run(port=5555, debug=True)
