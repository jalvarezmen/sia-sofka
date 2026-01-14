import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Mail, Lock } from 'lucide-react'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // Guardar la contraseña temporalmente para el login
    const passwordToSend = password

    const result = await login(email, passwordToSend)

    if (result.success) {
      // Limpiar el estado de la contraseña inmediatamente después del login exitoso
      setPassword('')
      setEmail('')
      navigate('/')
    } else {
      setError(result.error)
      // También limpiar la contraseña en caso de error para mayor seguridad
      setPassword('')
    }

    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-purple-50 to-purple-100 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute top-0 left-0 w-32 h-32 bg-purple-200 rounded-3xl opacity-30 transform rotate-12"></div>
      <div className="absolute top-0 right-0 w-40 h-40 bg-purple-200 rounded-full opacity-20"></div>
      <div className="absolute bottom-0 left-0 w-24 h-24 bg-purple-200 rounded-full opacity-30"></div>
      <div className="absolute bottom-0 right-0 w-32 h-32 bg-purple-200 rounded-3xl opacity-20 transform -rotate-12"></div>
      
      {/* Purple dots decoration */}
      <div className="absolute bottom-10 left-10 flex gap-2">
        <div className="w-2 h-2 bg-purple-300 rounded-full opacity-50"></div>
        <div className="w-2 h-2 bg-purple-300 rounded-full opacity-50"></div>
        <div className="w-2 h-2 bg-purple-300 rounded-full opacity-50"></div>
      </div>
      <div className="absolute left-1/2 top-1/4 transform -translate-x-1/2 flex flex-col gap-2">
        <div className="w-2 h-2 bg-purple-300 rounded-full opacity-50"></div>
        <div className="w-2 h-2 bg-purple-300 rounded-full opacity-50"></div>
        <div className="w-2 h-2 bg-purple-300 rounded-full opacity-50"></div>
      </div>

      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="flex items-center justify-center mb-6 md:mb-8">
          {/* Logo SofkaU - tries image first, then text fallback */}
          <img 
            src="/images/logo-sofkau.svg" 
            alt="SofkaU Logo" 
            className="h-16 md:h-24 lg:h-28 transition-all duration-300 hover:scale-110 hover:drop-shadow-lg cursor-pointer"
            onError={(e) => {
              // Fallback to text logo if image doesn't exist
              e.target.style.display = 'none'
              const fallback = e.target.nextElementSibling
              if (fallback) fallback.style.display = 'flex'
            }}
          />
          <div className="hidden items-center gap-1 transition-all duration-300 hover:scale-110 cursor-pointer group">
            <span className="text-4xl md:text-5xl lg:text-6xl font-bold text-blue-800 group-hover:text-blue-900 transition-colors">Sofka</span>
            <span className="text-4xl md:text-5xl lg:text-6xl font-bold text-blue-800 group-hover:text-blue-900 relative inline-block transition-colors">
              U
              {/* Graduation cap on the U */}
              <span className="absolute -top-2 md:-top-3 left-0 w-8 md:w-10 h-6 md:h-7 bg-blue-400 group-hover:bg-blue-500 rounded-sm transform rotate-12 transition-colors"></span>
              <span className="absolute -top-3 md:-top-4 left-1 w-6 md:w-7 h-1 bg-blue-500 group-hover:bg-blue-600 rounded-full transition-colors"></span>
            </span>
          </div>
        </div>

        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-8 items-center">
          {/* Left Panel - Illustration */}
          <div className="hidden md:block bg-white rounded-3xl p-6 md:p-8 shadow-xl">
            <div className="w-full h-full min-h-[500px] flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl overflow-hidden relative">
              {/* Background blur effect */}
              <div className="absolute inset-0 bg-white/30 backdrop-blur-sm"></div>
              
              {/* Group illustration with effects */}
              <div className="relative z-10 w-full h-full flex items-center justify-center p-4">
                <img 
                  src="/images/group-illustration.png" 
                  alt="SofkaU Team" 
                  className="w-full h-full object-contain brightness-105 contrast-105 animate-fade-in-up animate-float animate-pulse-glow transition-transform duration-300 hover:scale-105"
                  style={{
                    filter: 'drop-shadow(0 25px 50px -12px rgba(0, 0, 0, 0.25)) drop-shadow(0 10px 20px -5px rgba(147, 51, 234, 0.2))',
                  }}
                  onError={(e) => {
                    // Try SVG if PNG doesn't exist
                    if (e.target.src.includes('.png')) {
                      e.target.src = '/images/group-illustration.svg'
                    } else {
                      // Show placeholder if both fail
                      e.target.style.display = 'none'
                      const fallback = e.target.parentElement.nextElementSibling
                      if (fallback) fallback.style.display = 'flex'
                    }
                  }}
                />
              </div>
              
              <div className="hidden absolute inset-0 w-full h-full items-center justify-center text-gray-400 z-20" style={{ display: 'none' }}>
                <div className="text-center">
                  <div className="text-6xl mb-4">👥</div>
                  <p className="text-sm">Ilustración del equipo SofkaU</p>
                  <p className="text-xs mt-2 text-gray-500">Coloca la imagen en: /public/images/group-illustration.png</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel - Login Form */}
          <div className="bg-white rounded-3xl p-8 md:p-12 shadow-xl">
            <div className="space-y-6">
              {/* Title */}
              <div>
                <h2 className="text-4xl font-bold text-gray-900 mb-2">
                  Bienvenido Sofkiano
                </h2>
                <p className="text-gray-500 text-sm">
                  Administrador/Profesor/Estudiante
                </p>
              </div>

              {/* Error message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              {/* Login Form */}
              <form className="space-y-6" onSubmit={handleSubmit}>
                {/* Email Field */}
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Correo Electrónico
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Mail className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition"
                      placeholder="tu@email.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    Contraseña
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="password"
                      name="password"
                      type="password"
                      required
                      className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>
                </div>

                {/* Forgot Password Link */}
                <div className="flex justify-end">
                  <a 
                    href="#" 
                    className="text-sm text-purple-600 hover:text-purple-700 font-medium"
                    onClick={(e) => {
                      e.preventDefault()
                      // TODO: Implement forgot password functionality
                    }}
                  >
                    
                  </a>
                </div>

                {/* Login Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-purple-700 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-purple-800 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                >
                  {loading ? 'Iniciando sesión...' : 'Iniciar Sesión Ahora'}
                </button>

                
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
