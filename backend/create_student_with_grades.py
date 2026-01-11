"""Script para crear un estudiante, asignarle materias y notas."""

import asyncio
import sys
from app.core.database import AsyncSessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash
from datetime import date
from sqlalchemy import select


async def create_student_with_grades():
    """Crear estudiante, asignar materias y crear notas."""
    # Crear tablas si no existen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Verificar si ya existe el estudiante
        from app.repositories.user_repository import UserRepository
        user_repo = UserRepository(session)
        existing_student = await user_repo.get_by_email("carlos.estudiante@sofka.edu.co")
        
        if existing_student:
            print("[INFO] Ya existe un estudiante con el email carlos.estudiante@sofka.edu.co")
            print(f"   ID: {existing_student.id}")
            print(f"   Código: {existing_student.codigo_institucional}")
            estudiante_id = existing_student.id
        else:
            # Crear estudiante
            codigo = await generar_codigo_institucional(session, "Estudiante")
            estudiante = User(
                email="carlos.estudiante@sofka.edu.co",
                password_hash=get_password_hash("estudiante123"),
                role=UserRole.ESTUDIANTE,
                nombre="Carlos",
                apellido="Estudiante",
                codigo_institucional=codigo,
                fecha_nacimiento=date(2002, 5, 15),
                numero_contacto="3001234567",
                programa_academico="Ingeniería de Sistemas",
                ciudad_residencia="Bogotá",
            )
            session.add(estudiante)
            await session.commit()
            await session.refresh(estudiante)
            estudiante_id = estudiante.id
            print("=" * 60)
            print("[OK] ESTUDIANTE CREADO EXITOSAMENTE")
            print("=" * 60)
            print(f"Email: {estudiante.email}")
            print(f"Password: estudiante123")
            print(f"Código Institucional: {estudiante.codigo_institucional}")
            print(f"ID: {estudiante_id}")
            print()
        
        # Obtener materias disponibles (IDs 1-6)
        from app.models.subject import Subject
        materias_query = select(Subject).where(Subject.id.in_([1, 2, 3, 4, 5, 6]))
        result = await session.execute(materias_query)
        materias = result.scalars().all()
        
        if len(materias) == 0:
            print("[ERROR] No se encontraron materias. Verifica que la base de datos tenga materias creadas.")
            print("        Ejecuta primero el script de poblacion de datos o crea materias manualmente.")
            return
        
        if len(materias) < 6:
            print(f"[INFO] Advertencia: Solo se encontraron {len(materias)} materias. Se asignaran las disponibles.")
        
        # Verificar enrollments existentes
        from app.repositories.enrollment_repository import EnrollmentRepository
        enrollment_repo = EnrollmentRepository(session)
        
        enrollments_creados = []
        for materia in materias:
            # Verificar si ya existe el enrollment
            existing_enrollment = await enrollment_repo.get_by_estudiante_and_subject(
                estudiante_id, materia.id
            )
            
            if existing_enrollment:
                print(f"  [INFO] Ya existe enrollment para {materia.nombre}")
                enrollments_creados.append(existing_enrollment)
            else:
                enrollment = Enrollment(
                    estudiante_id=estudiante_id,
                    subject_id=materia.id,
                )
                session.add(enrollment)
                await session.commit()
                await session.refresh(enrollment)
                enrollments_creados.append(enrollment)
                print(f"  [OK] Enrollment creado: {materia.nombre}")
        
        print()
        print("=" * 60)
        print("[OK] MATERIAS ASIGNADAS")
        print("=" * 60)
        print(f"Total de materias asignadas: {len(enrollments_creados)}")
        print()
        
        # Crear notas para todas las materias EXCEPTO la última
        from app.repositories.grade_repository import GradeRepository
        grade_repo = GradeRepository(session)
        
        notas_creadas = []
        # Notas de ejemplo (dejamos la última materia sin notas)
        notas_ejemplo = [
            [4.5, 4.0, 4.8, 3.9],  # Materia 1: 4.3 promedio
            [3.5, 4.2, 4.0, 3.8],  # Materia 2: 3.875 promedio
            [5.0, 4.5, 4.7, 4.9],  # Materia 3: 4.775 promedio
            [3.0, 3.5, 3.2, 3.8],  # Materia 4: 3.375 promedio
            [4.8, 4.6, 4.9, 5.0],  # Materia 5: 4.825 promedio
            # Materia 6: SIN NOTAS (la dejamos sin calificar)
        ]
        
        print("=" * 60)
        print("[OK] CREANDO NOTAS")
        print("=" * 60)
        
        for i, enrollment in enumerate(enrollments_creados[:-1]):  # Todas excepto la última
            materia = materias[i]
            notas = notas_ejemplo[i]
            
            # Verificar si ya existen notas para este enrollment
            existing_grades = await grade_repo.get_by_enrollment(enrollment.id)
            if existing_grades:
                print(f"  [INFO] Ya existen notas para {materia.nombre}, se omitiran")
                continue
            
            # Crear notas
            from datetime import datetime
            periodo_actual = f"{datetime.now().year}-1"  # Formato: 2026-1
            for j, nota in enumerate(notas, start=1):
                grade = Grade(
                    enrollment_id=enrollment.id,
                    nota=nota,
                    periodo=periodo_actual,
                    fecha=date.today(),
                    observaciones=f"Evaluacion {j} - {materia.nombre}",
                )
                session.add(grade)
                notas_creadas.append((materia.nombre, nota))
            
            await session.commit()
            promedio = sum(notas) / len(notas)
            print(f"  [OK] {materia.nombre}: {len(notas)} notas creadas (Promedio: {promedio:.2f})")
        
        # Mostrar la materia sin notas (si hay enrollments)
        if len(enrollments_creados) > 0:
            materia_sin_notas = materias[len(enrollments_creados) - 1]
            print(f"  [INFO] {materia_sin_notas.nombre}: SIN NOTAS (como se solicito)")
        else:
            print("  [INFO] No hay materias asignadas para dejar sin notas")
        
        print()
        print("=" * 60)
        print("[OK] RESUMEN FINAL")
        print("=" * 60)
        print(f"Estudiante: Carlos Estudiante")
        print(f"Email: carlos.estudiante@sofka.edu.co")
        print(f"Password: estudiante123")
        print(f"Materias asignadas: {len(enrollments_creados)}")
        print(f"Materias con notas: {len(enrollments_creados) - 1}")
        print(f"Materias sin notas: 1 ({materia_sin_notas.nombre})")
        print(f"Total de notas creadas: {len(notas_creadas)}")
        print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(create_student_with_grades())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

