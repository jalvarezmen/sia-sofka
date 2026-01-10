"""Factories package.

This module imports all generators to ensure they are registered
with the ReportFactory using the Registry Pattern.
"""

from app.factories.report_factory import (
    ReportFactory,
    ReportGenerator,
    ReportFormat,
)

# Import generators to trigger registration via decorators
from app.factories.pdf_generator import PDFReportGenerator  # noqa: F401
from app.factories.html_generator import HTMLReportGenerator  # noqa: F401
from app.factories.json_generator import JSONReportGenerator  # noqa: F401

__all__ = [
    "ReportFactory",
    "ReportGenerator",
    "ReportFormat",
    "PDFReportGenerator",
    "HTMLReportGenerator",
    "JSONReportGenerator",
]
