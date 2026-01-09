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
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mb-1">
            Notas
          </h1>
          <p className="text-gray-600 text-sm">Gestiona las calificaciones académicas</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-5 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl hover:from-purple-700 hover:to-purple-800 shadow-lg hover:shadow-xl transition-all duration-200 font-semibold transform hover:scale-105"
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
            className="px-4 py-2.5 border-2 border-purple-200 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all duration-200 bg-white text-gray-700 font-medium"
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
                Estudiante
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Materia
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Nota
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Período
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Fecha
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
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
                <tr key={grade.id} className="hover:bg-purple-50 transition-colors duration-150">
                  <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                    {grade.enrollment?.estudiante?.nombre}{' '}
                    {grade.enrollment?.estudiante?.apellido}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                    {grade.enrollment?.subject?.nombre}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1.5 text-xs rounded-full font-bold shadow-md ${
                      grade.nota >= 4.5 ? 'bg-gradient-to-r from-green-500 to-green-600 text-white' :
                      grade.nota >= 3.5 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-white' :
                      'bg-gradient-to-r from-red-500 to-red-600 text-white'
                    }`}>
                      {grade.nota}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-700">{grade.periodo}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                    {grade.fecha ? new Date(grade.fecha).toLocaleDateString('es-ES') : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleEdit(grade)}
                        className="p-2 text-purple-600 hover:text-white hover:bg-purple-600 rounded-lg transition-all duration-200 hover:scale-110"
                        title="Editar"
                      >
                        <Edit className="w-5 h-5" />
                      </button>
                      {user?.role === 'Admin' && (
                        <button
                          onClick={() => handleDelete(grade.id)}
                          className="p-2 text-red-600 hover:text-white hover:bg-red-600 rounded-lg transition-all duration-200 hover:scale-110"
                          title="Eliminar"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      )}
                    </div>
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
