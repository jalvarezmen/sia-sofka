# 🚀 Quick Start - Playwright Tests

## Instalación Rápida

```powershell
cd frontend
npm install -D @playwright/test
npx playwright install
```

## Ejecutar Tests

```powershell
# Modo UI (recomendado para desarrollo)
npm run test:e2e:ui

# Headless (para CI/CD)
npm run test:e2e

# Con navegador visible
npm run test:e2e:headed

# Ver reporte
npm run test:e2e:report
```

## Requisitos Previos

1. **Backend corriendo** en `http://localhost:8000`
2. **Frontend corriendo** en `http://localhost:5173`

### Iniciar Backend

```powershell
cd backend
docker-compose up
```

### Iniciar Frontend

```powershell
cd frontend
npm run dev
```

## Tests Incluidos

✅ **46 tests E2E** cubriendo:

- 🔐 Autenticación (login/logout)
- 👥 Gestión de usuarios (CRUD)
- 📚 Gestión de materias (CRUD)
- 📊 Gestión de notas (CRUD)
- 📝 Inscripciones (CRUD)
- 🧭 Navegación y permisos

## Estructura

```
frontend/
├── playwright.config.js          # Configuración
├── tests/
│   ├── e2e/                      # Tests
│   │   ├── auth.spec.js
│   │   ├── users.spec.js
│   │   ├── subjects.spec.js
│   │   ├── grades.spec.js
│   │   ├── enrollments.spec.js
│   │   └── navigation.spec.js
│   └── fixtures/
│       └── auth.js               # Helpers
└── PLAYWRIGHT_GUIDE.md           # Documentación completa
```

## Troubleshooting

### No encuentra selectores?

```powershell
# Genera código automáticamente
npm run test:e2e:codegen
```

### Tests fallan?

```powershell
# Modo debug paso a paso
npm run test:e2e:debug
```

### Ver qué pasó?

```powershell
# Ver reporte con screenshots y videos
npm run test:e2e:report
```

## Siguiente Paso

📖 Lee la [Guía Completa](PLAYWRIGHT_GUIDE.md) para:
- Escribir nuevos tests
- Mejores prácticas
- CI/CD
- Troubleshooting avanzado

## CI/CD

Los tests se ejecutan automáticamente en:
- ✅ Push a `main` o `develop`
- ✅ Pull Requests

Ver configuración en `.github/workflows/playwright.yml`

---

**¿Preguntas?** Consulta [PLAYWRIGHT_GUIDE.md](PLAYWRIGHT_GUIDE.md)
