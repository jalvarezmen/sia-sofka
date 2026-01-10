"""Test relationship loading."""
import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from app.core.database import get_engine
from app.models.grade import Grade
from app.models.enrollment import Enrollment
from sqlalchemy.ext.asyncio import AsyncSession


async def test():
    """Test loading grades with relationships."""
    engine = get_engine()
    async with AsyncSession(engine) as session:
        # Load a grade with all relationships
        result = await session.execute(
            select(Grade)
            .options(
                selectinload(Grade.enrollment).selectinload(Enrollment.estudiante),
                selectinload(Grade.enrollment).joinedload(Enrollment.subject)
            )
            .limit(1)
        )
        grade = result.scalar_one_or_none()
        
        if grade:
            print(f"\n✅ Grade found: ID {grade.id}")
            print(f"📝 Nota: {grade.nota}")
            print(f"📋 Enrollment: {grade.enrollment}")
            
            if grade.enrollment:
                print(f"  - Enrollment ID: {grade.enrollment.id}")
                print(f"  - Estudiante ID: {grade.enrollment.estudiante_id}")
                print(f"  - Subject ID: {grade.enrollment.subject_id}")
                print(f"  - Estudiante object: {grade.enrollment.estudiante}")
                print(f"  - Subject object: {grade.enrollment.subject}")
                
                if grade.enrollment.estudiante:
                    print(f"\n👤 ESTUDIANTE LOADED:")
                    print(f"  - ID: {grade.enrollment.estudiante.id}")
                    print(f"  - Nombre: {grade.enrollment.estudiante.nombre}")
                    print(f"  - Apellido: {grade.enrollment.estudiante.apellido}")
                else:
                    print(f"\n❌ ESTUDIANTE is None!")
                
                if grade.enrollment.subject:
                    print(f"\n📚 SUBJECT LOADED:")
                    print(f"  - ID: {grade.enrollment.subject.id}")
                    print(f"  - Nombre: {grade.enrollment.subject.nombre}")
                else:
                    print(f"\n❌ SUBJECT is None!")
        else:
            print("❌ No grades found")


if __name__ == "__main__":
    asyncio.run(test())
