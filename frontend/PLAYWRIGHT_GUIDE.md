# 🎭 Playwright Testing Guide - SIA SOFKA

## 📋 Tabla de Contenido

1. [Instalación](#instalación)
2. [Configuración](#configuración)
3. [Ejecutar Tests](#ejecutar-tests)
4. [Estructura de Tests](#estructura-de-tests)
5. [Escribir Tests](#escribir-tests)
6. [CI/CD](#cicd)
7. [Troubleshooting](#troubleshooting)

## 📦 Instalación

### 1. Instalar Playwright

```powershell
cd frontend
npm install -D @playwright/test
```

### 2. Instalar Navegadores

```powershell
npx playwright install
```

Esto instalará:
- ✅ Chromium (Chrome/Edge)
- ✅ Firefox
- ✅ WebKit (Safari)

### 3. Verificar Instalación

```powershell
npx playwright --version
```

## ⚙️ Configuración

### Archivo de Configuración: `playwright.config.js`

```javascript
- Base URL: http://localhost:3000 (frontend)
- API URL: http://localhost:8000 (backend FastAPI)
- Timeout: 30 segundos
- Retries: 2 (solo en CI)
- Screenshots: Solo en fallos
- Videos: Solo en fallos
```

### Variables de Entorno

Puedes sobrescribir la configuración con variables de entorno:

```powershell
$env:BASE_URL="http://localhost:3000"
$env:API_URL="http://localhost:8080"
npm run test:e2e
```

## 🚀 Ejecutar Tests

### Comandos Disponibles

```powershell
# Ejecutar todos los tests (headless)
npm run test:e2e

# Ejecutar con interfaz UI (recomendado para desarrollo)
npm run test:e2e:ui

# Ejecutar con navegador visible
npm run test:e2e:headed

# Ejecutar tests específicos
npm run test:e2e auth.spec.js

# Ejecutar en modo debug
npm run test:e2e:debug

# Ver reporte HTML
npm run test:e2e:report

# Generar código automáticamente (record & play)
npm run test:e2e:codegen

# O especificar puerto manualmente
npx playwright codegen http://localhost:3000
```

### Ejecutar en Navegadores Específicos

```powershell
# Solo Chrome
npx playwright test --project=chromium

# Solo Firefox
npx playwright test --project=firefox

# Solo Safari
npx playwright test --project=webkit

# Chrome móvil
npx playwright test --project="Mobile Chrome"
```

### Ejecutar Tests con Filtros

```powershell
# Por nombre de test
npx playwright test -g "should login"

# Por archivo
npx playwright test tests/e2e/auth.spec.js

# Por directorio
npx playwright test tests/e2e/
```

## 📁 Estructura de Tests

```
frontend/
├── playwright.config.js          # Configuración principal
├── tests/
│   ├── e2e/                      # Tests end-to-end
│   │   ├── auth.spec.js          # Tests de autenticación
│   │   ├── users.spec.js         # Tests de usuarios
│   │   ├── subjects.spec.js      # Tests de materias
│   │   ├── grades.spec.js        # Tests de notas
│   │   ├── enrollments.spec.js   # Tests de inscripciones
│   │   └── navigation.spec.js    # Tests de navegación
│   └── fixtures/
│       └── auth.js               # Fixtures reutilizables
├── playwright-report/            # Reportes HTML (generado)
└── test-results/                 # Screenshots y videos (generado)
```

## ✍️ Escribir Tests

### Anatomía de un Test

```javascript
import { test, expect } from '../fixtures/auth.js';

test.describe('Feature Name', () => {
  // Setup antes de cada test
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    // 1. Arrange - Preparar
    await page.goto('/users');
    
    // 2. Act - Actuar
    await page.click('button:has-text("Crear")');
    await page.fill('input[name="nombre"]', 'Juan');
    await page.click('button[type="submit"]');
    
    // 3. Assert - Verificar
    await expect(page.locator('text=Juan')).toBeVisible();
  });
});
```

### Fixtures Disponibles

#### 1. `authenticatedPage` - Usuario Admin autenticado

```javascript
test('should access admin panel', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/admin');
  await expect(authenticatedPage.locator('h1')).toContainText('Admin');
});
```

#### 2. `profesorPage` - Usuario Profesor autenticado

```javascript
test('should create subject', async ({ profesorPage }) => {
  await profesorPage.goto('/subjects');
  // ... crear materia
});
```

#### 3. `estudiantePage` - Usuario Estudiante autenticado

```javascript
test('should view grades', async ({ estudiantePage }) => {
  await estudiantePage.goto('/grades');
  // ... ver notas
});
```

### Selectores Comunes

```javascript
// Por texto
page.click('button:has-text("Crear")');
page.locator('text=Bienvenido');

// Por atributo name
page.fill('input[name="email"]', 'test@test.com');

// Por tipo
page.fill('input[type="password"]', 'password123');

// Por placeholder
page.fill('input[placeholder="Buscar..."]', 'Juan');

// Por data-testid (recomendado)
page.click('[data-testid="create-button"]');

// Combinados
page.click('button[type="submit"]:has-text("Guardar")');

// Nth element
page.click('button >> nth=0'); // Primer botón
page.click('button >> nth=-1'); // Último botón
```

### Assertions Comunes

```javascript
// Visibilidad
await expect(page.locator('h1')).toBeVisible();
await expect(page.locator('.loading')).not.toBeVisible();

// Texto
await expect(page.locator('h1')).toHaveText('Dashboard');
await expect(page.locator('h1')).toContainText('Dash');

// URL
await expect(page).toHaveURL(/.*dashboard/);
await expect(page).toHaveURL('http://localhost:3000/dashboard');

// Conteo
await expect(page.locator('tr')).toHaveCount(5);

// Atributos
await expect(page.locator('input')).toHaveAttribute('disabled');
await expect(page.locator('input')).toHaveValue('Juan');

// Clase CSS
await expect(page.locator('button')).toHaveClass(/active/);
```

### Esperas y Timeouts

```javascript
// Esperar selector
await page.waitForSelector('table tbody tr');

// Esperar navegación
await page.waitForURL('**/dashboard');

// Esperar respuesta API
await page.waitForResponse(response => 
  response.url().includes('/api/users') && response.status() === 200
);

// Esperar timeout específico
await page.waitForTimeout(1000); // Solo para debugging

// Timeout personalizado
await page.click('button', { timeout: 5000 });
```

### Interacciones Avanzadas

```javascript
// Select dropdown
await page.selectOption('select[name="role"]', 'Profesor');
await page.selectOption('select[name="role"]', { index: 1 });

// Checkbox
await page.check('input[type="checkbox"]');
await page.uncheck('input[type="checkbox"]');

// Radio button
await page.click('input[value="opcion1"]');

// Upload file
await page.setInputFiles('input[type="file"]', 'path/to/file.pdf');

// Hover
await page.hover('button');

// Double click
await page.dblclick('button');

// Right click
await page.click('button', { button: 'right' });

// Keyboard
await page.keyboard.press('Enter');
await page.keyboard.type('Hello World');
```

## 🎯 Mejores Prácticas

### 1. Usar data-testid para selectores estables

```html
<!-- HTML -->
<button data-testid="create-user-btn">Crear Usuario</button>

<!-- Test -->
await page.click('[data-testid="create-user-btn"]');
```

### 2. Agrupar tests relacionados

```javascript
test.describe('User Management', () => {
  test.describe('Create User', () => {
    test('should create admin user', async ({ page }) => {});
    test('should create profesor user', async ({ page }) => {});
  });
});
```

### 3. Usar Page Object Model para tests complejos

```javascript
// pages/LoginPage.js
export class LoginPage {
  constructor(page) {
    this.page = page;
    this.emailInput = page.locator('input[name="email"]');
    this.passwordInput = page.locator('input[name="password"]');
    this.submitButton = page.locator('button[type="submit"]');
  }

  async login(email, password) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

// En el test
import { LoginPage } from '../pages/LoginPage';

test('should login', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.login('admin@test.com', 'password');
});
```

### 4. Aislar tests (no depender de otros tests)

```javascript
// ❌ MAL - Depende del test anterior
test('create user', async ({ page }) => {
  await page.click('button:has-text("Crear")');
});

test('edit user', async ({ page }) => {
  // Asume que el usuario del test anterior existe
  await page.click('button:has-text("Editar")');
});

// ✅ BIEN - Cada test es independiente
test('edit user', async ({ page }) => {
  // Crear usuario primero
  await createTestUser(page, 'Juan');
  
  // Ahora editarlo
  await page.click('button:has-text("Editar")');
});
```

## 🔄 CI/CD

### GitHub Actions

Crea `.github/workflows/playwright.yml`:

```yaml
name: Playwright Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - uses: actions/setup-node@v3
      with:
        node-version: 18
        
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
        
    - name: Install Playwright Browsers
      run: |
        cd frontend
        npx playwright install --with-deps
        
    - name: Run Playwright tests
      run: |
        cd frontend
        npm run test:e2e
        
    - uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: frontend/playwright-report/
        retention-days: 30
```

## 🐛 Troubleshooting

### Problema: Tests fallan aleatoriamente

**Solución**: Aumentar timeouts

```javascript
// En playwright.config.js
use: {
  actionTimeout: 15000, // De 10s a 15s
}

// O en test específico
await page.click('button', { timeout: 15000 });
```

### Problema: No encuentra selectores

**Solución**: Usar Playwright Inspector

```powershell
npm run test:e2e:debug
```

O generar código automáticamente:

```powershell
npm run test:e2e:codegen
```

### Problema: Tests lentos

**Solución**: Ejecutar en paralelo

```javascript
// playwright.config.js
export default defineConfig({
  workers: 4, // Número de workers paralelos
});
```

### Problema: Screenshots no se guardan

**Solución**: Verificar configuración

```javascript
// playwright.config.js
use: {
  screenshot: 'only-on-failure', // o 'on'
  video: 'retain-on-failure',    // o 'on'
}
```

### Problema: Backend no está corriendo

**Solución**: Iniciar backend primero

```powershell
# Terminal 1 - Backend
cd backend
docker-compose up

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - Tests
cd frontend
npm run test:e2e
```

## 📊 Reportes

### HTML Report

```powershell
npm run test:e2e:report
```

Abre automáticamente en el navegador con:
- ✅ Tests pasados/fallados
- 📸 Screenshots
- 🎥 Videos
- 📝 Logs de consola
- 🌐 Traces interactivos

### JSON Report

Los resultados también se guardan en `playwright-results.json` para integración con otras herramientas.

## 🎓 Recursos Adicionales

- [Documentación Oficial Playwright](https://playwright.dev)
- [API Reference](https://playwright.dev/docs/api/class-playwright)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Selector Guide](https://playwright.dev/docs/selectors)
- [Debugging Guide](https://playwright.dev/docs/debug)

## 📝 Notas Finales

### Tests Incluidos

1. **auth.spec.js** (7 tests)
   - Login Admin, Profesor, Estudiante
   - Logout
   - Validaciones
   - Errores

2. **users.spec.js** (8 tests)
   - CRUD de usuarios
   - Filtros y búsqueda
   - Validaciones

3. **subjects.spec.js** (7 tests)
   - CRUD de materias
   - Validaciones de créditos

4. **grades.spec.js** (9 tests)
   - CRUD de notas
   - Validación rango 0-5
   - Vista estudiante vs profesor

5. **enrollments.spec.js** (8 tests)
   - CRUD de inscripciones
   - Prevención duplicados
   - Filtros

6. **navigation.spec.js** (7 tests)
   - Navegación entre secciones
   - Permisos por rol
   - Rutas protegidas
   - 404

**Total: 46 tests E2E** ✅

### Tiempo Estimado de Ejecución

- **Local (headless)**: ~2-3 minutos
- **Local (headed)**: ~3-4 minutos
- **CI/CD**: ~4-5 minutos

### Próximos Pasos

1. Instalar Playwright
2. Ajustar selectores según tu HTML real
3. Agregar data-testid a componentes clave
4. Ejecutar tests
5. Ajustar según resultados
6. Integrar en CI/CD

¡Listo para testing profesional! 🚀
