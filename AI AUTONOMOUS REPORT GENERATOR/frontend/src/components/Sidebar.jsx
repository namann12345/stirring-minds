import React from 'react';
import { Home, Users, FileText, MessageSquare, Settings } from 'lucide-react';

export default function Sidebar({ currentPage, setCurrentPage, theme }) {
  const isDark = theme === 'dark';
  
  const menuItems = [
    { id: 'dashboard', icon: Home, label: 'Dashboard', badge: null },
    { id: 'departments', icon: Users, label: 'Departments', badge: '5' },
    { id: 'reports', icon: FileText, label: 'Reports', badge: null },
    { id: 'analytics', icon: MessageSquare, label: 'AI Assistant', badge: 'New' },
    { id: 'settings', icon: Settings, label: 'Settings', badge: null }
  ];

  return (
    <aside className={`fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-r transition-all duration-300 z-40 overflow-y-auto`}>
      <nav className="p-4 space-y-2">
        {menuItems.map(item => {
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg transform scale-105'
                  : isDark
                  ? 'text-gray-300 hover:bg-gray-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center gap-3">
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </div>
              {item.badge && (
                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                  isActive 
                    ? 'bg-white text-blue-600' 
                    : 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Quick Stats */}
      <div className="p-4 mt-4">
        <div className={`p-4 rounded-xl ${isDark ? 'bg-gray-700' : 'bg-gray-50'}`}>
          <h4 className="text-sm font-semibold mb-3">Quick Stats</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-500">Reports Today</span>
              <span className="text-sm font-bold">0</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-500">Active Users</span>
              <span className="text-sm font-bold">0</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-500">Pending Tasks</span>
              <span className="text-sm font-bold text-orange-500">0</span>
            </div>
          </div>
        </div>
      </div>

      {/* Support Section */}
      <div className="p-4">
        <div className={`p-4 rounded-xl ${isDark ? 'bg-gradient-to-br from-blue-900/50 to-purple-900/50 border-blue-500' : 'bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200'} border`}>
          <h4 className="text-sm font-semibold mb-2">Need Help?</h4>
          <p className="text-xs text-gray-500 mb-3">Check our documentation or contact support</p>
          <button className="w-full px-3 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
            Get Support
          </button>
        </div>
      </div>
    </aside>
  );
}