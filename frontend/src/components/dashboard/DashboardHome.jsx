import { useState, useEffect } from 'react'
import { Users, BookOpen, GraduationCap, UserCheck } from 'lucide-react'
import StatsCard from '../common/StatsCard'
import { userService, subjectService, enrollmentService, gradeService } from '../../services/apiService'
import Loading from '../common/Loading'

const DashboardHome = () => {
  const [stats, setStats] = useState({
    users: 0,
    subjects: 0,
    enrollments: 0,
    grades: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      const [users, subjects, enrollments, grades] = await Promise.all([
        userService.getAll(),
        subjectService.getAll(),
        enrollmentService.getAll(),
        gradeService.getAll(),
      ])

      setStats({
        users: users.length || 0,
        subjects: subjects.length || 0,
        enrollments: enrollments.length || 0,
        grades: grades.length || 0,
      })
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <Loading />
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mb-2">
          Dashboard
        </h1>
        <p className="text-gray-600">Bienvenido al Sistema de Información Académica</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard
          title="Total Usuarios"
          value={stats.users}
          icon={Users}
          color="purple"
        />
        <StatsCard
          title="Materias"
          value={stats.subjects}
          icon={BookOpen}
          color="blue"
        />
        <StatsCard
          title="Inscripciones"
          value={stats.enrollments}
          icon={UserCheck}
          color="green"
        />
        <StatsCard
          title="Notas Registradas"
          value={stats.grades}
          icon={GraduationCap}
          color="purple"
        />
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:shadow-xl transition-shadow duration-300">
        <div className="flex items-center space-x-4 mb-4">
          <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl">
            <GraduationCap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Sistema de Información Académica SOFKA U</h2>
            <p className="text-gray-600 mt-1">Gestión académica integral</p>
          </div>
        </div>
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-gray-600 leading-relaxed">
            Administra usuarios, materias, inscripciones y notas de manera eficiente y centralizada.
          </p>
        </div>
      </div>
    </div>
  )
}

export default DashboardHome
