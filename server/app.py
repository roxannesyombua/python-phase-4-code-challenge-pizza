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
    
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    restaurant_data = {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [{
            "id": rp.id,
            "pizza": {
                "id": rp.pizza.id,
                "name": rp.pizza.name,
                "ingredients": rp.pizza.ingredients
            },
            "pizza_id": rp.pizza_id,
            "price": rp.price,
            "restaurant_id": rp.restaurant_id
        } for rp in restaurant.restaurant_pizzas]
    }

    return jsonify(restaurant_data), 200

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    try:
       
        for rp in restaurant.restaurant_pizzas:
            db.session.delete(rp)

        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_list = [{
        "id": pizza.id,
        "name": pizza.name,
        "ingredients": pizza.ingredients
    } for pizza in pizzas]
    return jsonify(pizzas_list), 200



@app.route('/restaurant_pizzas', methods=['GET','POST'])
def create_restaurant_pizza():
    if request.method == 'GET':
        restauraunt_pizzas = []
        if restauraunt_pizzas is None:
            return jsonify({"error": "rest not found"}),404
        
        for rest_pizz in RestaurantPizza.query.all():
            rest_pizza_dict = rest_pizz.to_dict()
            restauraunt_pizzas.append(rest_pizza_dict)
        response = make_response(
                restauraunt_pizzas, 200
            )
        return response
    elif request.method == 'POST':
    
        try:
            
            new_restaurant_pizza = RestaurantPizza(
                price = request.get_json()['price'],
                pizza_id = request.get_json()['pizza_id'],
                restaurant_id = request.get_json()['restaurant_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()

            # Prepare response data
            response = make_response(new_restaurant_pizza.to_dict(), 201, {"Content-Type":"application/json"})

            return response
        except ValueError:
            message = {"errors": [f'validation errors']}
            response = make_response(message, 400)
            return response
  
    
if __name__ == "__main__":
    app.run(port=5555, debug=True)
