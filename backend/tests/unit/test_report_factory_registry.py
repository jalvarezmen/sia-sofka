"""Tests for Report Factory Registry Pattern."""

import pytest
from app.factories.report_factory import ReportFactory, ReportGenerator, ReportFormat
from app.factories.pdf_generator import PDFReportGenerator
from app.factories.html_generator import HTMLReportGenerator
from app.factories.json_generator import JSONReportGenerator


def test_registry_pattern_registers_all_generators():
    """Test that all generators are registered with the factory."""
    # Importar generadores activa los decoradores @register
    from app.factories import (
        ReportFactory,
        PDFReportGenerator,  # noqa: F401
        HTMLReportGenerator,  # noqa: F401
        JSONReportGenerator,  # noqa: F401
    )
    
    formats = ReportFactory.get_registered_formats()
    
    assert 'pdf' in formats
    assert 'html' in formats
    assert 'json' in formats
    assert len(formats) == 3


def test_factory_creates_pdf_generator():
    """Test that factory creates PDF generator correctly."""
    generator = ReportFactory.create_generator('pdf')
    assert isinstance(generator, PDFReportGenerator)
    assert isinstance(generator, ReportGenerator)


def test_factory_creates_html_generator():
    """Test that factory creates HTML generator correctly."""
    generator = ReportFactory.create_generator('html')
    assert isinstance(generator, HTMLReportGenerator)
    assert isinstance(generator, ReportGenerator)


def test_factory_creates_json_generator():
    """Test that factory creates JSON generator correctly."""
    generator = ReportFactory.create_generator('json')
    assert isinstance(generator, JSONReportGenerator)
    assert isinstance(generator, ReportGenerator)


def test_factory_creates_generator_with_enum_format():
    """Test that factory accepts ReportFormat enum."""
    generator = ReportFactory.create_generator(ReportFormat.PDF)
    assert isinstance(generator, PDFReportGenerator)
    
    generator = ReportFactory.create_generator(ReportFormat.HTML)
    assert isinstance(generator, HTMLReportGenerator)
    
    generator = ReportFactory.create_generator(ReportFormat.JSON)
    assert isinstance(generator, JSONReportGenerator)


def test_factory_singleton_pattern():
    """Test that factory returns same instance (singleton pattern)."""
    gen1 = ReportFactory.create_generator('pdf')
    gen2 = ReportFactory.create_generator('pdf')
    
    # Should be same instance (singleton)
    assert gen1 is gen2


def test_factory_singleton_different_formats():
    """Test that different formats return different instances."""
    pdf_gen = ReportFactory.create_generator('pdf')
    html_gen = ReportFactory.create_generator('html')
    
    # Different formats should return different instances
    assert pdf_gen is not html_gen


def test_factory_raises_error_for_unknown_format():
    """Test that factory raises error for unknown format."""
    with pytest.raises(ValueError, match="Unsupported report format"):
        ReportFactory.create_generator('unknown')
    
    with pytest.raises(ValueError, match="Unsupported report format"):
        ReportFactory.create_generator('xml')
    
    with pytest.raises(ValueError, match="Unsupported report format"):
        ReportFactory.create_generator('csv')


def test_factory_case_insensitive_format():
    """Test that factory handles case-insensitive formats."""
    pdf_gen_upper = ReportFactory.create_generator('PDF')
    pdf_gen_lower = ReportFactory.create_generator('pdf')
    pdf_gen_mixed = ReportFactory.create_generator('Pdf')
    
    # All should create PDF generator
    assert isinstance(pdf_gen_upper, PDFReportGenerator)
    assert isinstance(pdf_gen_lower, PDFReportGenerator)
    assert isinstance(pdf_gen_mixed, PDFReportGenerator)


def test_get_registered_formats_returns_list():
    """Test that get_registered_formats returns a list."""
    formats = ReportFactory.get_registered_formats()
    
    assert isinstance(formats, list)
    assert len(formats) > 0
    assert all(isinstance(fmt, str) for fmt in formats)


def test_generators_implement_generate_method():
    """Test that all generators implement the generate method."""
    pdf_gen = ReportFactory.create_generator('pdf')
    html_gen = ReportFactory.create_generator('html')
    json_gen = ReportFactory.create_generator('json')
    
    # All should have generate method
    assert hasattr(pdf_gen, 'generate')
    assert hasattr(html_gen, 'generate')
    assert hasattr(json_gen, 'generate')
    
    # Test that generate method works
    test_data = {
        "estudiante": {
            "nombre": "Test",
            "apellido": "User",
            "codigo_institucional": "EST-001"
        },
        "subjects": []
    }
    
    # Should not raise error
    pdf_result = pdf_gen.generate(test_data)
    assert 'content' in pdf_result
    assert 'filename' in pdf_result
    assert 'content_type' in pdf_result
    
    html_result = html_gen.generate(test_data)
    assert 'content' in html_result
    assert 'filename' in html_result
    assert 'content_type' in html_result
    
    json_result = json_gen.generate(test_data)
    assert 'content' in json_result
    assert 'filename' in json_result
    assert 'content_type' in json_result

