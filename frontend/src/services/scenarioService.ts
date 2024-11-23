import axios from 'axios';

const API_BASE_URL = 'http://localhost:3333';

export interface ScenarioResponse {
    status: string;
    scenario_id: string;
    utilization: number;
    efficiency: number;
}

export const getCurrentScenario = async (): Promise<ScenarioResponse> => {
    try {
        const response = await axios.get<ScenarioResponse>(`${API_BASE_URL}/current_scenario`);
        return response.data;
    } catch (error) {
        console.error('Error fetching current scenario:', error);
        throw error;
    }
};
