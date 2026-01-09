import { useState, useEffect } from 'react'
import { userService } from '../../services/apiService'
import { Plus, Edit, Trash2 } from 'lucide-react'
import UserModal from '../modals/UserModal'
import Loading from '../common/Loading'

const Users = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await userService.getAll()
      setUsers(data)
    } catch (err) {
      setError(err.message || 'Error al cargar usuarios')
      console.error('Error fetching users:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setSelectedUser(null)
    setIsModalOpen(true)
  }

  const handleEdit = (user) => {
    setSelectedUser(user)
    setIsModalOpen(true)
  }

  const handleDelete = async (userId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar este usuario?')) {
      return
    }

    try {
      await userService.delete(userId)
      setSuccess('Usuario eliminado exitosamente')
      fetchUsers()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message || 'Error al eliminar usuario')
      setTimeout(() => setError(''), 5000)
    }
  }

  const handleModalSubmit = async (userData) => {
    try {
      setError('')
      if (selectedUser) {
        await userService.update(selectedUser.id, userData)
        setSuccess('Usuario actualizado exitosamente')
      } else {
        await userService.create(userData)
        setSuccess('Usuario creado exitosamente')
      }
      setIsModalOpen(false)
      fetchUsers()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message || 'Error al guardar usuario')
      setTimeout(() => setError(''), 5000)
    }
  }

  if (loading) {
    return <Loading />
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mb-1">
            Usuarios
          </h1>
          <p className="text-gray-600 text-sm">Gestiona los usuarios del sistema</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-5 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl hover:from-purple-700 hover:to-purple-800 shadow-lg hover:shadow-xl transition-all duration-200 font-semibold transform hover:scale-105"
        >
          <Plus className="w-5 h-5" />
          <span>Nuevo Usuario</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg mb-4 shadow-md">
          <p className="font-medium">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border-l-4 border-green-500 text-green-700 px-4 py-3 rounded-lg mb-4 shadow-md">
          <p className="font-medium">{success}</p>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gradient-to-r from-purple-600 to-purple-700">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Nombre
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Rol
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Código Institucional
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  No hay usuarios registrados
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.id} className="hover:bg-purple-50 transition-colors duration-150">
                  <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                    {user.nombre} {user.apellido}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-700">{user.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1.5 text-xs font-semibold rounded-full ${
                      user.role === 'Admin' ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white shadow-md' :
                      user.role === 'Profesor' ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md' :
                      'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-md'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {user.codigo_institucional}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleEdit(user)}
                        className="p-2 text-purple-600 hover:text-white hover:bg-purple-600 rounded-lg transition-all duration-200 hover:scale-110"
                        title="Editar"
                      >
                        <Edit className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(user.id)}
                        className="p-2 text-red-600 hover:text-white hover:bg-red-600 rounded-lg transition-all duration-200 hover:scale-110"
                        title="Eliminar"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <UserModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedUser(null)
        }}
        user={selectedUser}
        onSubmit={handleModalSubmit}
      />
    </div>
  )
}

export default Users
