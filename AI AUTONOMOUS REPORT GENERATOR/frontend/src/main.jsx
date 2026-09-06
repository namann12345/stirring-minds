// frontend/src/main.jsx
// React application entry point

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Create root and render app
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

// Hot Module Replacement (HMR) for Vite
if (import.meta.hot) {
  import.meta.hot.accept();
} 