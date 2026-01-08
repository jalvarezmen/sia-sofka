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
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard
          title="Total Usuarios"
          value={stats.users}
          icon={Users}
          color="primary"
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

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Bienvenido al Sistema</h2>
        <p className="text-gray-600">
          Sistema de Información Académica SOFKA U
        </p>
      </div>
    </div>
  )
}

export default DashboardHome
