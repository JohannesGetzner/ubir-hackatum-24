from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from engine import ScenarioEngine
from database.session import get_db, init_db
import os
import random

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/hackathon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False  # Disable SQL Alchemy logging
db = SQLAlchemy(app)

# Initialize database tables
init_db()

# Create database session and engine
db_session = next(get_db())
engine = ScenarioEngine(db=db_session)

@app.route('/')
def hello():
    return {'message': 'Hello from Flask!'}

@app.route('/create_and_initialize_scenario', methods=['POST'])
def create_and_initialize_scenario():
    # Generate random numbers for vehicles and customers
    num_vehicles = random.randint(1, 50)
    num_customers = random.randint(1, 200)
    
    try:
        # Create and initialize the scenario using the engine
        scenario = engine.create_scenario(
            num_vehicles=num_vehicles,
            num_customers=num_customers
        )

        engine.initialize_scenario(scenario)
        
        return jsonify({
            'status': 'success',
            'scenario_id': str(scenario.id) if scenario else None,
            'num_vehicles': num_vehicles,
            'num_customers': num_customers
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/launch_scenario/<scenario_id>/<float:speed>', methods=['POST'])
def launch_scenario(scenario_id, speed):
    try:
        # Validate speed parameter
        if speed <= 0 or speed > 1:
            return jsonify({
                'status': 'error',
                'message': 'Speed must be between 0 and 1 (exclusive of 0)'
            }), 400

        # Launch the scenario using the engine
        engine.launch_scenario(scenario_id, speed)
        
        return jsonify({
            'status': 'success',
            'scenario_id': scenario_id,
            'speed': speed
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3333)