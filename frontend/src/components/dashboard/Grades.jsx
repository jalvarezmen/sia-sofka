import { useState, useEffect } from 'react'
import { gradeService, subjectService } from '../../services/apiService'
import { useAuth } from '../../context/AuthContext'
import { Plus, Edit, Trash2 } from 'lucide-react'
import GradeModal from '../modals/GradeModal'
import Loading from '../common/Loading'

const Grades = () => {
  const { user } = useAuth()
  const [grades, setGrades] = useState([])
  const [subjects, setSubjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedGrade, setSelectedGrade] = useState(null)
  const [selectedSubjectId, setSelectedSubjectId] = useState(null)
  const [filterSubjectId, setFilterSubjectId] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    if (filterSubjectId) {
      fetchGrades({ subject_id: parseInt(filterSubjectId) })
    } else {
      fetchGrades()
    }
  }, [filterSubjectId])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Si es profesor, obtener sus materias
      if (user?.role === 'Profesor') {
        const subjectsData = await subjectService.getAll()
        const mySubjects = subjectsData.filter((s) => s.profesor_id === user.id)
        setSubjects(mySubjects)
        if (mySubjects.length > 0) {
          setFilterSubjectId(mySubjects[0].id.toString())
        }
      } else {
        const subjectsData = await subjectService.getAll()
        setSubjects(subjectsData)
      }
      
      await fetchGrades()
    } catch (err) {
      setError(err.message || 'Error al cargar datos')
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchGrades = async (params = {}) => {
    try {
      setError('')
      const data = await gradeService.getAll(params)
      console.log('📊 DATOS RECIBIDOS DEL BACKEND:', JSON.stringify(data, null, 2))
      if (data.length > 0) {
        console.log('📋 PRIMERA NOTA:', data[0])
        console.log('👤 ENROLLMENT:', data[0].enrollment)
        console.log('🎓 ESTUDIANTE:', data[0].enrollment?.estudiante)
        console.log('📚 MATERIA:', data[0].enrollment?.subject)
      }
      setGrades(data)
    } catch (err) {
      setError(err.message || 'Error al cargar notas')
      console.error('Error fetching grades:', err)
    }
  }

  const handleCreate = () => {
    setSelectedGrade(null)
    setSelectedSubjectId(filterSubjectId || (subjects.length > 0 ? subjects[0].id : null))
    setIsModalOpen(true)
  }

  const handleEdit = (grade) => {
    setSelectedGrade(grade)
    setSelectedSubjectId(grade.enrollment?.subject_id || null)
    setIsModalOpen(true)
  }

  const handleDelete = async (gradeId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta nota?')) {
      return
    }

    try {
      await gradeService.delete(gradeId)
      setSuccess('Nota eliminada exitosamente')
      fetchGrades(filterSubjectId ? { subject_id: parseInt(filterSubjectId) } : {})
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message || 'Error al eliminar nota')
      setTimeout(() => setError(''), 5000)
    }
  }

  const handleModalSubmit = async (gradeData) => {
    try {
      setError('')
      if (selectedGrade) {
        await gradeService.update(selectedGrade.id, gradeData)
        setSuccess('Nota actualizada exitosamente')
      } else {
        await gradeService.create(gradeData, selectedSubjectId)
        setSuccess('Nota creada exitosamente')
      }
      setIsModalOpen(false)
      fetchGrades(filterSubjectId ? { subject_id: parseInt(filterSubjectId) } : {})
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message || 'Error al guardar nota')
      setTimeout(() => setError(''), 5000)
    }
  }

  if (loading) {
    return <Loading />
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Notas</h1>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          <span>Nueva Nota</span>
        </button>
      </div>

      {subjects.length > 0 && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Filtrar por Materia
          </label>
          <select
            value={filterSubjectId}
            onChange={(e) => setFilterSubjectId(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md"
          >
            <option value="">Todas las materias</option>
            {subjects.map((subject) => (
              <option key={subject.id} value={subject.id}>
                {subject.nombre} - {subject.codigo_institucional}
              </option>
            ))}
          </select>
        </div>
      )}

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
                Nota
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Período
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
            {grades.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                  No hay notas registradas
                </td>
              </tr>
            ) : (
              grades.map((grade) => (
                <tr key={grade.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {grade.enrollment?.estudiante?.nombre}{' '}
                    {grade.enrollment?.estudiante?.apellido}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {grade.enrollment?.subject?.nombre}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded font-semibold ${
                      grade.nota >= 4.5 ? 'bg-green-100 text-green-800' :
                      grade.nota >= 3.5 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {grade.nota}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">{grade.periodo}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {grade.fecha ? new Date(grade.fecha).toLocaleDateString('es-ES') : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => handleEdit(grade)}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                      title="Editar"
                    >
                      <Edit className="w-5 h-5 inline" />
                    </button>
                    {user?.role === 'Admin' && (
                      <button
                        onClick={() => handleDelete(grade.id)}
                        className="text-red-600 hover:text-red-900"
                        title="Eliminar"
                      >
                        <Trash2 className="w-5 h-5 inline" />
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <GradeModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedGrade(null)
        }}
        grade={selectedGrade}
        subjectId={selectedSubjectId}
        onSubmit={handleModalSubmit}
      />
    </div>
  )
}

export default Grades
