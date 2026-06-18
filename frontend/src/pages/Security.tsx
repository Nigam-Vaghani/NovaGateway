import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchIpRules, createIpRule, deleteIpRule, fetchApiKeys, createApiKey, deleteApiKey } from '../api/client';
import { Plus, Trash2, Key, Globe, Copy } from 'lucide-react';

const Security = () => {
  const queryClient = useQueryClient();
  const { data: ipRules } = useQuery({ queryKey: ['ipRules'], queryFn: fetchIpRules });
  const { data: apiKeys } = useQuery({ queryKey: ['apiKeys'], queryFn: fetchApiKeys });

  const [ipForm, setIpForm] = useState({ ip_address: '', action: 'block' });
  const [keyName, setKeyName] = useState('');
  const [newKey, setNewKey] = useState<string | null>(null);

  const createIpMutation = useMutation({
    mutationFn: createIpRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ipRules'] });
      setIpForm({ ip_address: '', action: 'block' });
    }
  });

  const deleteIpMutation = useMutation({
    mutationFn: deleteIpRule,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['ipRules'] })
  });

  const createKeyMutation = useMutation({
    mutationFn: createApiKey,
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
      setKeyName('');
      setNewKey(data.key);
    }
  });

  const deleteKeyMutation = useMutation({
    mutationFn: deleteApiKey,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['apiKeys'] })
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-slate-800">Security Policies</h1>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        
        {/* IP Rules Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 flex flex-col h-[500px]">
          <div className="p-6 border-b border-slate-100 flex items-center space-x-3">
            <Globe className="text-blue-500" />
            <h2 className="text-xl font-bold text-slate-800">IP Rules (Allow/Block)</h2>
          </div>
          
          <div className="p-6 border-b border-slate-100 bg-slate-50">
            <div className="flex space-x-3">
              <input type="text" value={ipForm.ip_address} onChange={e => setIpForm({...ipForm, ip_address: e.target.value})} placeholder="e.g. 192.168.1.1 or 10.0.0.0/24" className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
              <select value={ipForm.action} onChange={e => setIpForm({...ipForm, action: e.target.value})} className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white">
                <option value="allow">Allow</option>
                <option value="block">Block</option>
              </select>
              <button onClick={() => createIpMutation.mutate(ipForm)} disabled={!ipForm.ip_address} className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                <Plus size={18} />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50 sticky top-0">
                <tr>
                  <th className="px-6 py-3 font-medium text-slate-500 text-sm">IP / CIDR</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-sm">Action</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-sm text-right"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {ipRules?.map((rule: any) => (
                  <tr key={rule.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-3 text-sm font-mono text-slate-700">{rule.ip_address}</td>
                    <td className="px-6 py-3 text-sm">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${rule.action === 'allow' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                        {rule.action.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-right">
                      <button onClick={() => deleteIpMutation.mutate(rule.id)} className="text-slate-400 hover:text-red-500 transition-colors">
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* API Keys Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 flex flex-col h-[500px]">
          <div className="p-6 border-b border-slate-100 flex items-center space-x-3">
            <Key className="text-amber-500" />
            <h2 className="text-xl font-bold text-slate-800">API Keys</h2>
          </div>
          
          <div className="p-6 border-b border-slate-100 bg-slate-50 space-y-4">
            <div className="flex space-x-3">
              <input type="text" value={keyName} onChange={e => setKeyName(e.target.value)} placeholder="Key Name (e.g. Mobile App, Partner API)" className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500" />
              <button onClick={() => createKeyMutation.mutate({ name: keyName })} disabled={!keyName} className="bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap">
                Generate Key
              </button>
            </div>
            {newKey && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg flex items-center justify-between">
                <div>
                  <p className="text-xs text-amber-800 font-bold uppercase tracking-wider mb-1">New Key Generated</p>
                  <p className="font-mono text-sm text-slate-800">{newKey}</p>
                  <p className="text-xs text-amber-700 mt-1">Please copy this now, you won't be able to see it again.</p>
                </div>
                <button onClick={() => navigator.clipboard.writeText(newKey)} className="p-2 text-amber-700 hover:bg-amber-100 rounded-lg transition-colors">
                  <Copy size={18} />
                </button>
              </div>
            )}
          </div>

          <div className="flex-1 overflow-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50 sticky top-0">
                <tr>
                  <th className="px-6 py-3 font-medium text-slate-500 text-sm">Name</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-sm">Key Prefix</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-sm text-right"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {apiKeys?.map((key: any) => (
                  <tr key={key.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-3 text-sm font-medium text-slate-700">{key.name}</td>
                    <td className="px-6 py-3 text-sm font-mono text-slate-500">
                      {key.key_prefix || (key.key ? `${key.key.substring(0, 8)}...` : 'Hidden')}
                    </td>
                    <td className="px-6 py-3 text-right">
                      <button onClick={() => deleteKeyMutation.mutate(key.id)} className="text-slate-400 hover:text-red-500 transition-colors">
                        <Trash2 size={16} />
                      </button>
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

export default Security;
