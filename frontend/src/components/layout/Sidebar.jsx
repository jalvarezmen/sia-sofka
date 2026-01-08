import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { 
  LayoutDashboard, 
  Users, 
  BookOpen, 
  UserCheck, 
  GraduationCap,
  LogOut 
} from 'lucide-react'

const Sidebar = () => {
  const location = useLocation()
  const { user, logout } = useAuth()

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/users', label: 'Usuarios', icon: Users, roles: ['Admin'] },
    { path: '/subjects', label: 'Materias', icon: BookOpen, roles: ['Admin'] },
    { path: '/enrollments', label: 'Inscripciones', icon: UserCheck, roles: ['Admin'] },
    { path: '/grades', label: 'Notas', icon: GraduationCap },
  ]

  const filteredMenuItems = menuItems.filter((item) => {
    if (!item.roles) return true
    return item.roles.includes(user?.role)
  })

  return (
    <div className="fixed inset-y-0 left-0 w-64 bg-gray-900 text-white">
      <div className="flex flex-col h-full">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold">SIA SOFKA U</h1>
          <p className="text-sm text-gray-400 mt-1">Sistema Académico</p>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-gray-800">
          <div className="mb-4 px-4 py-2 bg-gray-800 rounded-lg">
            <p className="text-sm font-medium">{user?.nombre} {user?.apellido}</p>
            <p className="text-xs text-gray-400">{user?.role}</p>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>Cerrar sesión</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default Sidebar

