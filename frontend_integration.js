
// Example: Calling the API from React/JavaScript Frontend

// API Configuration
const API_BASE_URL = 'http://localhost:5000';

// Function 1: Get Model Info
async function getModelInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/model_info`);
        const data = await response.json();
        console.log('Model Info:', data);
        return data;
    } catch (error) {
        console.error('Error fetching model info:', error);
    }
}

// Function 2: Make Single Prediction
async function predictEnrollment(features) {
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(features)
        });

        const data = await response.json();

        if (data.success) {
            console.log('Predicted Enrollment:', data.prediction);
            return data.prediction;
        } else {
            console.error('Prediction failed:', data.error);
        }
    } catch (error) {
        console.error('Error making prediction:', error);
    }
}

// Function 3: Make Batch Predictions
async function predictBatch(featuresArray) {
    try {
        const response = await fetch(`${API_BASE_URL}/predict_batch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(featuresArray)
        });

        const data = await response.json();

        if (data.success) {
            console.log('Batch Predictions:', data.predictions);
            return data.predictions;
        } else {
            console.error('Batch prediction failed:', data.error);
        }
    } catch (error) {
        console.error('Error making batch prediction:', error);
    }
}

// Function 4: Detect Anomaly
async function detectAnomaly(features) {
    try {
        const response = await fetch(`${API_BASE_URL}/detect_anomaly`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(features)
        });

        const data = await response.json();

        if (data.success) {
            console.log('Anomaly Detection Result:', data);
            if (data.is_anomaly) {
                console.warn(`ANOMALY DETECTED: ${data.anomaly_type} (Severity: ${data.severity})`);
            }
            return data;
        } else {
            console.error('Anomaly detection failed:', data.error);
        }
    } catch (error) {
        console.error('Error detecting anomaly:', error);
    }
}

// Function 5: Predict Service Demand
async function predictServiceDemand(features) {
    try {
        const response = await fetch(`${API_BASE_URL}/predict_service_demand`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(features)
        });

        const data = await response.json();

        if (data.success) {
            console.log('Service Demand Prediction:', data);
            return data;
        } else {
            console.error('Demand prediction failed:', data.error);
        }
    } catch (error) {
        console.error('Error predicting demand:', error);
    }
}

// Example Usage:
async function example() {
    // Get model information
    const modelInfo = await getModelInfo();

    // Example feature data (adjust based on your actual features)
    const sampleFeatures = {
        day_of_week: 3,
        day_of_month: 15,
        month: 6,
        quarter: 2,
        is_weekend: 0,
        days_since_start: 365,
        enrol_rolling_mean_7d: 1000,
        enrol_rolling_std_7d: 150,
        // ... add all required features
    };

    // Make single prediction
    const prediction = await predictEnrollment(sampleFeatures);
    console.log(`Predicted enrollment: ${prediction}`);
}

// React Component Example
function EnrollmentPredictor() {
    const [prediction, setPrediction] = React.useState(null);
    const [loading, setLoading] = React.useState(false);

    const handlePredict = async (formData) => {
        setLoading(true);
        try {
            const result = await predictEnrollment(formData);
            setPrediction(result);
        } catch (error) {
            console.error('Prediction error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="predictor">
            <h2>Aadhaar Enrollment Predictor</h2>
            {loading ? (
                <p>Loading prediction...</p>
            ) : (
                <div>
                    {prediction && (
                        <div className="result">
                            <h3>Predicted Enrollment: {prediction.toFixed(0)}</h3>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
