import { DashboardData } from '../types';

// Placeholder for real API calls
// Ensure this environment variable is set in .env or .env.local
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = {
    async getDashboardData(): Promise<DashboardData> {
        try {
            const response = await fetch(`${API_BASE_URL}/dashboard`, {
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            if (!response.ok) {
                throw new Error(`API call failed: ${response.statusText}`);
            }
            return response.json();
        } catch (error) {
            console.error("API Error:", error);
            throw error;
        }
    },

    async detectAnomaly(payload: any): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/detect_anomaly`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`Anomaly API failed: ${response.statusText}`);
            return response.json();
        } catch (error) {
            console.error("Anomaly API Error:", error);
            throw error;
        }
    },

    async predictServiceDemand(payload: any): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/predict_service_demand`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`Demand API failed: ${response.statusText}`);
            return response.json();
        } catch (error) {
            console.error("Demand API Error:", error);
            throw error;
        }
    }
};
