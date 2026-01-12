# CI/CD Pipeline - SIA SOFKA U

## 📋 Descripción General

Este proyecto utiliza **GitHub Actions** para ejecutar un pipeline de CI/CD automatizado que garantiza la calidad del código y las pruebas antes de integrar cambios.

## 🚀 Pipeline Workflow

El pipeline se ejecuta automáticamente en:
- **Push** a las ramas `main` y `develop`
- **Pull Requests** hacia las ramas `main` y `develop`

### Stages del Pipeline

#### 1. **Test Job**
Ejecuta pruebas en múltiples versiones de Python (3.11, 3.12) con los siguientes pasos:

- ✅ **Checkout del código**
- ✅ **Configuración de Python** (con cache de dependencias)
- ✅ **Instalación de dependencias**
- ✅ **Linting con flake8**
  - Verifica errores de sintaxis y código problemático
  - Valida complejidad del código (max 10)
  - Valida longitud de línea (max 127 caracteres)
- ✅ **Formateo con black**
  - Verifica que el código siga el estilo black
- ✅ **Type checking con mypy**
  - Valida tipos estáticos en el código
- ✅ **Ejecución de pruebas con pytest**
  - Pruebas unitarias e integración
  - Generación de cobertura de código
- ✅ **Verificación de cobertura mínima (80%)**
- ✅ **Upload de reportes de cobertura**
  - Codecov para métricas públicas
  - Artefactos HTML para revisión detallada

#### 2. **Docker Build Job**
Valida que la imagen Docker se construya correctamente:

- ✅ **Build de imagen Docker**
- ✅ **Test básico de la imagen**

## 📊 Badges

Agrega estos badges a tu README para mostrar el estado del proyecto:

```markdown
[![CI Pipeline](https://github.com/YOUR_USERNAME/sia-sofka/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/sia-sofka/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/sia-sofka/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/sia-sofka)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

**Nota:** Reemplaza `YOUR_USERNAME` con tu usuario de GitHub.

## 🔧 Configuración Local

### Pre-commit Hooks

Para ejecutar las mismas validaciones localmente antes de hacer commit:

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar los hooks
pre-commit install

# Ejecutar manualmente en todos los archivos
pre-commit run --all-files
```

Los hooks configurados ejecutan:
- Eliminación de espacios en blanco al final
- Corrección de finales de archivo
- Validación de YAML, JSON, TOML
- Detección de archivos grandes
- Black (formateo)
- Flake8 (linting)
- isort (ordenamiento de imports)
- mypy (type checking)

### Ejecutar Verificaciones Localmente

```bash
# Formatear código
black app tests

# Verificar linting
flake8 app tests

# Type checking
mypy app

# Ejecutar pruebas con cobertura
pytest --cov=app --cov-report=html --cov-report=term-missing

# Verificar cobertura mínima
coverage report --fail-under=80
```

## 📁 Archivos de Configuración

### `.github/workflows/ci.yml`
Define el workflow completo de GitHub Actions.

### `.coveragerc`
Configuración de coverage.py para reportes de cobertura:
- Archivos a incluir/excluir
- Líneas a ignorar
- Formatos de reporte (HTML, XML, terminal)

### `.pre-commit-config.yaml`
Define los hooks de pre-commit para validaciones locales.

## 🎯 Estándares de Calidad

### Cobertura de Código
- **Mínimo requerido:** 80%
- El pipeline falla si la cobertura está por debajo del umbral
- Se generan reportes HTML detallados para análisis

### Estilo de Código
- **Formateo:** Black (línea máxima 120 caracteres)
- **Linting:** Flake8 (complejidad máxima 10)
- **Import sorting:** isort (perfil black)

### Type Hints
- Validación con mypy
- Se ignoran imports faltantes para facilitar desarrollo

## 🔍 Debugging del Pipeline

### Ver logs de GitHub Actions
1. Ve a la pestaña "Actions" en tu repositorio
2. Selecciona el workflow "CI Pipeline"
3. Haz clic en el run específico para ver detalles
4. Expande cada step para ver logs detallados

### Descargar reportes de cobertura
Los reportes HTML de cobertura están disponibles como artefactos en cada run:
1. Ve al run específico en Actions
2. Scroll down hasta "Artifacts"
3. Descarga `coverage-report-{python-version}`

## 🚨 Troubleshooting

### Pipeline falla en linting
```bash
# Ejecutar black para auto-formatear
black app tests

# Verificar problemas de flake8
flake8 app tests
```

### Pipeline falla en tests
```bash
# Ejecutar tests localmente con output detallado
pytest -v

# Ejecutar un test específico
pytest tests/path/to/test.py::test_function -v
```

### Pipeline falla en cobertura
```bash
# Ver reporte de cobertura local
pytest --cov=app --cov-report=term-missing

# Identificar archivos sin cobertura
coverage report --show-missing
```

## 📚 Recursos

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
