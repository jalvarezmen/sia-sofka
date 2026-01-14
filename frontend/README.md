# SIA SOFKA U - Frontend

Frontend de la aplicación SIA SOFKA U - Sistema de Información Académica

## 🚀 Tecnologías

- **React 18** - Biblioteca de UI
- **Vite** - Build tool y dev server
- **React Router** - Enrutamiento
- **Axios** - Cliente HTTP
- **Tailwind CSS** - Framework de CSS
- **Lucide React** - Iconos

## 📁 Estructura del Proyecto

```
frontend/
├── public/              # Archivos estáticos
├── src/
│   ├── components/      # Componentes React
│   │   ├── auth/        # Componentes de autenticación
│   │   ├── layout/      # Componentes de layout
│   │   ├── modals/      # Modales
│   │   ├── dashboard/   # Páginas del dashboard
│   │   └── common/      # Componentes comunes
│   ├── context/         # Context API
│   ├── services/         # Servicios API
│   │   ├── api.js       # Cliente axios configurado
│   │   └── apiService.js # Servicios helper por entidad
│   ├── config/          # Configuración
│   ├── App.jsx          # Componente principal
│   ├── main.jsx         # Punto de entrada
│   └── index.css        # Estilos globales
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 📦 Instalación

```bash
# Instalar dependencias
npm install

# O con yarn
yarn install
```

## 🔧 Configuración

1. Copia el archivo `.env.example` a `.env`:
```bash
cp .env.example .env
```

2. Ajusta la URL de la API si es necesario:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 🛠️ Desarrollo

```bash
# Iniciar servidor de desarrollo
npm run dev

# El servidor estará disponible en http://localhost:3000
```

## 📦 Build

```bash
# Crear build de producción
npm run build

# Preview del build
npm run preview
```

## 🔐 Servicios API

El proyecto incluye dos archivos de servicios:

### `api.js`
Cliente axios configurado con:
- Interceptores para agregar tokens automáticamente
- Manejo de errores de autenticación
- Manejo de errores de red y servidor
- Timeout configurado

### `apiService.js`
Servicios helper organizados por entidad:
- `authService` - Autenticación
- `userService` - Gestión de usuarios
- `subjectService` - Gestión de materias
- `enrollmentService` - Gestión de inscripciones
- `gradeService` - Gestión de notas
- `reportService` - Generación de reportes
- `profileService` - Gestión de perfil

**Ejemplo de uso:**
```javascript
import { userService } from '../services/apiService'

// Obtener todos los usuarios
const users = await userService.getAll()

// Crear un usuario
const newUser = await userService.create(userData)
```

## ✨ Características

- ✅ Autenticación con JWT
- ✅ Dashboard con diferentes vistas según rol
- ✅ Gestión de usuarios (Admin)
- ✅ Gestión de materias (Admin)
- ✅ Gestión de inscripciones (Admin)
- ✅ Gestión de notas (Profesor/Admin)
- ✅ Diseño responsive con Tailwind CSS
- ✅ Manejo de errores robusto
- ✅ Interceptores de axios para autenticación automática

## 👥 Roles y Permisos

- **Admin**: Acceso completo a todas las funcionalidades
- **Profesor**: Puede gestionar notas de sus materias
- **Estudiante**: Solo puede ver sus propias notas

## 📝 Scripts Disponibles

- `npm run dev` - Inicia el servidor de desarrollo
- `npm run build` - Crea el build de producción
- `npm run preview` - Preview del build de producción
- `npm run lint` - Ejecuta el linter

## 🔍 Manejo de Errores

El servicio API incluye manejo automático de:
- Errores de autenticación (401) - Redirige a login
- Errores de red - Muestra mensaje amigable
- Errores del servidor (5xx) - Muestra mensaje genérico
- Errores del cliente (4xx) - Muestra mensaje del servidor
- Timeout - Manejo de peticiones que tardan mucho

## 🌐 Proxy de Desarrollo

El `vite.config.js` incluye un proxy para desarrollo que redirige las peticiones `/api` al backend en `http://localhost:8000`.

