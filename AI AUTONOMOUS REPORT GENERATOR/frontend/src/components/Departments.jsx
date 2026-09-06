import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { DollarSign, Users, ShoppingCart, Package, Shield, Filter, Calendar } from 'lucide-react';

const mockKPIs = {
  finance: [
    { label: 'Total Revenue', value: '$2.4M', change: '+12.5%', positive: true },
    { label: 'Expenses', value: '$1.8M', change: '+8.2%', positive: false },
    { label: 'Net Profit', value: '$600K', change: '+18.3%', positive: true },
    { label: 'Profit Margin', value: '25%', change: '+2.1%', positive: true }
  ],
  hr: [
    { label: 'Total Employees', value: '342', change: '+5.2%', positive: true },
    { label: 'Attrition Rate', value: '8.2%', change: '-1.3%', positive: true },
    { label: 'New Hires', value: '23', change: '+15%', positive: true },
    { label: 'Satisfaction', value: '87%', change: '+3%', positive: true }
  ],
  sales: [
    { label: 'Total Deals', value: '156', change: '+22%', positive: true },
    { label: 'Conversion Rate', value: '34%', change: '+5%', positive: true },
    { label: 'Pipeline Value', value: '$4.2M', change: '+28%', positive: true },
    { label: 'Avg Deal Size', value: '$27K', change: '+8%', positive: true }
  ],
  operations: [
    { label: 'Efficiency', value: '94%', change: '+2%', positive: true },
    { label: 'Downtime', value: '2.3h', change: '-15%', positive: true },
    { label: 'Orders', value: '1,234', change: '+18%', positive: true },
    { label: 'On-Time', value: '96%', change: '+3%', positive: true }
  ],
  compliance: [
    { label: 'Audits', value: '12', change: '0%', positive: true },
    { label: 'Open Issues', value: '3', change: '-40%', positive: true },
    { label: 'Resolved', value: '89%', change: '+12%', positive: true },
    { label: 'Risk Level', value: 'Low', change: 'Stable', positive: true }
  ]
};

const mockChartData = {
  finance: [
    { month: 'Jan', revenue: 180, expenses: 140 },
    { month: 'Feb', revenue: 200, expenses: 150 },
    { month: 'Mar', revenue: 220, expenses: 160 },
    { month: 'Apr', revenue: 240, expenses: 180 },
    { month: 'May', revenue: 260, expenses: 190 },
    { month: 'Jun', revenue: 280, expenses: 200 }
  ],
  hr: [
    { month: 'Jan', hires: 5, exits: 3 },
    { month: 'Feb', hires: 8, exits: 2 },
    { month: 'Mar', hires: 6, exits: 4 },
    { month: 'Apr', hires: 7, exits: 3 },
    { month: 'May', hires: 9, exits: 5 },
    { month: 'Jun', hires: 4, exits: 3 }
  ],
  sales: [
    { month: 'Jan', deals: 20, value: 540 },
    { month: 'Feb', deals: 25, value: 675 },
    { month: 'Mar', deals: 28, value: 756 },
    { month: 'Apr', deals: 22, value: 594 },
    { month: 'May', deals: 30, value: 810 },
    { month: 'Jun', deals: 31, value: 837 }
  ],
  operations: [
    { month: 'Jan', efficiency: 91, downtime: 3.2 },
    { month: 'Feb', efficiency: 92, downtime: 2.8 },
    { month: 'Mar', efficiency: 93, downtime: 2.5 },
    { month: 'Apr', efficiency: 94, downtime: 2.3 },
    { month: 'May', efficiency: 94, downtime: 2.1 },
    { month: 'Jun', efficiency: 95, downtime: 1.9 }
  ],
  compliance: [
    { month: 'Jan', audits: 2, issues: 5 },
    { month: 'Feb', audits: 2, issues: 4 },
    { month: 'Mar', audits: 2, issues: 6 },
    { month: 'Apr', audits: 2, issues: 5 },
    { month: 'May', audits: 2, issues: 4 },
    { month: 'Jun', audits: 2, issues: 3 }
  ]
};

