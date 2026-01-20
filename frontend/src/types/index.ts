export type Status = "idle" | "loading" | "success" | "error";

export type Trend = "up" | "down" | "neutral";

export interface KPI {
    id: string;
    label: string;
    value: number;
    unit?: string;
    trend: Trend;
    delta: number; // percentage
    confidence?: number; // 0-1
    isAnomaly?: boolean;
}

export interface ChartDataPoint {
    date: string;
    value: number;
    baseline?: number;
    [key: string]: string | number | undefined;
}

export interface Anomaly {
    id: string;
    metric: string;
    detectedAt: string;
    severity: "low" | "medium" | "high";
    description: string;
    acknowledged: boolean;
}

export interface DashboardData {
    kpis: KPI[];
    trends: ChartDataPoint[];
    anomalies: Anomaly[];
    lastUpdated: string;
}
