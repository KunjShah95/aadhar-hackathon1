import { useState, useEffect } from 'react';
import { DashboardData, Status } from '../types';

const MOCK_DATA: DashboardData = {
    kpis: [
        { id: '1', label: 'Total Enrolments', value: 1350000000, trend: 'up', delta: 0.8, confidence: 0.99 },
        { id: '2', label: 'Auth Transactions', value: 85000000, unit: '/day', trend: 'up', delta: 12.5, confidence: 0.95 },
        { id: '3', label: 'e-KYC Success', value: 92.4, unit: '%', trend: 'down', delta: -0.5, isAnomaly: true },
        { id: '4', label: 'Update Requests', value: 450000, unit: '/day', trend: 'neutral', delta: 0.1 },
    ],
    trends: Array.from({ length: 30 }, (_, i) => ({
        date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        value: 100 + Math.random() * 20 + i,
        baseline: 100 + i * 0.5,
    })),
    anomalies: [
        { id: 'a1', metric: 'e-KYC Success', detectedAt: new Date().toISOString(), severity: 'medium', description: 'Drop in success rate detected in North region', acknowledged: false },
    ],
    lastUpdated: new Date().toISOString(),
};

export function useDashboardData() {
    const [data, setData] = useState<DashboardData | null>(null);
    const [status, setStatus] = useState<Status>('idle');

    useEffect(() => {
        // Initial load
        const load = async () => {
            setStatus('loading');
            await new Promise(resolve => setTimeout(resolve, 800)); // Faster initial load
            setData(MOCK_DATA);
            setStatus('success');
        }
        load();

        // Simulate real-time updates
        const interval = setInterval(() => {
            setData(prev => {
                if (!prev) return null;
                return {
                    ...prev,
                    kpis: prev.kpis.map(kpi => {
                        // Randomly update some KPIs
                        if (Math.random() > 0.7) {
                            const change = (Math.random() - 0.5) * (kpi.value as number) * 0.001; // Small variations
                            return { ...kpi, value: (kpi.value as number) + change };
                        }
                        return kpi;
                    }),
                    trends: [...prev.trends.slice(1), {
                        date: new Date().toISOString(),
                        value: prev.trends[prev.trends.length - 1].value + (Math.random() - 0.5) * 5,
                        baseline: prev.trends[prev.trends.length - 1].baseline
                    }],
                    lastUpdated: new Date().toISOString()
                };
            });
        }, 3000); // Update every 3 seconds

        return () => clearInterval(interval);
    }, []);

    return { data, status };
}
