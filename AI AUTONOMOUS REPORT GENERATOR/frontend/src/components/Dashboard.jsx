import React from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { FileText, AlertCircle, Users, Package, Plus } from 'lucide-react';

const mockChartData = {
  finance: [
    { month: 'Jan', revenue: 180, expenses: 140 },
    { month: 'Feb', revenue: 200, expenses: 150 },
    { month: 'Mar', revenue: 220, expenses: 160 },
    { month: 'Apr', revenue: 240, expenses: 180 },
    { month: 'May', revenue: 260, expenses: 190 },
    { month: 'Jun', revenue: 280, expenses: 200 }
  ]
};

const mockActivities = [
  { id: 1, action: 'Finance Report Generated', user: 'John Doe', time: '10 mins ago', icon: FileText },
  { id: 2, action: 'HR Dashboard Updated', user: 'Jane Smith', time: '1 hour ago', icon: Users },
  { id: 3, action: 'Sales Query Processed', user: 'Mike Johnson', time: '2 hours ago', icon: Package },
  { id: 4, action: 'Compliance Audit Completed', user: 'Sarah Wilson', time: '3 hours ago', icon: AlertCircle }
];

const mockAlerts = [
  { id: 1, dept: 'Finance', message: 'Marketing expenses exceeded budget by 5%', priority: 'high', time: '2h ago' },
  { id: 2, dept: 'HR', message: 'Attrition rate increased to 8.2% this month', priority: 'medium', time: '5h ago' },
  { id: 3, dept: 'Sales', message: 'Q2 targets achieved - 102% of goal', priority: 'low', time: '1d ago' },
  { id: 4, dept: 'Operations', message: 'Equipment downtime detected in Warehouse B', priority: 'high', time: '3h ago' }
];

export default function Dashboard({ theme }) {
  const isDark = theme === 'dark';
  
  const stats = [
    { label: 'Total Reports', value: '1,234', change: '+12%', icon: FileText, color: 'from-blue-500 to-blue-600' },
    { label: 'Active Alerts', value: '8', change: '-3 from last week', icon: AlertCircle, color: 'from-orange-500 to-orange-600' },
    { label: 'Departments', value: '5', change: 'All Active', icon: Users, color: 'from-green-500 to-green-600' },
    { label: 'Data Sources', value: '23', change: '+2 this month', icon: Package, color: 'from-purple-500 to-purple-600' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Dashboard Overview</h2>
          <p className="text-gray-500 mt-1">Welcome back! Here's what's happening today.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all">
          <Plus className="w-4 h-4" />
          Generate Report
        </button>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <div key={idx} className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all cursor-pointer transform hover:-translate-y-1`}>
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${stat.color} flex items-center justify-center shadow-lg`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
            <h3 className="text-3xl font-bold mb-1">{stat.value}</h3>
            <p className="text-sm text-gray-500 mb-2">{stat.label}</p>
            <p className="text-xs text-green-600 font-semibold">{stat.change}</p>
          </div>
        ))}
      </div>

      {/* Charts and Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className={`lg:col-span-2 ${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-6 shadow-lg`}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold">Revenue Trends</h3>
            <div className="flex gap-2">
              <button className={`px-3 py-1 rounded-lg text-sm ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>6M</button>
              <button className="px-3 py-1 rounded-lg text-sm bg-blue-600 text-white">1Y</button>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={mockChartData.finance}>
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorExpenses" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="revenue" stroke="#3b82f6" fillOpacity={1} fill="url(#colorRevenue)" />
              <Area type="monotone" dataKey="expenses" stroke="#ef4444" fillOpacity={1} fill="url(#colorExpenses)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-6 shadow-lg`}>
          <h3 className="text-xl font-bold mb-6">Recent Activity</h3>
          <div className="space-y-4">
            {mockActivities.map(activity => (
              <div key={activity.id} className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <activity.icon className="w-4 h-4 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{activity.action}</p>
                  <p className="text-xs text-gray-500">{activity.user} • {activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Priority Alerts */}
      <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-6 shadow-lg`}>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold">Priority Alerts</h3>
          <button className="text-sm text-blue-600 hover:underline">View All</button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {mockAlerts.map(alert => (
            <div key={alert.id} className={`p-4 rounded-xl border-l-4 ${
              alert.priority === 'high' ? 'border-red-500 bg-red-50 dark:bg-red-900/20' :
              alert.priority === 'medium' ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/20' :
              'border-green-500 bg-green-50 dark:bg-green-900/20'
            }`}>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-semibold text-gray-500 mb-1">{alert.dept}</p>
                  <p className="text-sm font-medium">{alert.message}</p>
                  <p className="text-xs text-gray-500 mt-2">{alert.time}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}