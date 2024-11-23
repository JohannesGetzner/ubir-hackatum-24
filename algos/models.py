import math

ASSUMED_SPEED: float = 15.0
assert ASSUMED_SPEED > 0, "the assumed speed must be greater than 0."


class Scenario:
    def __init__(self, vehicles: dict, customers: dict):
        self.vehicles = vehicles
        self.customers = customers
        # Mapping from vehicles ids to ints.
        self.indexed_vehicles = dict(enumerate(vehicles, start=1))
        self.indexed_customers = dict(enumerate(customers, start=1))

    def calculate_cost(self, individual: list[tuple[int, int]]):
        total_distance: float = 0.0
        total_active_time: float = 0.0  # time a taxi is active
        total_waiting_time: float = 0.0  # time a customer is waiting
        for gen in individual:
            # Get vehicle position.
            vehicle = self.indexed_vehicles[gen[0]]
            vehicle_x, vehicle_y = vehicle["coordX"], vehicle["coordY"]

            # Get customer position.
            customer = self.indexed_customers[gen[1]]
            customer_origin_x, customer_origin_y = (
                customer["coordX"],
                customer["coordY"],
            )
            customer_destination_x, customer_destination_y = (
                customer["destinationX"],
                customer["destinationY"],
            )
            # Distance from taxi to customer.
            pickup_distance = Scenario._euclidean_distance(
                vehicle_x, vehicle_y, customer_origin_x, customer_origin_y
            )
            # Distance from customer origin to destination.
            travel_distance = Scenario._euclidean_distance(
                customer_origin_x,
                customer_origin_y,
                customer_destination_x,
                customer_destination_y,
            )
            total_distance += pickup_distance + travel_distance
            # Waiting and active times.
            waiting_time = pickup_distance / ASSUMED_SPEED
            travel_time = travel_distance / ASSUMED_SPEED
            total_active_time += waiting_time + travel_time
            total_waiting_time += waiting_time
        return total_distance, total_active_time, total_waiting_time

    @classmethod
    def _euclidean_distance(cls, x1, y1, x2, y2) -> float:
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
