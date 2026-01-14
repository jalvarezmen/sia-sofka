// Detectar si estamos en Docker o desarrollo local
const getApiUrl = () => {
  // Si hay una variable de entorno, usarla
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // En Docker, usar el nombre del servicio
  // En desarrollo local, usar localhost
  return window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api/v1'
    : '/api/v1';
};

export const API_URL = getApiUrl();
export const API_BASE_URL = getApiUrl(); // Alias para compatibilidad

export const USER_ROLES = {
  ADMIN: 'Admin',
  PROFESOR: 'Profesor',
  ESTUDIANTE: 'Estudiante'
};

export const MENU_ITEMS = {
  Admin: [
    { id: 'dashboard', label: 'Dashboard', icon: 'BarChart3' },
    { id: 'users', label: 'Usuarios', icon: 'Users' },
    { id: 'subjects', label: 'Materias', icon: 'BookOpen' },
    { id: 'enrollments', label: 'Matrículas', icon: 'GraduationCap' },
    { id: 'grades', label: 'Calificaciones', icon: 'FileText' },
    { id: 'reports', label: 'Reportes', icon: 'FileText' }
  ],
  Profesor: [
    { id: 'dashboard', label: 'Dashboard', icon: 'BarChart3' },
    { id: 'subjects', label: 'Mis Materias', icon: 'BookOpen' },
    { id: 'grades', label: 'Calificaciones', icon: 'FileText' },
    { id: 'reports', label: 'Reportes', icon: 'FileText' }
  ],
  Estudiante: [
    { id: 'dashboard', label: 'Dashboard', icon: 'BarChart3' },
    { id: 'subjects', label: 'Mis Materias', icon: 'BookOpen' },
    { id: 'grades', label: 'Calificaciones', icon: 'FileText' },
    { id: 'reports', label: 'Mi Reporte', icon: 'FileText' }
  ]
};