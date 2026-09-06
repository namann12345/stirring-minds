import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { MessageSquare, Send, Mic, Sparkles } from 'lucide-react';

const mockChartData = [
  { month: 'Jan', deals: 20, value: 540 },
  { month: 'Feb', deals: 25, value: 675 },
  { month: 'Mar', deals: 28, value: 756 },
  { month: 'Apr', deals: 22, value: 594 },
  { month: 'May', deals: 30, value: 810 },
  { month: 'Jun', deals: 31, value: 837 }
];

const suggestedQuestions = [
  "What was Q2 sales growth?",
  "Show me HR attrition trends",
  "Compare revenue vs expenses",
  "Generate finance summary"
];

export default function AIAssistant({ theme }) {
  const isDark = theme === 'dark';
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = () => {
    if (!input.trim()) return;
    
    // Add user message
    const userMessage = { type: 'user', content: input, timestamp: new Date() };
    setMessages([...messages, userMessage]);
    setInput('');
    setIsTyping(true);
    
    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        type: 'ai',
        content: 'Based on the latest data analysis, Q2 sales performance shows a 12% increase compared to Q1. The technology sector led with 23% growth, while retail showed modest gains of 8%. Key drivers include improved customer retention and successful product launches in the enterprise segment.',
        chart: mockChartData,
        insights: [
          'Technology sector outperformed by 23%',
          'Customer retention up 15%',
          'Average deal size increased to $27K'
        ],
        recommendations: [
          'Invest more in technology vertical',
          'Expand sales team by 20%',
          'Launch customer loyalty program'
        ],
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const handleSuggestedQuestion = (question) => {
    setInput(question);
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      // Simulate voice recording
      setTimeout(() => {
        setIsRecording(false);
        setInput("What was the Q2 sales growth?");
      }, 2000);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold">AI Assistant</h2>
        <p className="text-gray-500 mt-1">Ask questions about your data in natural language</p>
      </div>
      
      <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl shadow-lg h-[600px] flex flex-col`}>
        {/* Chat Messages */}
        <div className="flex-1 p-6 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center mb-4">
                <MessageSquare className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2">How can I help you today?</h3>
              <p className="text-gray-500 mb-6">Ask me anything about your enterprise data</p>
              
              {/* Suggested Questions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl w-full">
                {suggestedQuestions.map((question, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSuggestedQuestion(question)}
                    className={`p-4 rounded-xl text-left transition-all ${
                      isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <p className="text-sm font-medium">{question}</p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-2xl rounded-2xl p-4 ${
                    msg.type === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white'
                      : isDark
                      ? 'bg-gray-700'
                      : 'bg-gray-100'
                  }`}>
                    {msg.type === 'ai' && (
                      <div className="flex items-center gap-2 mb-2">
                        <Sparkles className="w-4 h-4 text-blue-500" />
                        <span className="text-xs font-semibold text-blue-500">AI Assistant</span>
                      </div>
                    )}
                    
                    <p className="text-sm leading-relaxed">{msg.content}</p>
                    
                    {/* Insights */}
                    {msg.insights && (
                      <div className="mt-4 space-y-2">
                        <p className="text-xs font-semibold opacity-75">Key Insights:</p>
                        {msg.insights.map((insight, i) => (
                          <div key={i} className="flex items-start gap-2">
                            <span className="text-blue-500 mt-0.5">•</span>
                            <p className="text-sm">{insight}</p>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {/* Chart */}
                    {msg.chart && (
                      <div className="mt-4 bg-white rounded-xl p-4">
                        <ResponsiveContainer width="100%" height={200}>
                          <BarChart data={msg.chart}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="deals" fill="#3b82f6" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}
                    
                    {/* Recommendations */}
                    {msg.recommendations && (
                      <div className="mt-4 space-y-2">
                        <p className="text-xs font-semibold opacity-75">Recommendations:</p>
                        {msg.recommendations.map((rec, i) => (
                          <div key={i} className={`p-3 rounded-lg ${
                            isDark ? 'bg-gray-600' : 'bg-blue-50'
                          }`}>
                            <p className="text-sm">{rec}</p>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    <p className="text-xs opacity-50 mt-2">
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))}
              
              {/* Typing Indicator */}
              {isTyping && (
                <div className="flex justify-start">
                  <div className={`rounded-2xl p-4 ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className="text-xs text-gray-500">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Input Area */}
        <div className={`p-4 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type your question here..."
              className={`flex-1 px-4 py-3 rounded-xl border ${
                isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'
              } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
            />
            <button
              onClick={toggleRecording}
              className={`p-3 rounded-xl transition-all ${
                isRecording
                  ? 'bg-red-500 text-white animate-pulse'
                  : isDark
                  ? 'bg-gray-700 hover:bg-gray-600'
                  : 'bg-gray-100 hover:bg-gray-200'
              }`}
              title={isRecording ? 'Recording...' : 'Voice Input'}
            >
              <Mic className="w-5 h-5" />
            </button>
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className={`px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all ${
                !input.trim() && 'opacity-50 cursor-not-allowed'
              }`}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          
          {isRecording && (
            <div className="mt-2 flex items-center gap-2 text-sm text-red-500">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span>Recording... Click mic to stop</span>
            </div>
          )}
        </div>
      </div>

      {/* Features Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-xl p-4 shadow`}>
          <h4 className="font-semibold mb-2">Natural Language</h4>
          <p className="text-sm text-gray-500">Ask questions in plain English about your data</p>
        </div>
        <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-xl p-4 shadow`}>
          <h4 className="font-semibold mb-2">Voice Input</h4>
          <p className="text-sm text-gray-500">Use voice commands for hands-free querying</p>
        </div>
        <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-xl p-4 shadow`}>
          <h4 className="font-semibold mb-2">Visual Insights</h4>
          <p className="text-sm text-gray-500">Get charts and visualizations with answers</p>
        </div>
      </div>
    </div>
  );
}