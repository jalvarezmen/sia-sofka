"""Unit tests for ReportResponseHandler."""

import json
import pytest
from fastapi import Response
from app.api.v1.serializers.report_response_handler import ReportResponseHandler
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError


def test_handle_response_json_format_bytes():
    """Test handling JSON response with bytes content."""
    report = {
        "content": json.dumps({"test": "data"}).encode("utf-8"),
        "content_type": "application/json",
        "filename": "report.json",
    }
    
    result = ReportResponseHandler.handle_response(report, "json")
    
    assert isinstance(result, dict)
    assert result["test"] == "data"


def test_handle_response_json_format_string():
    """Test handling JSON response with string content."""
    report = {
        "content": json.dumps({"test": "data"}),
        "content_type": "application/json",
        "filename": "report.json",
    }
    
    result = ReportResponseHandler.handle_response(report, "json")
    
    assert isinstance(result, dict)
    assert result["test"] == "data"


def test_handle_response_pdf_format():
    """Test handling PDF response."""
    report = {
        "content": b"PDF content here",
        "content_type": "application/pdf",
        "filename": "report.pdf",
    }
    
    result = ReportResponseHandler.handle_response(report, "pdf")
    
    assert isinstance(result, Response)
    assert result.media_type == "application/pdf"
    assert "attachment" in result.headers.get("content-disposition", "")
    assert "report.pdf" in result.headers.get("content-disposition", "")


def test_handle_response_pdf_format_string():
    """Test handling PDF response with string content (should encode)."""
    report = {
        "content": "PDF content here",
        "content_type": "application/pdf",
        "filename": "report.pdf",
    }
    
    result = ReportResponseHandler.handle_response(report, "pdf")
    
    assert isinstance(result, Response)
    assert result.media_type == "application/pdf"
    assert isinstance(result.body, bytes)


def test_handle_response_html_format():
    """Test handling HTML response."""
    report = {
        "content": b"<html><body>Report</body></html>",
        "content_type": "text/html",
        "filename": "report.html",
    }
    
    result = ReportResponseHandler.handle_response(report, "html")
    
    assert isinstance(result, Response)
    assert result.media_type == "text/html"
    assert "attachment" in result.headers.get("content-disposition", "")
    assert "report.html" in result.headers.get("content-disposition", "")


def test_handle_response_html_format_string():
    """Test handling HTML response with string content (should encode)."""
    report = {
        "content": "<html><body>Report</body></html>",
        "content_type": "text/html",
        "filename": "report.html",
    }
    
    result = ReportResponseHandler.handle_response(report, "html")
    
    assert isinstance(result, Response)
    assert result.media_type == "text/html"
    assert isinstance(result.body, bytes)


def test_handle_response_case_insensitive_format():
    """Test that format is case insensitive."""
    report = {
        "content": json.dumps({"test": "data"}),
        "content_type": "application/json",
        "filename": "report.json",
    }
    
    result = ReportResponseHandler.handle_response(report, "JSON")
    
    assert isinstance(result, dict)
    assert result["test"] == "data"


def test_handle_response_error_not_found():
    """Test handling NotFoundError."""
    report = {
        "content": "",
        "content_type": "application/json",
        "filename": "report.json",
    }
    
    error = ValueError("Student not found")
    
    with pytest.raises(NotFoundError) as exc_info:
        ReportResponseHandler.handle_response(report, "json", error, "not_found")
    
    assert "Student" in str(exc_info.value)


def test_handle_response_error_forbidden():
    """Test handling ForbiddenError."""
    report = {
        "content": "",
        "content_type": "application/json",
        "filename": "report.json",
    }
    
    error = ValueError("Subject not assigned")
    
    with pytest.raises(ForbiddenError) as exc_info:
        ReportResponseHandler.handle_response(report, "json", error, "forbidden")
    
    assert "Subject not assigned" in str(exc_info.value)


def test_handle_response_error_validation():
    """Test handling ValidationError."""
    report = {
        "content": "",
        "content_type": "application/json",
        "filename": "report.json",
    }
    
    error = ValueError("Invalid data")
    
    with pytest.raises(ValidationError) as exc_info:
        ReportResponseHandler.handle_response(report, "json", error, "validation")
    
    assert "Invalid data" in str(exc_info.value)


def test_handle_response_error_auto_detect_not_found():
    """Test auto-detection of 'not found' in error message."""
    report = {
        "content": "",
        "content_type": "application/json",
        "filename": "report.json",
    }
    
    error = ValueError("Student not found")
    
    with pytest.raises(NotFoundError):
        ReportResponseHandler.handle_response(report, "json", error)


def test_handle_response_error_auto_detect_forbidden():
    """Test auto-detection of 'not assigned' in error message."""
    report = {
        "content": "",
        "content_type": "application/json",
        "filename": "report.json",
    }
    
    error = ValueError("Subject not assigned to profesor")
    
    with pytest.raises(ForbiddenError):
        ReportResponseHandler.handle_response(report, "json", error)


def test_handle_response_error_default_validation():
    """Test default to ValidationError for unknown errors."""
    report = {
        "content": "",
        "content_type": "application/json",
        "filename": "report.json",
    }
    
    error = ValueError("Some other error")
    
    with pytest.raises(ValidationError) as exc_info:
        ReportResponseHandler.handle_response(report, "json", error)
    
    assert "Some other error" in str(exc_info.value)

