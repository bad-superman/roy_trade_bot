import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import BacktestPage from './pages/Backtest';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="backtest" element={<BacktestPage />} />
          <Route path="*" element={<div>页面建设中...</div>} />
        </Route>
      </Routes>
    </Router>
  );
}


export default App;

