"""Script para probar la generación de reportes en PDF, HTML y JSON."""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from app.core.config import settings
from app.factories.report_factory import ReportFactory
from app.services.admin_service import AdminService
from app.services.profesor_service import ProfesorService
from app.services.estudiante_service import EstudianteService
from app.repositories.user_repository import UserRepository
from app.models.user import UserRole


async def test_report_generation():
    """Probar la generación de reportes en los tres formatos."""
    print("=" * 60)
    print("PRUEBA DE GENERACIÓN DE REPORTES")
    print("=" * 60)
    
    async for db in get_db():
        try:
            # Obtener un usuario admin para los servicios
            user_repo = UserRepository(db)
            admin = await user_repo.get_by_email("admin@sofka.edu.co")
            
            if not admin:
                print("❌ ERROR: No se encontró el usuario admin")
                print("   Ejecuta primero: python create_admin.py")
                return
            
            print(f"\n✓ Usuario admin encontrado: {admin.email}")
            
            # Obtener un estudiante para probar
            estudiantes = await user_repo.get_by_role(UserRole.ESTUDIANTE, skip=0, limit=1)
            if not estudiantes:
                print("\n⚠ ADVERTENCIA: No hay estudiantes en la base de datos")
                print("   Creando un estudiante de prueba...")
                # Aquí podrías crear un estudiante de prueba si es necesario
                return
            
            estudiante = estudiantes[0]
            print(f"✓ Estudiante encontrado: {estudiante.nombre} {estudiante.apellido}")
            
            # Probar generación de reporte de estudiante
            print("\n" + "-" * 60)
            print("1. PROBANDO REPORTE DE ESTUDIANTE")
            print("-" * 60)
            
            admin_service = AdminService(db, admin)
            
            # Probar JSON
            print("\n  → Generando reporte JSON...")
            try:
                json_report = await admin_service.generate_student_report(estudiante.id, "json")
                print(f"    ✓ JSON generado: {json_report['filename']}")
                print(f"    ✓ Tipo de contenido: {json_report['content_type']}")
                print(f"    ✓ Tamaño: {len(json_report['content'])} bytes")
            except Exception as e:
                print(f"    ❌ Error generando JSON: {e}")
            
            # Probar HTML
            print("\n  → Generando reporte HTML...")
            try:
                html_report = await admin_service.generate_student_report(estudiante.id, "html")
                print(f"    ✓ HTML generado: {html_report['filename']}")
                print(f"    ✓ Tipo de contenido: {html_report['content_type']}")
                print(f"    ✓ Tamaño: {len(html_report['content'])} bytes")
            except Exception as e:
                print(f"    ❌ Error generando HTML: {e}")
            
            # Probar PDF
            print("\n  → Generando reporte PDF...")
            try:
                pdf_report = await admin_service.generate_student_report(estudiante.id, "pdf")
                print(f"    ✓ PDF generado: {pdf_report['filename']}")
                print(f"    ✓ Tipo de contenido: {pdf_report['content_type']}")
                print(f"    ✓ Tamaño: {len(pdf_report['content'])} bytes")
            except Exception as e:
                print(f"    ❌ Error generando PDF: {e}")
            
            # Probar Factory Method directamente
            print("\n" + "-" * 60)
            print("2. PROBANDO FACTORY METHOD DIRECTAMENTE")
            print("-" * 60)
            
            test_data = {
                "estudiante": {
                    "nombre": "Juan",
                    "apellido": "Pérez",
                    "codigo_institucional": "EST-2026-0001",
                    "programa_academico": "Ingeniería de Software"
                },
                "subjects": [
                    {
                        "subject": {
                            "nombre": "Matemáticas",
                            "codigo_institucional": "MATH-001",
                            "numero_creditos": 3
                        },
                        "average": 4.5
                    }
                ]
            }
            
            for format_type in ["json", "html", "pdf"]:
                print(f"\n  → Probando generador {format_type.upper()}...")
                try:
                    generator = ReportFactory.create_generator(format_type)
                    report = generator.generate(test_data)
                    print(f"    ✓ {format_type.upper()} generado: {report['filename']}")
                    print(f"    ✓ Tipo: {report['content_type']}")
                    print(f"    ✓ Tamaño: {len(report['content'])} bytes")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
            
            print("\n" + "=" * 60)
            print("✓ PRUEBAS COMPLETADAS")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ ERROR GENERAL: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break


if __name__ == "__main__":
    asyncio.run(test_report_generation())

