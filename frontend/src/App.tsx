import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Demographics from './pages/Demographics';
import Biometrics from './pages/Biometrics';
import LiveMap from './pages/LiveMap';
import PredictionStudio from './pages/PredictionStudio';
import Pricing from './pages/pricing/Pricing';

function App() {
    return (
        <Router>
            <Routes>
                {/* Public Route */}
                <Route path="/" element={<LandingPage />} />

                {/* Protected/Dashboard Routes */}
                <Route path="/dashboard" element={<MainLayout><Dashboard /></MainLayout>} />
                <Route path="/demographics" element={<MainLayout><Demographics /></MainLayout>} />
                <Route path="/biometrics" element={<MainLayout><Biometrics /></MainLayout>} />
                <Route path="/live-map" element={<MainLayout><LiveMap /></MainLayout>} />
                <Route path="/prediction-studio" element={<MainLayout><PredictionStudio /></MainLayout>} />
                <Route path="/pricing" element={<MainLayout><Pricing /></MainLayout>} />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Router>
    );
}

export default App;
