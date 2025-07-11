"""
Web crawler module for Graphiti using Crawl4AI.
Specialized for legal document extraction and processing.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union

from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LegalDocumentMetadata(BaseModel):
    """Metadata structure for legal documents."""
    title: str = Field(description="Title of the legal document")
    document_type: str = Field(description="Type: case_law, statute, regulation, circular, guideline")
    jurisdiction: str = Field(description="Jurisdiction: supreme_court, high_court, tribunal, regulatory")
    case_number: Optional[str] = Field(description="Case number if applicable")
    date: Optional[str] = Field(description="Date of judgment/enactment")
    citation: Optional[str] = Field(description="Legal citation")
    judge_names: Optional[List[str]] = Field(description="Names of judges")
    parties: Optional[List[str]] = Field(description="Parties involved")
    keywords: List[str] = Field(description="Legal keywords and topics")


class LegalDocumentSection(BaseModel):
    """Structure for sections within legal documents."""
    section_type: str = Field(description="Type: facts, issues, arguments, judgment, precedents")
    heading: Optional[str] = Field(description="Section heading")
    content: str = Field(description="Section content")
    legal_principles: Optional[List[str]] = Field(description="Legal principles identified")
    cited_cases: Optional[List[str]] = Field(description="Cases cited in this section")


class LegalDocument(BaseModel):
    """Complete legal document structure."""
    metadata: LegalDocumentMetadata
    sections: List[LegalDocumentSection]
    summary: str = Field(description="Executive summary of the document")
    cyber_law_relevance: str = Field(description="Specific relevance to cyber law")
    key_holdings: List[str] = Field(description="Key legal holdings or principles")


class WebCrawler:
    """Web crawler for extracting legal documents with Crawl4AI."""
    
    def __init__(self, llm_provider: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the web crawler.
        
        Args:
            llm_provider: LLM provider for extraction (openai, gemini, etc.)
            api_key: API key for the LLM provider
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.crawler = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.crawler = AsyncWebCrawler(verbose=True)
        await self.crawler.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.crawler:
            await self.crawler.__aexit__(exc_type, exc_val, exc_tb)
    
    def _create_legal_extraction_strategy(self) -> LLMExtractionStrategy:
        """Create LLM extraction strategy for legal documents."""
        if not self.llm_provider or not self.api_key:
            raise ValueError("LLM provider and API key required for legal document extraction")
            
        return LLMExtractionStrategy(
            provider=self.llm_provider,
            api_key=self.api_key,
            schema=LegalDocument.model_json_schema(),
            extraction_type="legal_document",
            instruction="""Extract the complete legal document with the following focus:
            1. Identify the document type and metadata
            2. Extract all sections with proper categorization
            3. Identify legal principles and precedents
            4. Focus on cyber law relevance - data protection, privacy, cybercrime, IT Act provisions
            5. Extract key holdings and judgments
            6. Identify all case citations and references
            7. Summarize the document's significance for cyber law practice"""
        )
    
    def _create_css_extraction_strategy(self, selectors: Dict[str, str]) -> JsonCssExtractionStrategy:
        """Create CSS extraction strategy for structured legal websites."""
        schema = {
            "name": "Legal Document Extraction",
            "baseSelector": selectors.get("base", "body"),
            "fields": [
                {"name": "title", "selector": selectors.get("title", "h1"), "type": "text"},
                {"name": "content", "selector": selectors.get("content", "div.content"), "type": "text"},
                {"name": "date", "selector": selectors.get("date", ".date"), "type": "text"},
                {"name": "citation", "selector": selectors.get("citation", ".citation"), "type": "text"},
                {"name": "metadata", "selector": selectors.get("metadata", ".metadata"), "type": "text"}
            ]
        }
        return JsonCssExtractionStrategy(schema)
    
    async def crawl_legal_document(
        self, 
        url: str, 
        use_llm_extraction: bool = True,
        css_selectors: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Crawl a legal document from a URL.
        
        Args:
            url: URL of the legal document
            use_llm_extraction: Whether to use LLM extraction (True) or CSS extraction (False)
            css_selectors: CSS selectors for structured extraction (if not using LLM)
            
        Returns:
            Extracted legal document data
        """
        if not self.crawler:
            raise RuntimeError("Crawler not initialized. Use async context manager.")
            
        # Choose extraction strategy
        if use_llm_extraction:
            strategy = self._create_legal_extraction_strategy()
        else:
            if not css_selectors:
                raise ValueError("CSS selectors required when not using LLM extraction")
            strategy = self._create_css_extraction_strategy(css_selectors)
        
        # Crawl the page
        result = await self.crawler.arun(
            url=url,
            extraction_strategy=strategy,
            bypass_cache=True
        )
        
        if result.success:
            if use_llm_extraction:
                return json.loads(result.extracted_content)
            else:
                return result.extracted_content
        else:
            raise Exception(f"Failed to crawl {url}: {result.error_message}")
    
    async def crawl_multiple_documents(
        self, 
        urls: List[str], 
        use_llm_extraction: bool = True,
        css_selectors: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl multiple legal documents concurrently.
        
        Args:
            urls: List of URLs to crawl
            use_llm_extraction: Whether to use LLM extraction
            css_selectors: CSS selectors for structured extraction
            
        Returns:
            List of extracted legal documents
        """
        tasks = [
            self.crawl_legal_document(url, use_llm_extraction, css_selectors)
            for url in urls
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)


def create_legal_entity_definitions():
    """Create Pydantic models for legal entities in the knowledge graph."""
    
    class CaseLaw(BaseModel):
        """Case law entity."""
        name: str = Field(description="Case name")
        citation: str = Field(description="Legal citation")
        court: str = Field(description="Court name")
        date: str = Field(description="Decision date")
        cyber_law_category: str = Field(description="Category: data_protection, cybercrime, etc.")
        
    class LegalPrinciple(BaseModel):
        """Legal principle or doctrine entity."""
        name: str = Field(description="Principle name")
        description: str = Field(description="Principle description")
        established_by: str = Field(description="Case that established this principle")
        
    class Statute(BaseModel):
        """Statute or regulation entity."""
        name: str = Field(description="Statute name")
        section: str = Field(description="Section number")
        description: str = Field(description="Section description")
        
    class LegalProcedure(BaseModel):
        """Legal procedure or process entity."""
        name: str = Field(description="Procedure name")
        steps: List[str] = Field(description="Procedure steps")
        applicable_to: str = Field(description="When this procedure applies")
        
    return {
        'CaseLaw': CaseLaw,
        'LegalPrinciple': LegalPrinciple,
        'Statute': Statute,
        'LegalProcedure': LegalProcedure
    }