import React from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { authAPI } from '../services/api'
import './Dashboard.css'

function Dashboard({ onLogout }) {
  const location = useLocation()
  const navigate = useNavigate()
  const [user, setUser] = React.useState(null)

  React.useEffect(() => {
    loadUser()
  }, [])

  const loadUser = async () => {
    try {
      const userData = await authAPI.getMe()
      setUser(userData)
    } catch (error) {
      console.error('Error loading user:', error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    onLogout()
    navigate('/login')
  }

  const navItems = [
    { path: '/register', label: '📝 Register User', icon: '👤' },
    { path: '/recognition', label: '🎥 Recognition Mode', icon: '🎬' },
    { path: '/users', label: '👥 Users', icon: '📋' },
    { path: '/logs', label: '📊 Logs & Analytics', icon: '📈' },
  ]

  return (
    <div className="dashboard">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h2>FaceStream</h2>
          {user && (
            <div className="user-info">
              <span className="user-name">{user.username}</span>
              <span className="user-role">{user.role}</span>
            </div>
          )}
        </div>
        
        <ul className="nav-menu">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={location.pathname === item.path ? 'active' : ''}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
        
        <button className="logout-btn" onClick={handleLogout}>
          🚪 Logout
        </button>
      </nav>
      
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Dashboard

