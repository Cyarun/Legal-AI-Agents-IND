"""Tests for GraphQL API implementation."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime

from app.main import app
from app.middleware.auth import AuthInfo


# Mock authentication for tests
def override_verify_token():
    return AuthInfo(
        auth_type="test",
        token="test-token",
        metadata={"permissions": ["read", "write", "admin"]}
    )


# Apply mock to all tests
@pytest.fixture(autouse=True)
def mock_auth(monkeypatch):
    from app.middleware import auth
    monkeypatch.setattr(auth, "verify_token", override_verify_token)


client = TestClient(app)


class TestGraphQLQueries:
    """Test GraphQL query operations."""
    
    def test_graphql_endpoint_exists(self):
        """Test that GraphQL endpoint is accessible."""
        response = client.get("/graphql")
        assert response.status_code == 200
        assert "GraphiQL" in response.text or "graphql" in response.text.lower()
    
    @patch('app.services.graphiti_service.graphiti_service.search_graph')
    def test_search_knowledge_graph_query(self, mock_search):
        """Test GraphQL search query."""
        # Mock response
        mock_search.return_value = {
            "status": "success",
            "results": [
                {
                    "entity": {
                        "id": "entity-123",
                        "type": "CaseLaw",
                        "name": "Test Case",
                        "properties": {"citation": "2024 SC 123"},
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    },
                    "score": 0.95,
                    "relevance_type": "semantic",
                    "snippet": "Test snippet"
                }
            ]
        }
        
        # GraphQL query
        query = """
        query SearchGraph($input: GraphSearchInput!) {
            searchKnowledgeGraph(input: $input) {
                entity {
                    id
                    type
                    name
                }
                score
                relevanceType
            }
        }
        """
        
        variables = {
            "input": {
                "query": "IT Act",
                "entityTypes": ["CaseLaw"],
                "limit": 10
            }
        }
        
        response = client.post(
            "/graphql",
            json={"query": query, "variables": variables},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "searchKnowledgeGraph" in data["data"]
        results = data["data"]["searchKnowledgeGraph"]
        assert len(results) == 1
        assert results[0]["entity"]["id"] == "entity-123"
    
    def test_health_query(self):
        """Test simple health check query."""
        query = """
        query {
            health
        }
        """
        
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["health"] == "healthy"


class TestGraphQLMutations:
    """Test GraphQL mutation operations."""
    
    @patch('app.services.graphiti_service.graphiti_service.crawl_document')
    def test_crawl_document_mutation(self, mock_crawl):
        """Test document crawling mutation."""
        # Mock response
        mock_crawl.return_value = {
            "status": "success",
            "url": "https://example.com/test",
            "extracted_at": datetime.now(),
            "extraction_type": "judgment",
            "entities_found": 3,
            "data": {"title": "Test Case", "content": "Test content"}
        }
        
        mutation = """
        mutation CrawlDoc($input: CrawlInput!) {
            crawlDocument(input: $input) {
                status
                url
                extractionType
                entitiesFound
            }
        }
        """
        
        variables = {
            "input": {
                "url": "https://example.com/test",
                "extractType": "judgment"
            }
        }
        
        response = client.post(
            "/graphql",
            json={"query": mutation, "variables": variables},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        result = data["data"]["crawlDocument"]
        assert result["status"] == "success"
        assert result["entitiesFound"] == 3
    
    @patch('app.services.unstract_service.unstract_service.process_document')
    def test_process_document_mutation(self, mock_process):
        """Test document processing mutation."""
        # Mock response
        mock_process.return_value = {
            "status": "success",
            "execution_id": "exec-123",
            "workflow_id": "workflow-456",
            "organization_id": "org-789",
            "processed_at": datetime.now(),
            "result": {"extracted": "data"},
            "processing_time_ms": 1500.0
        }
        
        mutation = """
        mutation ProcessDoc($input: ProcessDocumentInput!) {
            processDocument(input: $input) {
                status
                executionId
                workflowId
                processingTimeMs
            }
        }
        """
        
        variables = {
            "input": {
                "textContent": "Test document content",
                "workflowId": "workflow-456",
                "organizationId": "org-789"
            }
        }
        
        response = client.post(
            "/graphql",
            json={"query": mutation, "variables": variables},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        result = data["data"]["processDocument"]
        assert result["status"] == "success"
        assert result["executionId"] == "exec-123"


class TestGraphQLErrorHandling:
    """Test GraphQL error handling."""
    
    def test_unauthenticated_request(self):
        """Test that unauthenticated requests are rejected."""
        query = """
        query {
            searchKnowledgeGraph(input: {query: "test"}) {
                entity {
                    id
                }
            }
        }
        """
        
        # Override auth to fail
        with patch('app.graphql.context.verify_token', side_effect=Exception("Auth failed")):
            response = client.post(
                "/graphql",
                json={"query": query}
            )
        
        assert response.status_code == 200  # GraphQL returns 200 even for errors
        data = response.json()
        assert "errors" in data
    
    def test_invalid_query(self):
        """Test handling of invalid GraphQL queries."""
        query = """
        query {
            invalidField
        }
        """
        
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data


class TestGraphQLComplexQueries:
    """Test complex GraphQL operations."""
    
    @patch('app.services.graphiti_service.graphiti_service.crawl_document')
    @patch('app.services.graphiti_service.graphiti_service.search_graph')
    def test_legal_analysis_mutation(self, mock_search, mock_crawl):
        """Test comprehensive legal analysis mutation."""
        # Mock crawl response
        mock_crawl.return_value = {
            "status": "success",
            "data": {
                "title": "Important Case",
                "content": "Case content",
                "entities": [{"id": "1", "type": "CaseLaw"}],
                "legal_issues": ["Issue 1"]
            }
        }
        
        # Mock search response
        mock_search.return_value = {
            "results": [
                {
                    "entity": {
                        "id": "related-case",
                        "type": "CaseLaw",
                        "name": "Related Case",
                        "properties": {},
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    },
                    "score": 0.85,
                    "relevance_type": "semantic"
                }
            ]
        }
        
        mutation = """
        mutation AnalyzeDoc($input: LegalAnalysisInput!) {
            analyzeLegalDocument(input: $input) {
                status
                documentTitle
                entitiesCount
                relatedCasesCount
            }
        }
        """
        
        variables = {
            "input": {
                "url": "https://example.com/case",
                "extractEntities": True,
                "findPrecedents": True
            }
        }
        
        response = client.post(
            "/graphql",
            json={"query": mutation, "variables": variables},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        result = data["data"]["analyzeLegalDocument"]
        assert result["status"] == "success"
        assert result["documentTitle"] == "Important Case"
        assert result["entitiesCount"] == 1
        assert result["relatedCasesCount"] == 1