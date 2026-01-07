"""Unit tests for report factory and generators."""

import pytest
from app.factories.report_factory import ReportFactory, ReportFormat
from app.factories.pdf_generator import PDFReportGenerator
from app.factories.html_generator import HTMLReportGenerator
from app.factories.json_generator import JSONReportGenerator


def test_report_factory_create_pdf():
    """Test ReportFactory creates PDF generator."""
    generator = ReportFactory.create_generator(ReportFormat.PDF)
    
    assert isinstance(generator, PDFReportGenerator)


def test_report_factory_create_html():
    """Test ReportFactory creates HTML generator."""
    generator = ReportFactory.create_generator(ReportFormat.HTML)
    
    assert isinstance(generator, HTMLReportGenerator)


def test_report_factory_create_json():
    """Test ReportFactory creates JSON generator."""
    generator = ReportFactory.create_generator(ReportFormat.JSON)
    
    assert isinstance(generator, JSONReportGenerator)


def test_report_factory_invalid_format():
    """Test ReportFactory raises error for invalid format."""
    with pytest.raises(ValueError):
        ReportFactory.create_generator("invalid_format")


def test_pdf_generator_generate():
    """Test PDFReportGenerator generates PDF report."""
    generator = PDFReportGenerator()
    
    report_data = {
        "estudiante": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "codigo_institucional": "EST-2024-0001",
        },
        "subjects": [
            {
                "subject": {"nombre": "Matemáticas"},
                "average": 4.5,
            }
        ],
    }
    
    result = generator.generate(report_data)
    
    assert result is not None
    assert "content" in result
    assert "filename" in result
    assert result["filename"].endswith(".pdf")
    assert result["content_type"] == "application/pdf"


def test_html_generator_generate():
    """Test HTMLReportGenerator generates HTML report."""
    generator = HTMLReportGenerator()
    
    report_data = {
        "estudiante": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "codigo_institucional": "EST-2024-0001",
        },
        "subjects": [
            {
                "subject": {"nombre": "Matemáticas"},
                "average": 4.5,
            }
        ],
    }
    
    result = generator.generate(report_data)
    
    assert result is not None
    assert "content" in result
    assert "filename" in result
    assert result["filename"].endswith(".html")
    assert result["content_type"] == "text/html"
    assert "<html" in result["content"].lower() or "<!doctype" in result["content"].lower()


def test_json_generator_generate():
    """Test JSONReportGenerator generates JSON report."""
    generator = JSONReportGenerator()
    
    report_data = {
        "estudiante": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "codigo_institucional": "EST-2024-0001",
        },
        "subjects": [
            {
                "subject": {"nombre": "Matemáticas"},
                "average": 4.5,
            }
        ],
    }
    
    result = generator.generate(report_data)
    
    assert result is not None
    assert "content" in result
    assert "filename" in result
    assert result["filename"].endswith(".json")
    assert result["content_type"] == "application/json"
    
    import json
    # Verify it's valid JSON
    parsed = json.loads(result["content"])
    assert parsed["estudiante"]["nombre"] == "Juan"


def test_all_generators_same_interface():
    """Test all generators implement the same interface."""
    pdf_gen = PDFReportGenerator()
    html_gen = HTMLReportGenerator()
    json_gen = JSONReportGenerator()
    
    report_data = {"test": "data"}
    
    # All should have generate method
    assert hasattr(pdf_gen, "generate")
    assert hasattr(html_gen, "generate")
    assert hasattr(json_gen, "generate")
    
    # All should return same structure
    pdf_result = pdf_gen.generate(report_data)
    html_result = html_gen.generate(report_data)
    json_result = json_gen.generate(report_data)
    
    assert "content" in pdf_result
    assert "filename" in pdf_result
    assert "content_type" in pdf_result
    
    assert "content" in html_result
    assert "filename" in html_result
    assert "content_type" in html_result
    
    assert "content" in json_result
    assert "filename" in json_result
    assert "content_type" in json_result

