"""Service for interacting with Graphiti."""
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
from neo4j import AsyncGraphDatabase

# Add graphiti to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../graphiti"))

from graphiti_core import Graphiti
from graphiti_core.utils.web_crawler import WebCrawler
from graphiti_core.utils.enhanced_legal_crawler import EnhancedLegalCrawler
from graphiti_core.search import SearchConfig
from graphiti_core.llm_client import OpenAIClient
from graphiti_core.embedder import OpenAIEmbedder

from ..config import get_settings
from ..models.requests import ExtractType

settings = get_settings()


class GraphitiService:
    """Service for Graphiti operations."""
    
    def __init__(self):
        self.graphiti: Optional[Graphiti] = None
        self.crawler: Optional[WebCrawler] = None
        self.enhanced_crawler: Optional[EnhancedLegalCrawler] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Graphiti and crawler instances."""
        if self._initialized:
            return
            
        # Initialize Graphiti
        self.graphiti = Graphiti(
            neo4j_uri=settings.neo4j_uri,
            neo4j_user=settings.neo4j_user,
            neo4j_password=settings.neo4j_password,
            neo4j_database=settings.neo4j_database,
            llm_client=OpenAIClient(
                api_key=settings.openai_api_key,
                model=settings.llm_model
            ),
            embedder=OpenAIEmbedder(
                api_key=settings.openai_api_key,
                model=settings.embedding_model
            )
        )
        
        # Initialize web crawler
        self.crawler = WebCrawler(
            llm_provider="openai",
            api_key=settings.openai_api_key
        )
        
        # Initialize enhanced legal crawler
        self.enhanced_crawler = EnhancedLegalCrawler(
            llm_provider="openai",
            api_key=settings.openai_api_key
        )
        
        await self.graphiti.build_indices_and_constraints()
        self._initialized = True
    
    async def crawl_document(
        self,
        url: str,
        extract_type: ExtractType,
        custom_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Crawl and extract information from a legal document."""
        await self.initialize()
        
        try:
            # Use enhanced crawler for supported legal sites
            if self.enhanced_crawler.is_supported_url(url):
                legal_doc = await self.enhanced_crawler.extract_legal_document(url)
                
                # Convert to dict format
                extracted_data = {
                    "title": legal_doc.metadata.title,
                    "document_type": legal_doc.metadata.document_type,
                    "jurisdiction": legal_doc.metadata.jurisdiction,
                    "date": legal_doc.metadata.date,
                    "citation": legal_doc.metadata.citation,
                    "parties": legal_doc.metadata.parties or [],
                    "judges": legal_doc.metadata.judge_names or [],
                    "keywords": legal_doc.metadata.keywords,
                    "sections": [
                        {
                            "type": section.section_type,
                            "heading": section.heading,
                            "content": section.content,
                            "legal_principles": section.legal_principles or [],
                            "cited_cases": section.cited_cases or []
                        }
                        for section in legal_doc.sections
                    ],
                    "summary": legal_doc.summary,
                    "cyber_law_relevance": legal_doc.cyber_law_relevance,
                    "key_holdings": legal_doc.key_holdings,
                    "enhanced_extraction": True
                }
                
                entities_count = len(legal_doc.sections) + len(legal_doc.metadata.keywords)
                
            else:
                # Fallback to basic crawler
                extracted_data = await self.crawler.crawl_legal_document(
                    url=url,
                    use_llm_extraction=True
                )
                entities_count = len(extracted_data.get("entities", []))
                extracted_data["enhanced_extraction"] = False
            
            # Add to knowledge graph
            episode_name = extracted_data.get("title", f"Document from {url}")
            await self.graphiti.add_episode(
                name=episode_name,
                episode_body=json.dumps(extracted_data),
                source_description=f"Crawled from {url}",
                reference_time=extracted_data.get("date", datetime.utcnow())
            )
            
            return {
                "status": "success",
                "data": extracted_data,
                "url": url,
                "extracted_at": datetime.utcnow(),
                "extraction_type": extract_type.value,
                "entities_found": entities_count
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "data": None,
                "url": url,
                "extracted_at": datetime.utcnow(),
                "extraction_type": extract_type.value,
                "entities_found": 0,
                "error": str(e)
            }
    
    async def search_graph(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
        include_semantic: bool = True,
        include_text: bool = True,
        limit: int = 10,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Search the knowledge graph."""
        await self.initialize()
        
        # Build search configuration
        search_config = SearchConfig(
            include_semantic_similarity=include_semantic,
            include_text_similarity=include_text,
            limit=limit
        )
        
        if entity_types:
            search_config.entity_types = entity_types
        
        # Perform search
        start_time = datetime.utcnow()
        results = await self.graphiti.search(
            query=query,
            config=search_config
        )
        search_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "entity": {
                    "id": result.id,
                    "type": result.__class__.__name__,
                    "name": result.name,
                    "properties": result.dict(),
                    "created_at": result.created_at,
                    "updated_at": result.updated_at or result.created_at
                },
                "score": getattr(result, "score", 0.0),
                "relevance_type": "semantic" if include_semantic else "text",
                "snippet": getattr(result, "summary", None)
            })
        
        return {
            "status": "success",
            "query": query,
            "results": formatted_results,
            "total_results": len(formatted_results),
            "search_time_ms": search_time_ms,
            "filters_applied": {
                "entity_types": entity_types,
                "include_semantic": include_semantic,
                "include_text": include_text,
                "date_range": {
                    "from": date_from.isoformat() if date_from else None,
                    "to": date_to.isoformat() if date_to else None
                }
            }
        }
    
    async def batch_crawl(
        self,
        urls: List[str],
        extract_type: ExtractType,
        delay_seconds: float = 1.0
    ) -> List[Dict[str, Any]]:
        """Crawl multiple URLs with rate limiting."""
        results = []
        
        for i, url in enumerate(urls):
            # Add delay between requests (except for first)
            if i > 0:
                await asyncio.sleep(delay_seconds)
            
            result = await self.crawl_document(url, extract_type)
            results.append(result)
        
        return results
    
    async def enhanced_batch_crawl(
        self,
        urls: List[str],
        extract_type: ExtractType,
        use_enhanced_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Enhanced batch crawl using the enhanced legal crawler."""
        await self.initialize()
        
        results = []
        
        # Separate supported and unsupported URLs
        supported_urls = [url for url in urls if self.enhanced_crawler.is_supported_url(url)]
        unsupported_urls = [url for url in urls if not self.enhanced_crawler.is_supported_url(url)]
        
        # Process supported URLs with enhanced crawler
        if supported_urls:
            try:
                legal_docs = await self.enhanced_crawler.batch_extract_documents(supported_urls)
                
                for doc, url in zip(legal_docs, supported_urls):
                    # Convert to standard format and add to graph
                    extracted_data = {
                        "title": doc.metadata.title,
                        "document_type": doc.metadata.document_type,
                        "jurisdiction": doc.metadata.jurisdiction,
                        "date": doc.metadata.date,
                        "citation": doc.metadata.citation,
                        "parties": doc.metadata.parties or [],
                        "judges": doc.metadata.judge_names or [],
                        "keywords": doc.metadata.keywords,
                        "sections": [
                            {
                                "type": section.section_type,
                                "heading": section.heading,
                                "content": section.content,
                                "legal_principles": section.legal_principles or [],
                                "cited_cases": section.cited_cases or []
                            }
                            for section in doc.sections
                        ],
                        "summary": doc.summary,
                        "cyber_law_relevance": doc.cyber_law_relevance,
                        "key_holdings": doc.key_holdings,
                        "enhanced_extraction": True
                    }
                    
                    # Add to knowledge graph
                    episode_name = extracted_data.get("title", f"Document from {url}")
                    await self.graphiti.add_episode(
                        name=episode_name,
                        episode_body=json.dumps(extracted_data),
                        source_description=f"Enhanced crawl from {url}",
                        reference_time=extracted_data.get("date", datetime.utcnow())
                    )
                    
                    results.append({
                        "status": "success",
                        "data": extracted_data,
                        "url": url,
                        "extracted_at": datetime.utcnow(),
                        "extraction_type": extract_type.value,
                        "entities_found": len(doc.sections) + len(doc.metadata.keywords)
                    })
                    
            except Exception as e:
                # Add error results for supported URLs
                for url in supported_urls:
                    results.append({
                        "status": "failed",
                        "data": None,
                        "url": url,
                        "extracted_at": datetime.utcnow(),
                        "extraction_type": extract_type.value,
                        "entities_found": 0,
                        "error": str(e)
                    })
        
        # Process unsupported URLs with regular crawler (unless use_enhanced_only is True)
        if unsupported_urls and not use_enhanced_only:
            for url in unsupported_urls:
                try:
                    result = await self.crawl_document(url, extract_type)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "status": "failed",
                        "data": None,
                        "url": url,
                        "extracted_at": datetime.utcnow(),
                        "extraction_type": extract_type.value,
                        "entities_found": 0,
                        "error": str(e)
                    })
        elif unsupported_urls and use_enhanced_only:
            # Add skipped results for unsupported URLs
            for url in unsupported_urls:
                results.append({
                    "status": "skipped",
                    "data": None,
                    "url": url,
                    "extracted_at": datetime.utcnow(),
                    "extraction_type": extract_type.value,
                    "entities_found": 0,
                    "error": "URL not supported by enhanced crawler"
                })
        
        return results
    
    def get_supported_legal_sites(self) -> Dict[str, str]:
        """Get supported legal websites."""
        return self.enhanced_crawler.get_supported_domains() if self.enhanced_crawler else {}
    
    async def get_entity_details(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific entity."""
        await self.initialize()
        
        # Query Neo4j directly for entity details
        async with AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        ).session(database=settings.neo4j_database) as session:
            
            result = await session.run(
                """
                MATCH (n)
                WHERE n.id = $entity_id
                OPTIONAL MATCH (n)-[r]-(related)
                RETURN n, collect({
                    relationship: type(r),
                    related_entity: related
                }) as relationships
                """,
                entity_id=entity_id
            )
            
            record = await result.single()
            if record:
                node = record["n"]
                relationships = record["relationships"]
                
                return {
                    "entity": dict(node),
                    "relationships": relationships
                }
        
        return None
    
    async def close(self):
        """Close connections."""
        if self.graphiti:
            await self.graphiti.close()
        # Enhanced crawler uses async context manager, no explicit close needed


# Singleton instance
graphiti_service = GraphitiService()