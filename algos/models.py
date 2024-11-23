import math

ASSUMED_SPEED: float = 4.2
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
            pickup_distance = Scenario._haversine_distance(
                vehicle_x, vehicle_y, customer_origin_x, customer_origin_y
            )
            # Distance from customer origin to destination.
            travel_distance = Scenario._haversine_distance(
                customer_origin_x,
                customer_origin_y,
                customer_destination_x,
                customer_destination_y,
            )
            total_distance += pickup_distance + travel_distance
            # Waiting times.
            waiting_time = pickup_distance / ASSUMED_SPEED
            total_waiting_time += waiting_time
        return total_distance, total_waiting_time

    @classmethod
    def _haversine_distance(cls, lat1, lon1, lat2, lon2) -> float:
        """Calculate the total distance between start point and customer."""
        R = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.

        # Convert to radians.
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

        # Haversine formula.
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        return c * R
