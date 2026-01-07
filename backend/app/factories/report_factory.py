"""Report factory for creating report generators."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any
from app.factories.pdf_generator import PDFReportGenerator
from app.factories.html_generator import HTMLReportGenerator
from app.factories.json_generator import JSONReportGenerator


class ReportFormat(str, Enum):
    """Report format enumeration."""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"


class ReportGenerator(ABC):
    """Abstract base class for report generators."""
    
    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a report from data.
        
        Args:
            data: Report data dictionary
        
        Returns:
            Dictionary with 'content', 'filename', and 'content_type'
        """
        pass


class ReportFactory:
    """Factory for creating report generators."""
    
    @staticmethod
    def create_generator(format: str | ReportFormat) -> ReportGenerator:
        """Create a report generator based on format.
        
        Args:
            format: Report format (pdf, html, json)
        
        Returns:
            Report generator instance
        
        Raises:
            ValueError: If format is not supported
        """
        format_str = format.value if isinstance(format, ReportFormat) else format.lower()
        
        generators = {
            "pdf": PDFReportGenerator,
            "html": HTMLReportGenerator,
            "json": JSONReportGenerator,
        }
        
        generator_class = generators.get(format_str)
        if not generator_class:
            raise ValueError(f"Unsupported report format: {format_str}")
        
        return generator_class()

