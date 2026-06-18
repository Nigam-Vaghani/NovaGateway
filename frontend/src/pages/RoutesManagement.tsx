import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchRoutes, toggleRoute, deleteRoute, createRoute } from '../api/client';
import { Plus, Trash2, Power } from 'lucide-react';

const RoutesManagement = () => {
  const queryClient = useQueryClient();
  const { data: routes, isLoading } = useQuery({ queryKey: ['routes'], queryFn: fetchRoutes });

  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ name: '', path_prefix: '', strip_prefix: true, cache_ttl_seconds: '' });

  const toggleMutation = useMutation({
    mutationFn: toggleRoute,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['routes'] })
  });

  const deleteMutation = useMutation({
    mutationFn: deleteRoute,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['routes'] })
  });

  const createMutation = useMutation({
    mutationFn: createRoute,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routes'] });
      setShowModal(false);
      setFormData({ name: '', path_prefix: '', strip_prefix: true, cache_ttl_seconds: '' });
    }
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-800">Routes Management</h1>
        <button onClick={() => setShowModal(true)} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
          <Plus size={18} />
          <span>Add Route</span>
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-4 font-medium text-slate-500 text-sm">Name</th>
              <th className="px-6 py-4 font-medium text-slate-500 text-sm">Prefix</th>
              <th className="px-6 py-4 font-medium text-slate-500 text-sm">Strip</th>
              <th className="px-6 py-4 font-medium text-slate-500 text-sm">Cache TTL</th>
              <th className="px-6 py-4 font-medium text-slate-500 text-sm">Status</th>
              <th className="px-6 py-4 font-medium text-slate-500 text-sm text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isLoading ? (
              <tr><td colSpan={6} className="px-6 py-8 text-center text-slate-500">Loading routes...</td></tr>
            ) : routes?.map((route: any) => (
              <tr key={route.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4 text-sm font-medium text-slate-800">{route.name}</td>
                <td className="px-6 py-4 text-sm font-mono text-slate-600">{route.path_prefix}</td>
                <td className="px-6 py-4 text-sm text-slate-600">{route.strip_prefix ? 'Yes' : 'No'}</td>
                <td className="px-6 py-4 text-sm text-slate-600">{route.cache_ttl_seconds ? `${route.cache_ttl_seconds}s` : 'Off'}</td>
                <td className="px-6 py-4 text-sm">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${route.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-800'}`}>
                    {route.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-right space-x-3">
                  <button onClick={() => toggleMutation.mutate(route.id)} className={`${route.is_active ? 'text-amber-500' : 'text-emerald-500'} hover:opacity-80 transition-opacity`} title="Toggle Status">
                    <Power size={18} />
                  </button>
                  <button onClick={() => deleteMutation.mutate(route.id)} className="text-red-500 hover:opacity-80 transition-opacity" title="Delete">
                    <Trash2 size={18} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
            <div className="p-6 border-b border-slate-100">
              <h2 className="text-xl font-bold text-slate-800">Add New Route</h2>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Route Name</label>
                <input type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. Users API" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Path Prefix</label>
                <input type="text" value={formData.path_prefix} onChange={e => setFormData({...formData, path_prefix: e.target.value})} className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. /api/users" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Cache TTL (Seconds)</label>
                <input type="number" value={formData.cache_ttl_seconds} onChange={e => setFormData({...formData, cache_ttl_seconds: e.target.value})} className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Leave empty to disable" />
              </div>
              <div className="flex items-center space-x-2">
                <input type="checkbox" id="strip" checked={formData.strip_prefix} onChange={e => setFormData({...formData, strip_prefix: e.target.checked})} className="rounded text-blue-600 focus:ring-blue-500" />
                <label htmlFor="strip" className="text-sm text-slate-700">Strip prefix before forwarding</label>
              </div>
            </div>
            <div className="p-6 border-t border-slate-100 bg-slate-50 flex justify-end space-x-3">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-slate-600 hover:text-slate-800 font-medium">Cancel</button>
              <button 
                onClick={() => createMutation.mutate({ ...formData, cache_ttl_seconds: formData.cache_ttl_seconds ? parseInt(formData.cache_ttl_seconds) : null })}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Save Route
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoutesManagement;
