import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './styles/widget.css'

console.log('🚀 Link-Coach Widget 시작!')
console.log('환경:', import.meta.env.MODE)
console.log('API URL:', import.meta.env.VITE_API_BASE_URL)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
