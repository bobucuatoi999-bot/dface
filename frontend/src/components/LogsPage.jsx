import React, { useState, useEffect } from 'react'
import { logsAPI } from '../services/api'
import './LogsPage.css'

function LogsPage() {
  const [stats, setStats] = useState(null)
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState({ limit: 50 })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [statsData, logsData] = await Promise.all([
        logsAPI.getStats(),
        logsAPI.getAll(filter)
      ])
      setStats(statsData)
      setLogs(logsData)
    } catch (err) {
      console.error('Error loading data:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="logs-page">
      <h1 className="page-title">📊 Logs & Analytics</h1>
      <p className="page-subtitle">Recognition events and statistics</p>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <div className="stat-value">{stats.total_recognitions}</div>
              <div className="stat-label">Total Recognitions</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-value">{stats.unique_users}</div>
              <div className="stat-label">Unique Users</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">❓</div>
            <div className="stat-content">
              <div className="stat-value">{stats.unknown_count}</div>
              <div className="stat-label">Unknown Persons</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📈</div>
            <div className="stat-content">
              <div className="stat-value">{(stats.average_confidence * 100).toFixed(1)}%</div>
              <div className="stat-label">Avg Confidence</div>
            </div>
          </div>
        </div>
      )}

      <div className="logs-section">
        <h2>Recent Recognition Events</h2>
        <div className="logs-table">
          <div className="logs-header">
            <div>Time</div>
            <div>User</div>
            <div>Confidence</div>
            <div>Status</div>
          </div>
          {logs.length === 0 ? (
            <div className="empty-logs">No recognition events yet</div>
          ) : (
            logs.map((log) => (
              <div key={log.id} className="log-row">
                <div>{new Date(log.created_at).toLocaleString()}</div>
                <div className={log.is_unknown ? 'unknown' : 'recognized'}>
                  {log.is_unknown ? 'Unknown Person' : log.user_name || 'N/A'}
                </div>
                <div>{(log.confidence * 100).toFixed(1)}%</div>
                <div>
                  {log.is_unknown ? (
                    <span className="badge unknown-badge">Unknown</span>
                  ) : (
                    <span className="badge recognized-badge">Recognized</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default LogsPage

