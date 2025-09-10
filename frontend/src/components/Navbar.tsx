import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Bell, User, LogOut } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import LogoutConfirmation from './ui/LogoutConfirmation'

const Navbar: React.FC = () => {
  const navigate = useNavigate()
  const { logout, user } = useAuthStore()
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false)

  // Debug user data
  console.log('🔍 Navbar: User data:', user)
  console.log('🔍 Navbar: Display name will be:', user?.full_name || user?.username || user?.email?.split('@')[0] || 'User')

  const handleLogoutClick = () => {
    setShowLogoutConfirm(true)
  }

  const handleLogoutConfirm = async () => {
    try {
      await logout()
      navigate('/login')
    } catch (error) {
      console.error('Logout failed:', error)
      // Still navigate to login even if logout fails
      navigate('/login')
    }
    // Close the popup immediately after logout starts
    setShowLogoutConfirm(false)
  }

  const handleLogoutCancel = () => {
    setShowLogoutConfirm(false)
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <span className="text-xl font-bold text-gray-900">Dietitian</span>
            </Link>
          </div>

          {/* Navigation Items */}
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-700 hover:text-green-600 px-3 py-2 rounded-md text-sm font-medium">
              Dashboard
            </Link>
            <Link to="/diet-plans" className="text-gray-700 hover:text-green-600 px-3 py-2 rounded-md text-sm font-medium">
              Diet Plans
            </Link>
            <Link to="/tracking" className="text-gray-700 hover:text-green-600 px-3 py-2 rounded-md text-sm font-medium">
              Tracking
            </Link>
            <Link to="/profile" className="text-gray-700 hover:text-green-600 px-3 py-2 rounded-md text-sm font-medium">
              Profile
            </Link>
          </div>

          {/* Right Side */}
          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-400 hover:text-gray-600">
              <Bell className="w-5 h-5" />
            </button>
            <div className="relative">
              <button className="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
                <User className="w-5 h-5" />
                <span className="hidden md:block text-sm font-medium">
                  {user?.full_name || user?.username || user?.email?.split('@')[0] || 'User'}
                </span>
              </button>
            </div>
            <button
              onClick={handleLogoutClick}
              className="flex items-center space-x-2 text-gray-700 hover:text-red-600 p-2 rounded-md hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden md:block text-sm">Logout</span>
            </button>
          </div>
        </div>
      </div>

      {/* Logout Confirmation Popup */}
      <LogoutConfirmation
        isOpen={showLogoutConfirm}
        onClose={handleLogoutCancel}
        onConfirm={handleLogoutConfirm}
      />
    </nav>
  )
}

export default Navbar




