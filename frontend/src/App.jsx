import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Login from './components/auth/Login'
import DashboardLayout from './components/layout/DashboardLayout'
import DashboardHome from './components/dashboard/DashboardHome'
import Users from './components/dashboard/Users'
import Subjects from './components/dashboard/Subjects'
import Enrollments from './components/dashboard/Enrollments'
import Grades from './components/dashboard/Grades'
import Reports from './components/dashboard/Reports'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<DashboardHome />} />
            <Route path="users" element={<Users />} />
            <Route path="subjects" element={<Subjects />} />
            <Route path="enrollments" element={<Enrollments />} />
            <Route path="grades" element={<Grades />} />
            <Route path="reports" element={<Reports />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App

