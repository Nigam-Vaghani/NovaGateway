import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Server, Route, Shield, ActivitySquare } from 'lucide-react';

const Navbar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard size={18} /> },
    { name: 'Request Logs', path: '/logs', icon: <ActivitySquare size={18} /> },
    { name: 'Routes', path: '/routes', icon: <Route size={18} /> },
    { name: 'Backends', path: '/backends', icon: <Server size={18} /> },
    { name: 'Security', path: '/security', icon: <Shield size={18} /> },
  ];

  return (
    <header className="glass-card m-4 sticky top-4 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0 flex items-center">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-brand-500 to-accent-500 bg-clip-text text-transparent">
              NovaGateway
            </h1>
          </div>
          
          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-2">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-300 ${
                    isActive 
                      ? 'bg-brand-500 text-white shadow-neon scale-105' 
                      : 'text-slate-600 hover:bg-brand-50 hover:text-brand-600'
                  }`
                }
              >
                {item.icon}
                <span>{item.name}</span>
              </NavLink>
            ))}
          </nav>

          {/* Version Info */}
          <div className="hidden md:block px-3 py-1 bg-white/50 border border-slate-200 rounded-full text-xs text-brand-600 font-mono font-semibold shadow-sm">
            v1.0.0
          </div>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      <div className="md:hidden overflow-x-auto pb-2 px-2 flex space-x-2 no-scrollbar">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-1 px-3 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all duration-300 ${
                isActive 
                  ? 'bg-brand-500 text-white shadow-neon' 
                  : 'text-slate-600 bg-white/40 hover:bg-white'
              }`
            }
          >
            {item.icon}
            <span>{item.name}</span>
          </NavLink>
        ))}
      </div>
    </header>
  );
};

export default Navbar;
