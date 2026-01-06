"""Utility for generating institutional codes."""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User


async def generar_codigo_institucional(
    db: AsyncSession, role: str
) -> str:
    """Generate institutional code for a user based on role.
    
    Args:
        db: Database session
        role: User role (Estudiante, Profesor, Admin)
    
    Returns:
        Generated institutional code in format: {PREFIX}-{YEAR}-{SEQUENTIAL}
    """
    prefixes = {
        "Estudiante": "EST",
        "Profesor": "PROF",
        "Admin": "ADM",
    }
    
    prefix = prefixes.get(role, "USR")
    current_year = datetime.now().year
    
    # Get the count of users with the same role and year
    stmt = select(func.count(User.id)).where(
        User.role == role,
        User.codigo_institucional.like(f"{prefix}-{current_year}-%")
    )
    result = await db.execute(stmt)
    count = result.scalar() or 0
    
    # Generate sequential number with 4 digits
    sequential = str(count + 1).zfill(4)
    
    return f"{prefix}-{current_year}-{sequential}"

