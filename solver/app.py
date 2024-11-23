from flask import Flask, jsonify, request

from algos import solver

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Fast and Neat Robotaxi Commissioning API"


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json()

    # Extract vehicles and customers from the request
    vehicles = data.get("vehicles", [])
    customers = data.get("customers", [])

    # Call the solver function
    solution = solver.solve(vehicles, customers)

    return jsonify(solution)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
