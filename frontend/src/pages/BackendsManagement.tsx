import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchBackends, fetchRoutes, toggleBackend, deleteBackend, createBackend } from '../api/client';
import { Plus, Trash2, Power } from 'lucide-react';

const BackendsManagement = () => {
  const queryClient = useQueryClient();
  const { data: backends, isLoading: loadingBackends } = useQuery({ queryKey: ['backends'], queryFn: fetchBackends });
  const { data: routes } = useQuery({ queryKey: ['routes'], queryFn: fetchRoutes });

  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ route_id: '', url: '', weight: 1 });

  const toggleMutation = useMutation({
    mutationFn: toggleBackend,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['backends'] })
  });

  const deleteMutation = useMutation({
    mutationFn: deleteBackend,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['backends'] })
  });

  const createMutation = useMutation({
    mutationFn: createBackend,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backends'] });
      setShowModal(false);
      setFormData({ route_id: '', url: '', weight: 1 });
    }
  });

  // Group backends by route
  const backendsByRoute = backends?.reduce((acc: any, backend: any) => {
    if (!acc[backend.route_id]) acc[backend.route_id] = [];
    acc[backend.route_id].push(backend);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-800">Backends Management</h1>
        <button onClick={() => setShowModal(true)} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
          <Plus size={18} />
          <span>Add Backend</span>
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        {loadingBackends ? (
          <div className="p-8 text-center text-slate-500">Loading backends...</div>
        ) : (
          Object.entries(backendsByRoute || {}).map(([routeId, routeBackends]: [string, any]) => {
            const route = routes?.find((r: any) => r.id === routeId);
            return (
              <div key={routeId} className="border-b border-slate-200 last:border-0">
                <div className="bg-slate-50 px-6 py-3 font-medium text-slate-700 flex justify-between">
                  <span>Route: {route?.name || routeId} ({route?.path_prefix})</span>
                  <span className="text-sm font-normal text-slate-500">{routeBackends.length} backend(s)</span>
                </div>
                <table className="w-full text-left border-collapse">
                  <tbody className="divide-y divide-slate-100">
                    {routeBackends.map((backend: any) => (
                      <tr key={backend.id} className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-6 py-4 text-sm font-mono text-slate-800 w-1/3">{backend.url}</td>
                        <td className="px-6 py-4 text-sm text-slate-600">Weight: {backend.weight}</td>
                        <td className="px-6 py-4 text-sm">
                          <span className="flex items-center space-x-2">
                            <span className={`w-2.5 h-2.5 rounded-full ${backend.is_healthy ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
                            <span className="text-slate-600">{backend.is_healthy ? 'Healthy' : 'Unhealthy'}</span>
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-right space-x-3">
                          <button onClick={() => toggleMutation.mutate(backend.id)} className={`${backend.is_healthy ? 'text-amber-500' : 'text-emerald-500'} hover:opacity-80 transition-opacity`} title="Toggle Health">
                            <Power size={18} />
                          </button>
                          <button onClick={() => deleteMutation.mutate(backend.id)} className="text-red-500 hover:opacity-80 transition-opacity" title="Delete">
                            <Trash2 size={18} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          })
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
            <div className="p-6 border-b border-slate-100">
              <h2 className="text-xl font-bold text-slate-800">Add New Backend</h2>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Target Route</label>
                <select 
                  value={formData.route_id} 
                  onChange={e => setFormData({...formData, route_id: e.target.value})}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                >
                  <option value="">Select a route...</option>
                  {routes?.map((route: any) => (
                    <option key={route.id} value={route.id}>{route.name} ({route.path_prefix})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Backend URL</label>
                <input type="text" value={formData.url} onChange={e => setFormData({...formData, url: e.target.value})} className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="http://127.0.0.1:8001" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Weight</label>
                <input type="number" min="1" value={formData.weight} onChange={e => setFormData({...formData, weight: parseInt(e.target.value)})} className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
            <div className="p-6 border-t border-slate-100 bg-slate-50 flex justify-end space-x-3">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-slate-600 hover:text-slate-800 font-medium">Cancel</button>
              <button 
                onClick={() => createMutation.mutate(formData)}
                disabled={!formData.route_id || !formData.url}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Save Backend
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BackendsManagement;
