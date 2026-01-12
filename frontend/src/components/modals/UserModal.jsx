import { useState, useEffect } from 'react'
import { X } from 'lucide-react'

const UserModal = ({ isOpen, onClose, user, onSubmit }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    nombre: '',
    apellido: '',
    role: 'Estudiante',
    fecha_nacimiento: '',
    numero_contacto: '',
    programa_academico: '',
    ciudad_residencia: '',
    area_ensenanza: '',
  })
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (user) {
      setFormData({
        email: user.email || '',
        password: '', // No mostrar password existente
        nombre: user.nombre || '',
        apellido: user.apellido || '',
        role: user.role || 'Estudiante',
        fecha_nacimiento: user.fecha_nacimiento || '',
        numero_contacto: user.numero_contacto || '',
        programa_academico: user.programa_academico || '',
        ciudad_residencia: user.ciudad_residencia || '',
        area_ensenanza: user.area_ensenanza || '',
      })
    } else {
      // Reset form for new user
      setFormData({
        email: '',
        password: '',
        nombre: '',
        apellido: '',
        role: 'Estudiante',
        fecha_nacimiento: '',
        numero_contacto: '',
        programa_academico: '',
        ciudad_residencia: '',
        area_ensenanza: '',
      })
    }
    setErrors({})
  }, [user, isOpen])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    // Clear error when user types
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }))
    }
  }

  const validate = () => {
    const newErrors = {}
    
    if (!formData.email) newErrors.email = 'El email es requerido'
    if (!formData.nombre) newErrors.nombre = 'El nombre es requerido'
    if (!formData.apellido) newErrors.apellido = 'El apellido es requerido'
    if (!user && !formData.password) newErrors.password = 'La contraseña es requerida'
    if (formData.role === 'Estudiante' && !formData.programa_academico) {
      newErrors.programa_academico = 'El programa académico es requerido para estudiantes'
    }
    if (formData.role === 'Profesor' && !formData.area_ensenanza) {
      newErrors.area_ensenanza = 'El área de enseñanza es requerida para profesores'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validate()) {
      // Remove password if editing and not provided
      const dataToSubmit = { ...formData }
      if (user && !dataToSubmit.password) {
        delete dataToSubmit.password
      }
      onSubmit(dataToSubmit)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {user ? 'Editar Usuario' : 'Nuevo Usuario'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email *
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                disabled={!!user}
                className={`w-full px-3 py-2 border rounded-md ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                } ${user ? 'bg-gray-100' : ''}`}
                required
              />
              {errors.email && (
                <p className="text-red-500 text-xs mt-1">{errors.email}</p>
              )}
            </div>

            {!user && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contraseña *
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-md ${
                    errors.password ? 'border-red-500' : 'border-gray-300'
                  }`}
                  required={!user}
                />
                {errors.password && (
                  <p className="text-red-500 text-xs mt-1">{errors.password}</p>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre *
              </label>
              <input
                type="text"
                name="nombre"
                value={formData.nombre}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${
                  errors.nombre ? 'border-red-500' : 'border-gray-300'
                }`}
                required
              />
              {errors.nombre && (
                <p className="text-red-500 text-xs mt-1">{errors.nombre}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Apellido *
              </label>
              <input
                type="text"
                name="apellido"
                value={formData.apellido}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${
                  errors.apellido ? 'border-red-500' : 'border-gray-300'
                }`}
                required
              />
              {errors.apellido && (
                <p className="text-red-500 text-xs mt-1">{errors.apellido}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rol *
              </label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                disabled={!!user}
                className={`w-full px-3 py-2 border rounded-md ${
                  user ? 'bg-gray-100' : ''
                }`}
              >
                <option value="Estudiante">Estudiante</option>
                <option value="Profesor">Profesor</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha de Nacimiento
              </label>
              <input
                type="date"
                name="fecha_nacimiento"
                value={formData.fecha_nacimiento}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Número de Contacto
              </label>
              <input
                type="text"
                name="numero_contacto"
                value={formData.numero_contacto}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>

            {formData.role === 'Estudiante' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Programa Académico *
                </label>
                <input
                  type="text"
                  name="programa_academico"
                  value={formData.programa_academico}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-md ${
                    errors.programa_academico ? 'border-red-500' : 'border-gray-300'
                  }`}
                  required={formData.role === 'Estudiante'}
                />
                {errors.programa_academico && (
                  <p className="text-red-500 text-xs mt-1">{errors.programa_academico}</p>
                )}
              </div>
            )}

            {formData.role === 'Estudiante' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ciudad de Residencia
                </label>
                <input
                  type="text"
                  name="ciudad_residencia"
                  value={formData.ciudad_residencia}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
            )}

            {formData.role === 'Profesor' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Área de Enseñanza *
                </label>
                <input
                  type="text"
                  name="area_ensenanza"
                  value={formData.area_ensenanza}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-md ${
                    errors.area_ensenanza ? 'border-red-500' : 'border-gray-300'
                  }`}
                  required={formData.role === 'Profesor'}
                />
                {errors.area_ensenanza && (
                  <p className="text-red-500 text-xs mt-1">{errors.area_ensenanza}</p>
                )}
              </div>
            )}
          </div>

          <div className="flex justify-end space-x-2 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-white bg-blue-600 rounded hover:bg-blue-700"
            >
              {user ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default UserModal
