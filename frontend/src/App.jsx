import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking')
  const [currentView, setCurrentView] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [kpiData, setKpiData] = useState({
    revenue: 'Loading...',
    deals: 'Loading...',
    workOrders: 'Loading...',
    delayedProjects: 'Loading...'
  })
  const messagesEndRef = useRef(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    checkApiHealth()
    fetchKpiData()
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/health')
      if (response.ok) {
        setApiStatus('online')
      } else {
        setApiStatus('error')
      }
    } catch (error) {
      setApiStatus('offline')
    }
  }

  const fetchKpiData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/kpi-dashboard')
      if (response.ok) {
        const data = await response.json()
        setKpiData({
          revenue: data.revenue || 'No data available',
          deals: data.deals || '0',
          workOrders: data.workOrders || '0',
          delayedProjects: data.delayedProjects || '0'
        })
      } else {
        setKpiData({
          revenue: 'Error loading',
          deals: 'Error',
          workOrders: 'Error',
          delayedProjects: 'Error'
        })
      }
    } catch (error) {
      console.error('KPI fetch error:', error)
      setKpiData({
        revenue: 'Connection error',
        deals: '—',
        workOrders: '—',
        delayedProjects: '—'
      })
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    
    if (!input.trim()) return
    
    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: input }),
      })

      if (response.ok) {
        const data = await response.json()
        const assistantMessage = { role: 'assistant', content: data.answer }
        setMessages(prev => [...prev, assistantMessage])
      } else {
        const error = await response.json()
        const errorMessage = { 
          role: 'assistant', 
          content: `Error: ${error.detail || 'Failed to get response'}`,
          isError: true 
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      const errorMessage = { 
        role: 'assistant', 
        content: `Connection error: Unable to reach the server.`,
        isError: true 
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleQuickAction = async (query) => {
    const userMessage = { role: 'user', content: query }
    setMessages(prev => [...prev, userMessage])
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: query }),
      })

      if (response.ok) {
        const data = await response.json()
        const assistantMessage = { role: 'assistant', content: data.answer }
        setMessages(prev => [...prev, assistantMessage])
        setCurrentView('chat')
      }
    } catch (error) {
      const errorMessage = { 
        role: 'assistant', 
        content: 'Connection error: Unable to reach the server',
        isError: true 
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleGetLeadershipUpdate = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/leadership-update')
      if (response.ok) {
        const data = await response.json()
        const message = { 
          role: 'assistant', 
          content: data.report,
          isReport: true 
        }
        setMessages(prev => [...prev, message])
        setCurrentView('chat')
      } else {
        const error = await response.json()
        const errorMessage = { 
          role: 'assistant', 
          content: `Error: ${error.detail || 'Failed to generate report'}`,
          isError: true 
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      const errorMessage = { 
        role: 'assistant', 
        content: 'Connection error: Unable to reach the server',
        isError: true 
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const quickActions = [
    { label: '📊 Revenue Summary', query: 'Show me revenue summary' },
    { label: '📈 Pipeline Health', query: 'What is the pipeline health?' },
    { label: '⏳ Delayed Projects', query: 'Show me delayed projects' },
    { label: '👔 Leadership Update', query: 'Generate leadership update' },
    { label: '🔄 Compare Sectors', query: 'Compare Mining vs Railways performance' },
  ]

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>Menu</h2>
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ✕
          </button>
        </div>
        
        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentView('dashboard')}
          >
            📊 Dashboard
          </button>
          <button 
            className={`nav-item ${currentView === 'chat' ? 'active' : ''}`}
            onClick={() => setCurrentView('chat')}
          >
            💬 AI Chat
          </button>
          <button 
            className={`nav-item ${currentView === 'leadership' ? 'active' : ''}`}
            onClick={() => {
              handleGetLeadershipUpdate()
              setCurrentView('leadership')
            }}
          >
            👔 Leadership Report
          </button>
          <button 
            className={`nav-item`}
            onClick={() => setCurrentView('about')}
          >
            ℹ️ About
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className={`status-badge ${apiStatus}`}>
            <span className="status-dot"></span>
            {apiStatus === 'online' && 'Connected'}
            {apiStatus === 'offline' && 'Offline'}
            {apiStatus === 'checking' && 'Checking...'}
            {apiStatus === 'error' && 'Error'}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="top-header">
          <div className="header-left">
            <button 
              className="menu-toggle"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              ☰
            </button>
            <div className="header-title">
              <h1>Skylark Drones BI Agent</h1>
              <p>AI-Powered Business Intelligence</p>
            </div>
          </div>
          <div className={`connection-status ${apiStatus}`}>
            {apiStatus === 'online' && '🟢 Connected'}
            {apiStatus === 'offline' && '🔴 Offline'}
            {apiStatus === 'checking' && '⚪ Checking...'}
            {apiStatus === 'error' && '⚠️ Error'}
          </div>
        </header>

        {/* Dashboard View */}
        {currentView === 'dashboard' && (
          <div className="dashboard-view">
            {/* KPI Cards */}
            <section className="kpi-section">
              <h2>Key Performance Indicators</h2>
              <div className="kpi-grid">
                <div className="kpi-card revenue">
                  <div className="kpi-icon">💰</div>
                  <div className="kpi-content">
                    <h3>Revenue</h3>
                    <p className="kpi-value">{kpiData.revenue}</p>
                  </div>
                </div>

                <div className="kpi-card deals">
                  <div className="kpi-icon">🤝</div>
                  <div className="kpi-content">
                    <h3>Active Deals</h3>
                    <p className="kpi-value">{kpiData.deals}</p>
                  </div>
                </div>

                <div className="kpi-card workorders">
                  <div className="kpi-icon">📋</div>
                  <div className="kpi-content">
                    <h3>Work Orders</h3>
                    <p className="kpi-value">{kpiData.workOrders}</p>
                  </div>
                </div>

                <div className="kpi-card delayed">
                  <div className="kpi-icon">⏰</div>
                  <div className="kpi-content">
                    <h3>Delayed Projects</h3>
                    <p className="kpi-value">{kpiData.delayedProjects}</p>
                  </div>
                </div>
              </div>
            </section>

            {/* Quick Actions */}
            <section className="quick-actions-section">
              <h2>Quick Actions</h2>
              <div className="quick-actions-grid">
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    className="quick-action-btn"
                    onClick={() => handleQuickAction(action.query)}
                    disabled={loading || apiStatus === 'offline'}
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            </section>

            {/* Analytics Placeholder */}
            <section className="analytics-section">
              <h2>Analytics Overview</h2>
              <div className="analytics-placeholder">
                <p>📊 Real-time analytics will appear here</p>
              </div>
            </section>
          </div>
        )}

        {/* Chat View */}
        {currentView === 'chat' && (
          <div className="chat-view">
            <div className="chat-container">
              <div className="messages-area">
                {messages.length === 0 ? (
                  <div className="welcome-area">
                    <div className="welcome-content">
                      <h2>Welcome to Skylark BI Chat</h2>
                      <p>Ask questions about your business metrics, pipeline, revenue, and operations</p>
                    </div>
                  </div>
                ) : (
                  <div className="messages-list">
                    {messages.map((msg, index) => (
                      <div key={index} className={`message ${msg.role}`}>
                        <div className={`message-bubble ${msg.isError ? 'error' : ''} ${msg.isReport ? 'report' : ''}`}>
                          {msg.content}
                        </div>
                      </div>
                    ))}
                    {loading && (
                      <div className="message assistant loading">
                        <div className="message-bubble">
                          <span className="typing-indicator">
                            <span></span><span></span><span></span>
                          </span>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              <form className="chat-input-area" onSubmit={handleSendMessage}>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask a question about your business..."
                  disabled={loading || apiStatus === 'offline'}
                  className="chat-input"
                />
                <button 
                  type="submit" 
                  disabled={loading || !input.trim() || apiStatus === 'offline'}
                  className="send-button"
                >
                  {loading ? '...' : '➤'}
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Leadership Report View */}
        {currentView === 'leadership' && (
          <div className="report-view">
            <button 
              className="back-button"
              onClick={() => setCurrentView('dashboard')}
            >
              ← Back
            </button>
            <div className="report-content">
              {messages.length > 0 ? (
                <div className="report-display">
                  {messages.filter(m => m.isReport).map((msg, idx) => (
                    <div key={idx} className="report-text">{msg.content}</div>
                  ))}
                </div>
              ) : (
                <p>No leadership report generated yet.</p>
              )}
            </div>
          </div>
        )}

        {/* About View */}
        {currentView === 'about' && (
          <div className="about-view">
            <button 
              className="back-button"
              onClick={() => setCurrentView('dashboard')}
            >
              ← Back
            </button>
            <div className="about-content">
              <h2>About Skylark Drones BI Agent</h2>
              <p>AI-Powered Business Intelligence Dashboard</p>
              <p>Built with FastAPI, React, and OpenAI</p>
              <p>Connected to Monday.com for real-time data</p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
