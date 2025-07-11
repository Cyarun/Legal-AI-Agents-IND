"""Integration tests for the unified API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.middleware.auth import AuthInfo


# Create test client
client = TestClient(app)


# Mock authentication for tests
@pytest.fixture
def mock_auth():
    """Mock authentication dependency."""
    def override_verify_token():
        return AuthInfo(
            auth_type="test",
            token="test-token",
            metadata={"permissions": ["read", "write", "admin"]}
        )
    
    app.dependency_overrides[verify_token] = override_verify_token
    yield
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test the health endpoint returns expected structure."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "services" in data
        assert "timestamp" in data


class TestCrawlEndpoints:
    """Test crawling endpoints."""
    
    @patch('app.services.graphiti_service.graphiti_service.crawl_document')
    def test_crawl_document(self, mock_crawl, mock_auth):
        """Test document crawling endpoint."""
        # Mock the crawl response
        mock_crawl.return_value = {
            "status": "success",
            "data": {
                "title": "Test Case",
                "content": "Test content",
                "date": "2024-01-01"
            },
            "url": "https://example.com/test",
            "extracted_at": "2024-01-20T10:00:00",
            "extraction_type": "judgment",
            "entities_found": 3
        }
        
        # Make request
        response = client.post(
            "/api/v1/crawl",
            json={
                "url": "https://example.com/test",
                "extract_type": "judgment"
            },
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["title"] == "Test Case"
        assert data["entities_found"] == 3
    
    def test_crawl_without_auth(self):
        """Test crawl endpoint requires authentication."""
        response = client.post(
            "/api/v1/crawl",
            json={
                "url": "https://example.com/test",
                "extract_type": "judgment"
            }
        )
        assert response.status_code == 403


class TestGraphEndpoints:
    """Test knowledge graph endpoints."""
    
    @patch('app.services.graphiti_service.graphiti_service.search_graph')
    def test_search_graph(self, mock_search, mock_auth):
        """Test graph search endpoint."""
        # Mock search response
        mock_search.return_value = {
            "status": "success",
            "query": "IT Act",
            "results": [
                {
                    "entity": {
                        "id": "case-123",
                        "type": "CaseLaw",
                        "name": "Test Case",
                        "properties": {"citation": "2024 SC 123"},
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    },
                    "score": 0.95,
                    "relevance_type": "semantic"
                }
            ],
            "total_results": 1,
            "search_time_ms": 125.5,
            "filters_applied": {}
        }
        
        # Make request
        response = client.post(
            "/api/v1/graph/search",
            json={
                "query": "IT Act",
                "entity_types": ["CaseLaw"],
                "limit": 10
            },
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["results"]) == 1
        assert data["results"][0]["entity"]["type"] == "CaseLaw"


class TestProcessEndpoints:
    """Test document processing endpoints."""
    
    @patch('app.services.unstract_service.unstract_service.process_document')
    def test_process_document(self, mock_process, mock_auth):
        """Test document processing endpoint."""
        # Mock process response
        mock_process.return_value = {
            "status": "success",
            "execution_id": "exec-123",
            "workflow_id": "legal-workflow",
            "organization_id": "org-456",
            "processed_at": "2024-01-20T10:00:00",
            "result": {"extracted_data": "test"},
            "processing_time_ms": 2500.0
        }
        
        # Make request
        response = client.post(
            "/api/v1/process/document",
            json={
                "file_url": "https://example.com/doc.pdf",
                "workflow_id": "legal-workflow",
                "organization_id": "org-456"
            },
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["execution_id"] == "exec-123"


class TestLegalEndpoints:
    """Test legal analysis endpoints."""
    
    @patch('app.services.graphiti_service.graphiti_service.crawl_document')
    @patch('app.services.graphiti_service.graphiti_service.search_graph')
    def test_analyze_legal_document(self, mock_search, mock_crawl, mock_auth):
        """Test comprehensive legal analysis endpoint."""
        # Mock crawl response
        mock_crawl.return_value = {
            "status": "success",
            "data": {
                "title": "Important Case",
                "content": "Case content",
                "legal_issues": ["Issue 1", "Issue 2"],
                "entities": [
                    {"id": "1", "type": "CaseLaw", "name": "Test Case"}
                ]
            }
        }
        
        # Mock search response
        mock_search.return_value = {
            "results": [
                {
                    "entity": {
                        "id": "case-456",
                        "type": "CaseLaw",
                        "name": "Related Case",
                        "properties": {},
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    },
                    "score": 0.85,
                    "relevance_type": "semantic"
                }
            ]
        }
        
        # Make request
        response = client.post(
            "/api/v1/legal/analyze",
            json={
                "url": "https://indiankanoon.org/doc/12345/",
                "extract_entities": True,
                "find_precedents": True
            },
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["document"]["title"] == "Important Case"
        assert len(data["entities"]) > 0
        assert "processing_details" in data


class TestBatchOperations:
    """Test batch operation endpoints."""
    
    def test_batch_crawl_initiation(self, mock_auth):
        """Test batch crawl job creation."""
        response = client.post(
            "/api/v1/crawl/batch",
            json={
                "urls": [
                    "https://example.com/doc1",
                    "https://example.com/doc2"
                ],
                "extract_type": "judgment",
                "delay_seconds": 1.0
            },
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert data["total_items"] == 2


# Add this import for the auth dependency
from app.middleware.auth import verify_token