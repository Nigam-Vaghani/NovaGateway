import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import RequestLogs from './pages/RequestLogs';
import RoutesManagement from './pages/RoutesManagement';
import BackendsManagement from './pages/BackendsManagement';
import Security from './pages/Security';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen flex flex-col text-slate-800">
          <Navbar />
          <main className="flex-1 w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/logs" element={<RequestLogs />} />
              <Route path="/routes" element={<RoutesManagement />} />
              <Route path="/backends" element={<BackendsManagement />} />
              <Route path="/security" element={<Security />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
