from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from engine import ScenarioEngine
from database import init_db, get_db
from sqlalchemy.orm import Session
import os
import random
import requests
from models.scenario import Scenario
from dataclasses import asdict
from threading import Thread
from database.repositories import ScenarioRepository

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],  # Add your frontend URLs
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize database
init_db()

# Get database session
def get_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/hackathon.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_ECHO'] = False  # Disable SQL Alchemy logging
db = SQLAlchemy(app)

# Create database session and engine
db_session = next(get_session())
engine = ScenarioEngine(db=db_session)

@app.route('/')
def hello():
    return {'message': 'Hello from Flask!'}

def call_solver(scenario:Scenario):
    request_body = {
        "id": str(scenario.id),
        "startTime": str(scenario.startTime),
        "endTime": str(scenario.endTime),
        "status": scenario.status,
        "vehicles": [asdict(v) for v in scenario.vehicles] if scenario.vehicles else None,
        "customers": [asdict(c) for c in scenario.customers] if scenario.customers else None
    }
    response = requests.post('http://localhost:5001/solve', json=request_body)
    return response.json()

@app.route('/run_scenario/<int:num_customers>/<int:num_vehicles>/<float:speed>', methods=['POST'])
def run_scenario(num_customers:int = 10, num_vehicles:int = 5, speed:float = 0.5):
    if speed <= 0 or speed > 1:
        return jsonify({
            'status': 'error',
            'message': 'Speed must be between 0 and 1 (exclusive of 0)'
        }), 400

    # Step 1: Create scenario
    scenario_dto = engine.create_scenario(
        num_vehicles=num_vehicles,
        num_customers=num_customers
    )

    # Get the database scenario object
    scenario = engine.scenario_repo.get(str(scenario_dto.id))
    if not scenario:
        return jsonify({
            'status': 'error',
            'message': 'Failed to create scenario'
        }), 500

    # Step 2: Initialize scenario
    engine.initialize_scenario(scenario_dto)
    scenario_solution = call_solver(scenario_dto)
    assignments = scenario_solution["genetic"]["allocation"]
    
    # Update scenario with savings rates
    scenario.savings_km_genetic = scenario_solution["saving_rates"]["total_distance"]
    scenario.savings_time_genetic = scenario_solution["saving_rates"]["total_waiting_time"]
    engine.scenario_repo.update(scenario)
    
    # Step 3: Launch scenario in background
    def run_background():
        engine.launch_scenario(str(scenario.scenario_id), speed)
        engine.run_scenario(str(scenario.scenario_id), assignments)
        engine.scenario_repo.finish(scenario.scenario_id)
    
    Thread(target=run_background).start()

    return jsonify({
        'status': 'success',
        'scenario_id': str(scenario.scenario_id)
    })


@app.route('/map_state/', methods=['GET'])
def get_map_state():
    scenario_id = request.args.get('scenario_id')
    if not scenario_id:
        return jsonify({
            'status': 'empty',
            'scenario_id': "",
            'vehicles': [],
            'customers': []
        })
    try:
        # Get all vehicles and customers for the scenario
        vehicles = engine.vehicle_repo.get_by_scenario(scenario_id)
        customers = engine.customer_repo.get_by_scenario(scenario_id)
        
        return jsonify({
            'status': 'success',
            'scenario_id': scenario_id,
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
        scenario_id = request.args.get('scenario_id')
        if not scenario_id:
            return jsonify({'error': 'scenario_id is required'}), 400

        db = next(get_session())
        scenario_repository = ScenarioRepository(db)
        scenario = scenario_repository.get(scenario_id)
        
        if not scenario:
            return jsonify({'error': 'Scenario not found'}), 404

        return jsonify(scenario.to_dict())
    except Exception as e:
        app.logger.error(f"Error fetching current scenario: {str(e)}")
        return jsonify({'error': 'Failed to fetch current scenario'}), 500

@app.route('/scenarios', methods=['GET'])
def get_all_scenarios():
    try:
        db = next(get_session())
        scenario_repository = ScenarioRepository(db)
        scenarios = scenario_repository.get_all()
        return jsonify({
            'scenarios': [scenario.to_dict() for scenario in scenarios]
        })
    except Exception as e:
        app.logger.error(f"Error fetching scenarios: {str(e)}")
        return jsonify({'error': 'Failed to fetch scenarios'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3333)