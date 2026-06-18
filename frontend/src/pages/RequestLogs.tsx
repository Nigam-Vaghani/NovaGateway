import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchLogs } from '../api/client';
import { Search, Filter } from 'lucide-react';

const RequestLogs = () => {
  const [page, setPage] = useState(1);
  const [method, setMethod] = useState('');
  const [path, setPath] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['logs', page, method, path],
    queryFn: () => fetchLogs({ page, page_size: 20, method: method || undefined, path: path || undefined }),
    refetchInterval: 10000,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-slate-800">Request Logs</h1>
      
      <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4 bg-white p-4 rounded-xl shadow-sm border border-slate-100">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input 
            type="text" 
            placeholder="Search by path..." 
            value={path}
            onChange={(e) => setPath(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="w-full md:w-48 relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <select 
            value={method}
            onChange={(e) => setMethod(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
          >
            <option value="">All Methods</option>
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
            <option value="PATCH">PATCH</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 font-medium text-slate-500 text-sm">Timestamp</th>
                <th className="px-6 py-4 font-medium text-slate-500 text-sm">Method</th>
                <th className="px-6 py-4 font-medium text-slate-500 text-sm">Path</th>
                <th className="px-6 py-4 font-medium text-slate-500 text-sm">Status</th>
                <th className="px-6 py-4 font-medium text-slate-500 text-sm">Latency</th>
                <th className="px-6 py-4 font-medium text-slate-500 text-sm">Client IP</th>
                <th className="px-6 py-4 font-medium text-slate-500 text-sm">Cache Hit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-500">Loading logs...</td></tr>
              ) : data?.items?.length === 0 ? (
                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-500">No logs found.</td></tr>
              ) : (
                data?.items?.map((log: any) => (
                  <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-3 text-sm text-slate-600">{new Date(log.timestamp).toLocaleString()}</td>
                    <td className="px-6 py-3 text-sm">
                      <span className={`font-semibold ${log.method === 'GET' ? 'text-blue-600' : log.method === 'POST' ? 'text-emerald-600' : 'text-amber-600'}`}>{log.method}</span>
                    </td>
                    <td className="px-6 py-3 text-sm font-mono text-slate-700">{log.path}</td>
                    <td className="px-6 py-3 text-sm">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${log.status_code < 400 ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                        {log.status_code}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-600">{log.latency_ms?.toFixed(2)} ms</td>
                    <td className="px-6 py-3 text-sm text-slate-600">{log.client_ip}</td>
                    <td className="px-6 py-3 text-sm">
                      {log.cache_hit ? <span className="text-emerald-600 font-medium">Yes</span> : <span className="text-slate-400">No</span>}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="px-6 py-4 border-t border-slate-200 flex items-center justify-between">
          <span className="text-sm text-slate-500">
            Showing {data?.items?.length || 0} of {data?.total || 0} results
          </span>
          <div className="flex space-x-2">
            <button 
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
              className="px-3 py-1 rounded border border-slate-200 text-sm text-slate-600 disabled:opacity-50 hover:bg-slate-50"
            >
              Previous
            </button>
            <button 
              disabled={!data?.items || data?.items.length < 20}
              onClick={() => setPage(p => p + 1)}
              className="px-3 py-1 rounded border border-slate-200 text-sm text-slate-600 disabled:opacity-50 hover:bg-slate-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RequestLogs;
