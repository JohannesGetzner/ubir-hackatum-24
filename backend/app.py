from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from engine import ScenarioEngine
from database.session import get_db, init_db
import os
import random

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],  # Add your frontend URLs
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

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
current_scenario = "7bcbfecf-0193-4792-b2b9-654163bb321a"

@app.route('/')
def hello():
    return {'message': 'Hello from Flask!'}

@app.route('/create_and_initialize_scenario', methods=['POST'])
def create_and_initialize_scenario():
    # Generate random numbers for vehicles and customers
    num_vehicles = random.randint(15, 30)
    num_customers = random.randint(55, 60)
    
    scenario = engine.create_scenario(
        num_vehicles=num_vehicles,
        num_customers=num_customers
    )

    engine.initialize_scenario(scenario)
    
    return jsonify({
        'status': 'success',
        'scenario': scenario,
        'num_vehicles': num_vehicles,
        'num_customers': num_customers
    })

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

@app.route('/run_scenario/<scenario_id>', methods=['POST'])
def run_scenario(scenario_id):
    global current_scenario
    vehicle_assignments = request.get_json()
    current_scenario = scenario_id
    if not isinstance(vehicle_assignments, dict):
        return jsonify({
            'status': 'error',
            'message': 'Request body must be a JSON object with vehicle IDs as keys and customer ID lists as values'
        }), 400

    # Validate that all values are lists
    for vehicle_id, customer_list in vehicle_assignments.items():
        if not isinstance(customer_list, list):
            return jsonify({
                'status': 'error',
                'message': f'Value for vehicle ID {vehicle_id} must be a list of customer IDs'
            }), 400

    # Run the scenario using the engine
    engine.run_scenario(scenario_id, vehicle_assignments)
    return jsonify({
        'status': 'success',
        'scenario_id': scenario_id,
        'vehicle_assignments': vehicle_assignments
    })

@app.route('/map_state/', methods=['GET'])
def get_map_state():
    if current_scenario == "":
        return jsonify({
            'status': 'empty',
            'scenario_id': "",
            'vehicles': [],
            'customers': []
        })
    try:
        # Get all vehicles and customers for the scenario
        vehicles = engine.vehicle_repo.get_by_scenario(current_scenario)
        customers = engine.customer_repo.get_by_scenario(current_scenario)
        
        return jsonify({
            'status': 'success',
            'scenario_id': current_scenario,
            'vehicles': [v.to_dict() for v in vehicles],
            'customers': [c.to_dict() for c in customers]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/current_scenario', methods=['GET'])
def get_current_scenario():
    try:
        # Get the scenario data from the engine
        #scenario = engine.get_scenario(current_scenario)
        #utilization = engine.calculate_utilization(current_scenario)
        #efficiency = engine.calculate_efficiency(current_scenario)
        
        return jsonify({
            'status': 'success',
            'scenario_id': current_scenario,
            'utilization': 1,
            'efficiency': 0.4
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'scenario_id': '',
            'utilization': 0,
            'efficiency': 0
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3333)