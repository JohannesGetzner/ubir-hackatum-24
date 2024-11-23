export interface Vehicle {
    id: string;
    scenario_id: string;
    vehicle_name: string;
    longitude: number;
    latitude: number;
    is_available: boolean;
    current_customer_id: string | null;
    active_time: number;
    distance_travelled: number;
    number_of_trips: number;
    remaining_travel_time: number;
    vehicle_speed: number;
    enroute: 'idle' | 'cust' | 'dest';
}

export interface Customer {
    id: string;
    fake_name: string;
    scenario_id: string;
    longitude: number;
    latitude: number;
    destination_longitude: number;
    destination_latitude: number;
    awaiting_service: boolean;
    picked_up: boolean;
}

export interface MapState {
    status: 'success' | 'error' | 'empty';
    scenario_id: string;
    vehicles: Vehicle[];
    customers: Customer[];
    message?: string;
}

const API_URL = 'http://localhost:3333';

// Keep track of the last known good state
let lastKnownGoodState: MapState | null = null;

export const mapService = {
    /**
     * Fetches the current map state including all vehicles and customers
     * @returns Promise<MapState> The current state of vehicles and customers, or last known good state if request fails
     */
    async getMapState(): Promise<MapState> {
        try {
            const response = await fetch(`${API_URL}/map_state/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data: MapState = await response.json();
            if (data.status === 'success') {
                lastKnownGoodState = data;
            }
            return data;
        } catch (error) {
            console.error('Error fetching map state:', error);
            // Return last known good state if available, otherwise return error state
            if (lastKnownGoodState) {
                return {
                    ...lastKnownGoodState,
                    status: 'error',
                    message: error instanceof Error ? error.message : 'Unknown error occurred'
                };
            }
            return {
                status: 'error',
                scenario_id: '',
                vehicles: [],
                customers: [],
                message: error instanceof Error ? error.message : 'Unknown error occurred'
            };
        }
    },
};
