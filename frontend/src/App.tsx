import { useEffect, useState } from 'react';
import axios from 'axios';
import { Activity, LayoutDashboard, Route, Server, Shield, FileText, Settings } from 'lucide-react';

function App() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    // Attempt to fetch health status from backend
    axios.get('http://localhost:8000/health')
      .then(res => setHealth(res.data))
      .catch(err => console.error("Failed to fetch health status:", err));
  }, []);

  return (
    <div className="flex h-screen bg-slate-900 text-slate-200">
      {/* Sidebar */}
      <div className="w-56 bg-slate-800 h-full flex flex-col py-5 border-r border-slate-700">
        <div className="px-5 mb-5 pb-5 border-b border-slate-700">
          <h1 className="text-lg font-bold text-sky-400 flex items-center gap-2">
            <Activity size={20} /> NovaGateway
          </h1>
        </div>
        <nav className="flex flex-col gap-1 px-3">
          <a href="#" className="px-3 py-2 bg-slate-900 text-sky-400 rounded-md flex items-center gap-3 text-sm border-l-2 border-sky-400">
            <LayoutDashboard size={18} /> Dashboard
          </a>
          <a href="#" className="px-3 py-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-md flex items-center gap-3 text-sm">
            <Route size={18} /> Routes
          </a>
          <a href="#" className="px-3 py-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-md flex items-center gap-3 text-sm">
            <Server size={18} /> Backends
          </a>
          <a href="#" className="px-3 py-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-md flex items-center gap-3 text-sm">
            <FileText size={18} /> Request Logs
          </a>
          <a href="#" className="px-3 py-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-md flex items-center gap-3 text-sm">
            <Shield size={18} /> Security
          </a>
          <a href="#" className="px-3 py-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-md flex items-center gap-3 text-sm">
            <Settings size={18} /> Settings
          </a>
        </nav>
      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col overflow-auto">
        <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
          <h2 className="text-xl font-semibold">Dashboard</h2>
          <div className="text-sm text-slate-500">
            Backend Status: {health ? (
              <span className="text-green-500 font-medium">Connected (v{health.version})</span>
            ) : (
              <span className="text-red-500 font-medium">Disconnected</span>
            )}
          </div>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-slate-800 p-5 rounded-lg border border-slate-700/50">
              <div className="text-xs text-slate-400 mb-2">Total Requests (24h)</div>
              <div className="text-2xl font-bold text-slate-100">0</div>
              <div className="text-xs text-sky-400 mt-1">Waiting for data...</div>
            </div>
            <div className="bg-slate-800 p-5 rounded-lg border border-slate-700/50">
              <div className="text-xs text-slate-400 mb-2">Avg Latency</div>
              <div className="text-2xl font-bold text-slate-100">0ms</div>
            </div>
            <div className="bg-slate-800 p-5 rounded-lg border border-slate-700/50">
              <div className="text-xs text-slate-400 mb-2">Error Rate</div>
              <div className="text-2xl font-bold text-slate-100">0%</div>
            </div>
            <div className="bg-slate-800 p-5 rounded-lg border border-slate-700/50">
              <div className="text-xs text-slate-400 mb-2">Cache Hit Rate</div>
              <div className="text-2xl font-bold text-slate-100">0%</div>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
             <div className="bg-slate-800 p-5 rounded-lg border border-slate-700/50 col-span-2">
                <h3 className="text-sm text-slate-400 mb-4">Requests per Minute</h3>
                <div className="h-48 flex items-center justify-center text-slate-600 bg-slate-900/50 rounded">
                   [ Chart Placeholder ]
                </div>
             </div>
             <div className="bg-slate-800 p-5 rounded-lg border border-slate-700/50">
                <h3 className="text-sm text-slate-400 mb-4">Status Codes</h3>
                <div className="h-48 flex items-center justify-center text-slate-600 bg-slate-900/50 rounded">
                   [ Pie Chart Placeholder ]
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