export default function Departments({ selectedDept, setSelectedDept, theme }) {
  const isDark = theme === 'dark';
  
  const departments = [
    { id: 'finance', name: 'Finance', icon: DollarSign, color: 'from-blue-500 to-blue-600' },
    { id: 'hr', name: 'Human Resources', icon: Users, color: 'from-green-500 to-green-600' },
    { id: 'sales', name: 'Sales & Marketing', icon: ShoppingCart, color: 'from-purple-500 to-purple-600' },
    { id: 'operations', name: 'Operations', icon: Package, color: 'from-orange-500 to-orange-600' },
    { id: 'compliance', name: 'Compliance', icon: Shield, color: 'from-red-500 to-red-600' }
  ];

  const currentKPIs = mockKPIs[selectedDept];
  const currentChart = mockChartData[selectedDept];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold">Department Dashboards</h2>
        <p className="text-gray-500 mt-1">View detailed analytics for each department</p>
      </div>
      
      {/* Department Tabs */}
      <div className="flex gap-3 overflow-x-auto pb-2">
        {departments.map(dept => {
          const isSelected = selectedDept === dept.id;
          return (
            <button
              key={dept.id}
              onClick={() => setSelectedDept(dept.id)}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl whitespace-nowrap transition-all ${
                isSelected
                  ? `bg-gradient-to-r ${dept.color} text-white shadow-lg`
                  : isDark
                  ? 'bg-gray-800 hover:bg-gray-700'
                  : 'bg-white hover:bg-gray-50'
              }`}
            >
              <dept.icon className="w-5 h-5" />
              <span className="font-medium">{dept.name}</span>
            </button>
          );
        })}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {currentKPIs.map((kpi, idx) => (
          <div key={idx} className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-6 shadow-lg`}>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-500">{kpi.label}</h3>
              <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                kpi.positive ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
              }`}>
                {kpi.change}
              </span>
            </div>
            <h4 className="text-3xl font-bold mb-1">{kpi.value}</h4>
          </div>
        ))}
      </div>

      {/* Performance Chart */}
      <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-6 shadow-lg`}>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold">Performance Trends</h3>
          <div className="flex gap-2">
            <button className={`p-2 rounded-lg ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}>
              <Filter className="w-4 h-4" />
            </button>
            <button className={`p-2 rounded-lg ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}>
              <Calendar className="w-4 h-4" />
            </button>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={350}>
          {selectedDept === 'sales' ? (
            <BarChart data={currentChart}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="deals" fill="#3b82f6" />
              <Bar dataKey="value" fill="#10b981" />
            </BarChart>
          ) : (
            <LineChart data={currentChart}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey={Object.keys(currentChart[0])[1]} stroke="#3b82f6" strokeWidth={3} />
              <Line type="monotone" dataKey={Object.keys(currentChart[0])[2]} stroke="#10b981" strokeWidth={3} />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* AI-Generated Summary */}
      <div className={`${isDark ? 'bg-gradient-to-r from-blue-900/20 to-purple-900/20 border-blue-500' : 'bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200'} border-l-4 rounded-xl p-6`}>
        <h3 className="text-lg font-bold mb-2">AI-Generated Insights</h3>
        <p className="text-sm leading-relaxed">
          {selectedDept === 'finance' && "Q2 financial performance exceeded expectations with 12.5% revenue growth. Operating margins improved to 25% through strategic cost optimization. Cash flow remains strong with $2.4M total revenue."}
          {selectedDept === 'hr' && "Workforce expansion on track with 23 new hires. Attrition rate decreased to 8.2%, below industry average. Employee satisfaction scores improved to 87% following new wellness initiatives."}
          {selectedDept === 'sales' && "Outstanding quarter with 156 deals closed, representing 22% growth. Average deal size increased to $27K. Sales pipeline robust at $4.2M with 34% conversion rate."}
          {selectedDept === 'operations' && "Operational efficiency reached 94% with significant reduction in equipment downtime. Order volume increased 18% while maintaining 96% on-time delivery rate."}
          {selectedDept === 'compliance' && "All regulatory requirements met with 12 successful audits. Issue resolution rate at 89%. Risk assessment remains at Low level with proactive monitoring in place."}
        </p>
      </div>
    </div>
  );
}