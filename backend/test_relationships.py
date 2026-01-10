"""Test para verificar carga de relaciones."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.grade import Grade
from app.models.enrollment import Enrollment
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def test():
    engine = create_async_engine("postgresql+asyncpg://postgres:postgres@postgres:5432/sia_sofka")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        result = await db.execute(
            select(Grade)
            .options(
                selectinload(Grade.enrollment).options(
                    selectinload(Enrollment.estudiante),
                    selectinload(Enrollment.subject)
                )
            )
            .limit(1)
        )
        grade = result.scalar_one_or_none()
        
        if grade:
            print(f"\n✅ Grade ID: {grade.id}")
            print(f"   Enrollment ID: {grade.enrollment_id}")
            
            if grade.enrollment:
                print(f"\n✅ Enrollment loaded: ID={grade.enrollment.id}")
                print(f"   - estudiante_id: {grade.enrollment.estudiante_id}")
                print(f"   - subject_id: {grade.enrollment.subject_id}")
                
                if grade.enrollment.estudiante:
                    print(f"\n✅ Estudiante loaded:")
                    print(f"   - ID: {grade.enrollment.estudiante.id}")
                    print(f"   - Nombre: {grade.enrollment.estudiante.nombre}")
                    print(f"   - Apellido: {grade.enrollment.estudiante.apellido}")
                else:
                    print("\n❌ Estudiante NOT loaded")
                
                if grade.enrollment.subject:
                    print(f"\n✅ Subject loaded:")
                    print(f"   - ID: {grade.enrollment.subject.id}")
                    print(f"   - Nombre: {grade.enrollment.subject.nombre}")
                    print(f"   - Código: {grade.enrollment.subject.codigo_institucional}")
                else:
                    print("\n❌ Subject NOT loaded")
            else:
                print("\n❌ Enrollment NOT loaded")

if __name__ == "__main__":
    asyncio.run(test())
