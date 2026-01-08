import { useState, useEffect } from 'react'
import { enrollmentService } from '../../services/apiService'
import { Plus, Trash2 } from 'lucide-react'
import EnrollmentModal from '../modals/EnrollmentModal'
import Loading from '../common/Loading'

const Enrollments = () => {
  const [enrollments, setEnrollments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    fetchEnrollments()
  }, [])

  const fetchEnrollments = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await enrollmentService.getAll()
      console.log('Enrollments data:', data) // Debug
      console.log('First enrollment:', data[0]) // Debug - ver estructura del primer elemento
      if (data[0]) {
        console.log('Estudiante:', data[0].estudiante) // Debug
        console.log('Subject:', data[0].subject) // Debug
      }
      setEnrollments(data)
    } catch (err) {
      setError(err.message || 'Error al cargar inscripciones')
      console.error('Error fetching enrollments:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setIsModalOpen(true)
  }

  const handleDelete = async (enrollmentId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta inscripción?')) {
      return
    }

    try {
      await enrollmentService.delete(enrollmentId)
      setSuccess('Inscripción eliminada exitosamente')
      fetchEnrollments()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message || 'Error al eliminar inscripción')
      setTimeout(() => setError(''), 5000)
    }
  }

  const handleModalSubmit = async (enrollmentData) => {
    try {
      setError('')
      await enrollmentService.create(enrollmentData)
      setSuccess('Inscripción creada exitosamente')
      setIsModalOpen(false)
      fetchEnrollments()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      // Extraer mensaje de error más específico
      let errorMessage = 'Error al crear inscripción'
      
      if (err.status === 409) {
        // Error de conflicto (duplicado)
        if (err.data?.detail) {
          const detail = err.data.detail
          if (detail.includes('already enrolled') || detail.includes('ya está inscrito')) {
            errorMessage = 'El estudiante ya está inscrito en esta materia'
          } else {
            errorMessage = detail
          }
        } else {
          errorMessage = 'El estudiante ya está inscrito en esta materia'
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
      setTimeout(() => setError(''), 5000)
    }
  }

  if (loading) {
    return <Loading />
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Inscripciones</h1>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          <span>Nueva Inscripción</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
          {success}
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Estudiante
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Materia
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Código Estudiante
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Fecha
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {enrollments.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  No hay inscripciones registradas
                </td>
              </tr>
            ) : (
              enrollments.map((enrollment) => {
                // Manejar datos relacionados que pueden ser null
                const estudianteNombre = enrollment.estudiante?.nombre || 'N/A'
                const estudianteApellido = enrollment.estudiante?.apellido || ''
                const subjectNombre = enrollment.subject?.nombre || 'N/A'
                const codigoEstudiante = enrollment.estudiante?.codigo_institucional || 'N/A'
                
                return (
                  <tr key={enrollment.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {estudianteNombre} {estudianteApellido}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {subjectNombre}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {codigoEstudiante}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {enrollment.created_at
                        ? new Date(enrollment.created_at).toLocaleDateString('es-ES')
                        : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleDelete(enrollment.id)}
                        className="text-red-600 hover:text-red-900"
                        title="Eliminar"
                      >
                        <Trash2 className="w-5 h-5 inline" />
                      </button>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      <EnrollmentModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setError('') // Limpiar errores al cerrar
        }}
        onSubmit={handleModalSubmit}
        existingEnrollments={enrollments}
      />
    </div>
  )
}

export default Enrollments
