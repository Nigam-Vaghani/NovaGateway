import { useQuery } from '@tanstack/react-query';
import { fetchDashboardStats, fetchBackends } from '../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, Clock, AlertTriangle, Zap } from 'lucide-react';

const COLORS = ['#0ea5e9', '#8b5cf6', '#f43f5e', '#10b981'];

const Dashboard = () => {
  const { data: stats, isLoading, isError } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: fetchDashboardStats,
    refetchInterval: 10000,
  });

  const { data: backends } = useQuery({
    queryKey: ['backends'],
    queryFn: fetchBackends,
    refetchInterval: 10000,
  });

  if (isLoading) return <div className="p-8 text-center text-slate-500 animate-pulse font-semibold">Initializing Neural Matrix...</div>;
  if (isError) return <div className="p-8 text-center text-red-500 font-semibold">Connection to core failed.</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-linear-to-r from-brand-600 to-accent-600">Overview</h1>
      
      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Requests (24h)" value={stats?.totalRequests || 0} icon={<Activity size={24} />} color="text-brand-500" bg="bg-brand-100" />
        <StatCard title="Avg Latency" value={`${stats?.avgLatency || 0} ms`} icon={<Clock size={24} />} color="text-accent-500" bg="bg-accent-100" />
        <StatCard title="Error Rate" value={`${stats?.errorRate || 0}%`} icon={<AlertTriangle size={24} />} color="text-rose-500" bg="bg-rose-100" />
        <StatCard title="Cache Hit Rate" value={`${stats?.cacheHitRate || 0}%`} icon={<Zap size={24} />} color="text-emerald-500" bg="bg-emerald-100" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Line Chart */}
        <div className="lg:col-span-2 glass-card p-6">
          <h2 className="text-lg font-bold mb-4 text-slate-800">Traffic Analysis (60m)</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats?.requestsPerMinute || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.3)" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip contentStyle={{ background: 'rgba(255,255,255,0.8)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.5)', backdropFilter: 'blur(8px)' }} />
                <Line type="monotone" dataKey="requests" stroke="#0ea5e9" strokeWidth={4} dot={false} activeDot={{ r: 8, fill: '#0ea5e9', stroke: '#fff', strokeWidth: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-bold mb-4 text-slate-800">Status Distribution</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={stats?.statusDistribution || []} cx="50%" cy="50%" innerRadius={70} outerRadius={90} paddingAngle={5} dataKey="value" stroke="none">
                  {(stats?.statusDistribution || []).map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip contentStyle={{ background: 'rgba(255,255,255,0.8)', borderRadius: '12px', border: 'none', backdropFilter: 'blur(8px)' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Endpoints Table */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-bold mb-4 text-slate-800">Top Endpoints</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200/50 text-sm text-slate-500 uppercase tracking-wider">
                  <th className="pb-3 font-semibold">Path</th>
                  <th className="pb-3 font-semibold text-right">Requests</th>
                </tr>
              </thead>
              <tbody>
                {(stats?.topEndpoints || []).map((endpoint: any, idx: number) => (
                  <tr key={idx} className="border-b border-slate-200/30 last:border-0 hover:bg-white/30 transition-colors">
                    <td className="py-3 text-slate-700 font-mono text-sm">{endpoint.path}</td>
                    <td className="py-3 text-slate-800 font-semibold text-right">{endpoint.requests}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Backend Health Table */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-bold mb-4 text-slate-800">Backend Nodes</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200/50 text-sm text-slate-500 uppercase tracking-wider">
                  <th className="pb-3 font-semibold">Node URL</th>
                  <th className="pb-3 font-semibold text-right">Status</th>
                </tr>
              </thead>
              <tbody>
                {(backends || []).map((backend: any) => (
                  <tr key={backend.id} className="border-b border-slate-200/30 last:border-0 hover:bg-white/30 transition-colors">
                    <td className="py-3 text-slate-700 font-medium">{backend.url}</td>
                    <td className="py-3 text-right">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold shadow-sm ${backend.is_healthy ? 'bg-emerald-100/80 text-emerald-700 border border-emerald-200' : 'bg-rose-100/80 text-rose-700 border border-rose-200'}`}>
                        {backend.is_healthy ? 'ONLINE' : 'OFFLINE'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color, bg }: any) => (
  <div className="glass-card p-6 flex items-center space-x-4 hover:-translate-y-1 transition-transform duration-300 group">
    <div className={`p-4 rounded-xl ${bg} ${color} shadow-inner group-hover:scale-110 transition-transform duration-300`}>{icon}</div>
    <div>
      <p className="text-sm font-semibold text-slate-500 tracking-wide uppercase">{title}</p>
      <p className="text-3xl font-extrabold text-slate-800">{value}</p>
    </div>
  </div>
);

export default Dashboard;
