import React, { useState } from 'react';
import { User, Bell, Globe, Palette, Mail, MessageSquare, CheckCircle } from 'lucide-react';

function Settings({ theme, setTheme, user }) {
  const isDark = theme === 'dark';
  const [language, setLanguage] = useState('english');
  const [reportFormat, setReportFormat] = useState('pdf');
  const [notifications, setNotifications] = useState({
    email: true,
    slack: false,
    teams: false,
    browser: true
  });

  const integrations = [
    { 
      id: 'slack',
      name: 'Slack',
      desc: 'Send reports and alerts to Slack channels',
      connected: notifications.slack,
      icon: MessageSquare,
      color: 'purple'
    },
    { 
      id: 'teams',
      name: 'Microsoft Teams',
      desc: 'Share insights with your team on Teams',
      connected: notifications.teams,
      icon: MessageSquare,
      color: 'blue'
    },
    { 
      id: 'email',
      name: 'Email Notifications',
      desc: 'Receive reports via email automatically',
      connected: notifications.email,
      icon: Mail,
      color: 'green'
    }
  ];

  const toggleIntegration = (id) => {
    setNotifications(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold">Settings</h2>
        <p className="text-gray-500 mt-1">Manage your preferences and integrations</p>
      </div>
      
      {/* User Profile */}
      <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-6 shadow-lg`}>
        <div className="flex items-center gap-2 mb-6">
          <User className="w-5 h-5 text-blue-600" />
          <h3 className="text-xl font-bold">User Profile</h3>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg">
            <span className="text-white text-2xl font-bold">{user.name.charAt(0)}</span>
          </div>
          <div className="flex-1">
            <h4 className="text-xl font-bold">{user.name}</h4>
            <p className="text-gray-500">{user.email}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="px-3 py-1 bg-blue-100 text-blue-600 rounded-full text-sm font-semibold">
                {user.role}
              </span>
              <span className="px-3 py-1 bg-green-100 text-green-600 rounded-full text-sm font-semibold flex items-center gap-1">
                <CheckCircle className="w-3 h-3" />
                Verified
              </span>
            </div>
          </div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Edit Profile
          </button>
        </div>
      </div>

      {/* Appearance Settings */}
      <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-6 shadow-lg`}>
        <div className="flex items-center gap-2 mb-6">
          <Palette className="w-5 h-5 text-blue-600" />
          <h3 className="text-xl font-bold">Appearance</h3>
        </div>
        
        <div>
          <label className="block text-sm font-semibold mb-3">Theme</label>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setTheme('light')}
              className={`p-4 rounded-xl border-2 transition-all ${
                theme === 'light'
                  ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                  : isDark ? 'border-gray-600' : 'border-gray-300'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-white border-2 border-gray-300 rounded-lg flex items-center justify-center">
                  <div className="w-6 h-6 bg-gradient-to-br from-blue-400 to-purple-400 rounded"></div>
                </div>
                <div className="text-left">
                  <p className="font-semibold">Light Mode</p>
                  <p className="text-xs text-gray-500">Classic bright theme</p>
                </div>
              </div>
            </button>
            
            <button
              onClick={() => setTheme('dark')}
              className={`p-4 rounded-xl border-2 transition-all ${
                theme === 'dark'
                  ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                  : isDark ? 'border-gray-600' : 'border-gray-300'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gray-800 border-2 border-gray-600 rounded-lg flex items-center justify-center">
                  <div className="w-6 h-6 bg-gradient-to-br from-blue-400 to-purple-400 rounded"></div>
                </div>
                <div className="text-left">
                  <p className="font-semibold">Dark Mode</p>
                  <p className="text-xs text-gray-500">Easy on the eyes</p>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Regional Settings */}
      <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-6 shadow-lg`}>
        <div className="flex items-center gap-2 mb-6">
          <Globe className="w-5 h-5 text-blue-600" />
          <h3 className="text-xl font-bold">Regional Settings</h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2">Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className={`w-full px-4 py-3 rounded-xl border ${
                isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'
              } focus:ring-2 focus:ring-blue-500`}
            >
              <option value="english">English</option>
              <option value="hindi">हिन्दी (Hindi)</option>
              <option value="spanish">Español (Spanish)</option>
              <option value="french">Français (French)</option>
              <option value="german">Deutsch (German)</option>
              <option value="chinese">中文 (Chinese)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-semibold mb-2">Default Report Format</label>
            <select
              value={reportFormat}
              onChange={(e) => setReportFormat(e.target.value)}
              className={`w-full px-4 py-3 rounded-xl border ${
                isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'
              } focus:ring-2 focus:ring-blue-500`}
            >
              <option value="pdf">PDF Document</option>
              <option value="ppt">PowerPoint Presentation</option>
              <option value="excel">Excel Spreadsheet</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-semibold mb-2">Time Zone</label>
            <select
              className={`w-full px-4 py-3 rounded-xl border ${
                isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'
              } focus:ring-2 focus:ring-blue-500`}
            >
              <option>Asia/Kolkata (IST, UTC+5:30)</option>
              <option>America/New_York (EST, UTC-5)</option>
              <option>Europe/London (GMT, UTC+0)</option>
              <option>Asia/Tokyo (JST, UTC+9)</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Notification Settings */}
      <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-6 shadow-lg`}>
        <div className="flex items-center gap-2 mb-6">
          <Bell className="w-5 h-5 text-blue-600" />
          <h3 className="text-xl font-bold">Notifications</h3>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold">Browser Notifications</p>
              <p className="text-sm text-gray-500">Get desktop notifications for alerts</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notifications.browser}
                onChange={() => toggleIntegration('browser')}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold">Alert Sounds</p>
              <p className="text-sm text-gray-500">Play sound for important alerts</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" defaultChecked className="sr-only peer" />
              <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Integrations */}
      <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-6 shadow-lg`}>
        <h3 className="text-xl font-bold mb-6">Integrations</h3>
        
        <div className="space-y-4">
          {integrations.map((integration) => (
            <div key={integration.id} className={`flex items-center justify-between p-4 rounded-xl ${
              isDark ? 'bg-gray-700' : 'bg-gray-50'
            }`}>
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl bg-${integration.color}-100 flex items-center justify-center`}>
                  <integration.icon className={`w-6 h-6 text-${integration.color}-600`} />
                </div>
                <div>
                  <p className="font-semibold">{integration.name}</p>
                  <p className="text-sm text-gray-500">{integration.desc}</p>
                </div>
              </div>
              <button
                onClick={() => toggleIntegration(integration.id)}
                className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                  integration.connected
                    ? 'bg-green-100 text-green-600 hover:bg-green-200'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {integration.connected ? 'Connected' : 'Connect'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Danger Zone */}
      <div className={`${isDark ? 'bg-red-900/20 border-red-500' : 'bg-red-50 border-red-200'} border-l-4 rounded-xl p-6`}>
        <h3 className="text-xl font-bold text-red-600 mb-4">Danger Zone</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold">Export Data</p>
              <p className="text-sm text-gray-500">Download all your data</p>
            </div>
            <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors">
              Export
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold">Delete Account</p>
              <p className="text-sm text-gray-500">Permanently delete your account</p>
            </div>
            <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;