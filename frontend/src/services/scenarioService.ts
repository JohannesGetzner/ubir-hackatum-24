import axios from 'axios';

const API_BASE_URL = 'http://localhost:3333';

export interface ScenarioResponse {
    status: string;
    scenario_id: string;
    start_time?: string;
    end_time?: string;
    num_customers?: number;
    num_vehicles?: number;
    savings_km_genetic?: number;
    savings_km_greedy?: number;
    savings_time_genetic?: number;
    savings_time_greedy?: number;
    utilization: number;
    efficiency: number;
}

export const getCurrentScenario = async (scenario_id?: string): Promise<ScenarioResponse> => {
    try {
        const url = scenario_id 
            ? `${API_BASE_URL}/current_scenario?scenario_id=${scenario_id}`
            : `${API_BASE_URL}/current_scenario`;
        const response = await axios.get<ScenarioResponse>(url);
        return response.data;
    } catch (error) {
        console.error('Error fetching current scenario:', error);
        throw error;
    }
};

export const getAllScenarios = async (): Promise<ScenarioResponse[]> => {
    try {
        const response = await axios.get<{ scenarios: ScenarioResponse[] }>(`${API_BASE_URL}/scenarios`);
        return response.data.scenarios;
    } catch (error) {
        console.error('Error fetching scenarios:', error);
        throw error;
    }
};

export const runScenario = async (numCustomers: number = 10, numVehicles: number = 5, breakdownRate: number = 0.1): Promise<ScenarioResponse> => {
    try {
        const response = await axios.post<ScenarioResponse>(
            `${API_BASE_URL}/run_scenario/${numCustomers}/${numVehicles}/${breakdownRate}`
        );
        return response.data;
    } catch (error) {
        console.error('Error running scenario:', error);
        throw error;
    }
};
