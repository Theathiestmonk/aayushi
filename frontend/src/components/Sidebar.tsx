import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  BarChart3, 
  User, 
  Settings,
  Utensils,
  Target,
  Activity,
  Brain
} from 'lucide-react'

const Sidebar: React.FC = () => {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Diet Plans', href: '/diet-plans', icon: Utensils },
    { name: 'AI Dietitian', href: '/diet-planner', icon: Brain },
    { name: 'Tracking', href: '/tracking', icon: BarChart3 },
    { name: 'Goals', href: '/goals', icon: Target },
    { name: 'Activity', href: '/activity', icon: Activity },
    { name: 'Profile', href: '/profile', icon: User },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  return (
    <div className="w-64 bg-white shadow-sm border-r border-gray-200 min-h-screen">
      <div className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Navigation</h2>
        <nav className="space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-green-100 text-green-700 border-r-2 border-green-500'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.name}</span>
              </Link>
            )
          })}
        </nav>
      </div>
    </div>
  )
}

export default Sidebar
