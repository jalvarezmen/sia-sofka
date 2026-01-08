import { useState, useEffect } from 'react'
import { subjectService } from '../../services/apiService'
import { Plus, Edit, Trash2 } from 'lucide-react'
import SubjectModal from '../modals/SubjectModal'
import Loading from '../common/Loading'

const Subjects = () => {
  const [subjects, setSubjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedSubject, setSelectedSubject] = useState(null)

  useEffect(() => {
    fetchSubjects()
  }, [])

  const fetchSubjects = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await subjectService.getAll()
      setSubjects(data)
    } catch (err) {
      setError(err.message || 'Error al cargar materias')
      console.error('Error fetching subjects:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setSelectedSubject(null)
    setIsModalOpen(true)
  }

  const handleEdit = (subject) => {
    setSelectedSubject(subject)
    setIsModalOpen(true)
  }

  const handleDelete = async (subjectId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta materia?')) {
      return
    }

    try {
      await subjectService.delete(subjectId)
      setSuccess('Materia eliminada exitosamente')
      fetchSubjects()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message || 'Error al eliminar materia')
      setTimeout(() => setError(''), 5000)
    }
  }

  const handleModalSubmit = async (subjectData) => {
    try {
      setError('')
      if (selectedSubject) {
        await subjectService.update(selectedSubject.id, subjectData)
        setSuccess('Materia actualizada exitosamente')
      } else {
        await subjectService.create(subjectData)
        setSuccess('Materia creada exitosamente')
      }
      setIsModalOpen(false)
      fetchSubjects()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message || 'Error al guardar materia')
      setTimeout(() => setError(''), 5000)
    }
  }

  if (loading) {
    return <Loading />
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Materias</h1>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          <span>Nueva Materia</span>
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
                Nombre
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Código
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Créditos
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Horario
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Profesor
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {subjects.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                  No hay materias registradas
                </td>
              </tr>
            ) : (
              subjects.map((subject) => (
                <tr key={subject.id}>
                  <td className="px-6 py-4 whitespace-nowrap">{subject.nombre}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {subject.codigo_institucional}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {subject.numero_creditos}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {subject.horario || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {subject.profesor?.nombre} {subject.profesor?.apellido}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => handleEdit(subject)}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                      title="Editar"
                    >
                      <Edit className="w-5 h-5 inline" />
                    </button>
                    <button
                      onClick={() => handleDelete(subject.id)}
                      className="text-red-600 hover:text-red-900"
                      title="Eliminar"
                    >
                      <Trash2 className="w-5 h-5 inline" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <SubjectModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedSubject(null)
        }}
        subject={selectedSubject}
        onSubmit={handleModalSubmit}
      />
    </div>
  )
}

export default Subjects
