import React, { useState } from 'react';
import { Bell, Menu, X, TrendingUp, AlertCircle, LogOut, User, Settings } from 'lucide-react';

const mockAlerts = [
  { id: 1, type: 'warning', dept: 'Finance', message: 'Marketing expenses exceeded budget by 5%', time: '2h ago', priority: 'high' },
  { id: 2, type: 'info', dept: 'HR', message: 'Attrition rate increased to 8.2% this month', time: '5h ago', priority: 'medium' },
  { id: 3, type: 'success', dept: 'Sales', message: 'Q2 targets achieved - 102% of goal', time: '1d ago', priority: 'low' },
  { id: 4, type: 'warning', dept: 'Operations', message: 'Equipment downtime detected in Warehouse B', time: '3h ago', priority: 'high' }
];

export default function Navbar({ 
  theme, 
  user, 
  showNotifications, 
  setShowNotifications, 
  sidebarOpen, 
  setSidebarOpen,
  onLogout 
}) {
  const isDark = theme === 'dark';
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = () => {
    setShowUserMenu(false);
    if (onLogout) {
      onLogout();
    }
  };

  return (
    <nav className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-b px-6 py-4 sticky top-0 z-50 backdrop-blur-lg bg-opacity-90`}>
      <div className="flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className={`p-2 rounded-lg transition-colors ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div className="hidden md:block">
              <h1 className="text-lg font-bold">Report Generator AI</h1>
              <p className="text-xs text-gray-500">Enterprise Dashboard</p>
            </div>
          </div>
        </div>
        
        {/* Right Section */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className={`relative p-2 rounded-lg transition-colors ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
            >
              <Bell className="w-5 h-5" />
              {mockAlerts.length > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
              )}
            </button>
            
            {/* Notifications Dropdown */}
            {showNotifications && (
              <>
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setShowNotifications(false)}
                ></div>
                <div className={`absolute right-0 mt-2 w-96 ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-2xl shadow-2xl border max-h-96 overflow-y-auto z-50`}>
                  <div className={`sticky top-0 ${isDark ? 'bg-gray-800' : 'bg-white'} p-4 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-lg">Notifications</h3>
                      <span className="px-2 py-1 bg-red-100 text-red-600 rounded-full text-xs font-semibold">
                        {mockAlerts.length} new
                      </span>
                    </div>
                  </div>
                  
                  {mockAlerts.map(alert => (
                    <div 
                      key={alert.id} 
                      className={`p-4 border-b ${isDark ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-100 hover:bg-gray-50'} transition-colors cursor-pointer`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                          alert.type === 'warning' ? 'bg-orange-100' : 
                          alert.type === 'success' ? 'bg-green-100' : 
                          'bg-blue-100'
                        }`}>
                          <AlertCircle className={`w-4 h-4 ${
                            alert.type === 'warning' ? 'text-orange-600' : 
                            alert.type === 'success' ? 'text-green-600' : 
                            'text-blue-600'
                          }`} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-semibold text-gray-500">{alert.dept}</span>
                            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                              alert.priority === 'high' ? 'bg-red-100 text-red-600' :
                              alert.priority === 'medium' ? 'bg-orange-100 text-orange-600' :
                              'bg-green-100 text-green-600'
                            }`}>
                              {alert.priority}
                            </span>
                          </div>
                          <p className="text-sm mb-1">{alert.message}</p>
                          <p className="text-xs text-gray-500">{alert.time}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  <div className="p-3 text-center">
                    <button className="text-sm text-blue-600 hover:underline font-medium">
                      View All Notifications
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
          
          {/* User Profile with Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-3 p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="text-right hidden md:block">
                <p className="text-sm font-semibold">{user?.name || 'User'}</p>
                <p className="text-xs text-gray-500">{user?.role || 'Role'}</p>
              </div>
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center cursor-pointer hover:shadow-lg transition-shadow">
                <span className="text-white text-sm font-bold">
                  {user?.name?.charAt(0) || 'U'}
                </span>
              </div>
            </button>
            
            {/* User Dropdown Menu */}
            {showUserMenu && (
              <>
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setShowUserMenu(false)}
                ></div>
                <div className={`absolute right-0 mt-2 w-64 ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-2xl shadow-2xl border z-50`}>
                  {/* User Info */}
                  <div className="p-4 border-b dark:border-gray-700">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-lg font-bold">
                          {user?.name?.charAt(0) || 'U'}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm truncate">{user?.name || 'User'}</p>
                        <p className="text-xs text-gray-500 truncate">{user?.email || 'user@company.com'}</p>
                        <p className="text-xs text-blue-600 font-medium">{user?.role || 'Role'}</p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Menu Items */}
                  <div className="p-2">
                    <button 
                      className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-left"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <User className="w-4 h-4 text-gray-500" />
                      <span className="text-sm">Profile Settings</span>
                    </button>
                    
                    <button 
                      className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-left"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <Settings className="w-4 h-4 text-gray-500" />
                      <span className="text-sm">Preferences</span>
                    </button>
                  </div>
                  
                  {/* Logout Button */}
                  <div className="p-2 border-t dark:border-gray-700">
                    <button 
                      className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-left text-red-600 dark:text-red-400"
                      onClick={handleLogout}
                    >
                      <LogOut className="w-4 h-4" />
                      <span className="text-sm font-medium">Sign Out</span>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}