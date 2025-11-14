import React, { useState, useEffect } from 'react'
import { usersAPI } from '../services/api'
import './UsersPage.css'

function UsersPage() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      setLoading(true)
      const data = await usersAPI.getAll()
      setUsers(data)
      setError('')
    } catch (err) {
      setError('Failed to load users')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (userId, userName) => {
    if (!window.confirm(`Delete user "${userName}"? This cannot be undone.`)) {
      return
    }

    try {
      await usersAPI.delete(userId)
      loadUsers()
    } catch (err) {
      alert('Failed to delete user')
    }
  }

  if (loading) {
    return <div className="loading">Loading users...</div>
  }

  return (
    <div className="users-page">
      <div className="page-header">
        <h1 className="page-title">👥 Registered Users</h1>
        <p className="page-subtitle">Manage users in the system</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="users-grid">
        {users.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">👤</div>
            <p>No users registered yet</p>
            <p className="empty-hint">Register a user from the Register page</p>
          </div>
        ) : (
          users.map((user) => (
            <div key={user.id} className="user-card">
              <div className="user-header">
                <div className="user-avatar">{user.name.charAt(0).toUpperCase()}</div>
                <div className="user-info">
                  <h3>{user.name}</h3>
                  {user.email && <p className="user-email">{user.email}</p>}
                  {user.employee_id && <p className="user-id">{user.employee_id}</p>}
                </div>
              </div>
              
              <div className="user-stats">
                <div className="stat-item">
                  <span className="stat-label">Face Embeddings:</span>
                  <span className="stat-value">{user.face_count}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Status:</span>
                  <span className={`stat-value ${user.is_active ? 'active' : 'inactive'}`}>
                    {user.is_active ? '🟢 Active' : '🔴 Inactive'}
                  </span>
                </div>
              </div>

              <div className="user-actions">
                <button
                  onClick={() => handleDelete(user.id, user.name)}
                  className="btn-danger btn-small"
                >
                  🗑 Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default UsersPage

