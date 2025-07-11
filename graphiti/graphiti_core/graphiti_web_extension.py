"""
Copyright 2024, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from graphiti_core.nodes import EntityNode, EpisodicNode
from graphiti_core.utils.web_crawler import WebCrawler, create_legal_entity_definitions

logger = logging.getLogger(__name__)


class WebCrawlResults(BaseModel):
    """Results from web crawling and processing."""
    episode: EpisodicNode
    legal_entities: List[EntityNode]
    total_documents: int
    cyber_law_relevance_score: float


async def add_legal_document_from_web(
    self,
    url: str,
    group_id: str = '',
    use_llm_extraction: bool = True,
    css_selectors: Optional[Dict[str, str]] = None,
) -> WebCrawlResults:
    """
    Crawl and process a legal document from the web.
    
    Args:
        url: URL of the legal document
        group_id: Group ID for organizing documents
        use_llm_extraction: Whether to use LLM extraction
        css_selectors: CSS selectors for structured extraction
        
    Returns:
        WebCrawlResults with processed entities
    """
    # Initialize web crawler with the LLM client's configuration
    llm_config = self.llm_client.config
    crawler = WebCrawler(
        llm_provider=llm_config.provider if hasattr(llm_config, 'provider') else 'openai',
        api_key=llm_config.api_key if hasattr(llm_config, 'api_key') else None
    )
    
    async with crawler:
        # Crawl the document
        document_data = await crawler.crawl_legal_document(
            url, 
            use_llm_extraction, 
            css_selectors
        )
        
        # Extract content and metadata
        if use_llm_extraction:
            content = document_data.get('summary', '')
            metadata = document_data.get('metadata', {})
            sections = document_data.get('sections', [])
            cyber_law_relevance = document_data.get('cyber_law_relevance', '')
            key_holdings = document_data.get('key_holdings', [])
        else:
            content = document_data.get('content', '')
            metadata = {
                'title': document_data.get('title', 'Untitled'),
                'date': document_data.get('date', ''),
                'citation': document_data.get('citation', '')
            }
            sections = []
            cyber_law_relevance = ''
            key_holdings = []
        
        # Create episode content
        episode_content = f"""
Legal Document: {metadata.get('title', 'Untitled')}
URL: {url}
Document Type: {metadata.get('document_type', 'Unknown')}
Jurisdiction: {metadata.get('jurisdiction', 'Unknown')}
Date: {metadata.get('date', 'Unknown')}
Citation: {metadata.get('citation', 'Not available')}

Summary:
{content}

Cyber Law Relevance:
{cyber_law_relevance}

Key Holdings:
{chr(10).join([f"- {holding}" for holding in key_holdings])}

Sections:
{chr(10).join([f"{s.get('heading', 'Section')}: {s.get('content', '')[:200]}..." for s in sections[:3]])}
"""
        
        # Add as episode with legal entity types
        legal_entity_types = create_legal_entity_definitions()
        
        result = await self.add_episode(
            name=f"Legal Document: {metadata.get('title', url)}",
            episode_body=episode_content,
            source_description=f"Crawled from {url}",
            reference_time=datetime.utcnow(),
            source=url,
            group_id=group_id,
            entity_types=legal_entity_types
        )
        
        # Calculate cyber law relevance score
        cyber_law_score = 0.0
        if hasattr(result, 'nodes'):
            for node in result.nodes:
                if hasattr(node, 'cyber_law_relevance'):
                    cyber_law_score = max(cyber_law_score, node.cyber_law_relevance)
        
        return WebCrawlResults(
            episode=result.episode,
            legal_entities=result.nodes,
            total_documents=1,
            cyber_law_relevance_score=cyber_law_score
        )


async def add_legal_documents_bulk_from_web(
    self,
    urls: List[str],
    group_id: str = '',
    use_llm_extraction: bool = True,
    css_selectors: Optional[Dict[str, str]] = None,
) -> List[WebCrawlResults]:
    """
    Crawl and process multiple legal documents from the web.
    
    Args:
        urls: List of URLs to crawl
        group_id: Group ID for organizing documents
        use_llm_extraction: Whether to use LLM extraction
        css_selectors: CSS selectors for structured extraction
        
    Returns:
        List of WebCrawlResults
    """
    results = []
    
    # Process URLs in batches to avoid overwhelming the system
    batch_size = 5
    for i in range(0, len(urls), batch_size):
        batch_urls = urls[i:i + batch_size]
        
        # Process each URL in the batch
        batch_results = await semaphore_gather(
            *[
                self.add_legal_document_from_web(
                    url, group_id, use_llm_extraction, css_selectors
                )
                for url in batch_urls
            ],
            max_coroutines=self.max_coroutines
        )
        
        results.extend(batch_results)
    
    return results


async def search_legal_knowledge(
    self,
    query: str,
    group_ids: List[str] = None,
    cyber_law_categories: Optional[List[str]] = None,
    case_law_only: bool = False,
    statutes_only: bool = False,
    limit: int = 10,
) -> SearchResults:
    """
    Search the legal knowledge graph with specialized filters.
    
    Args:
        query: Search query
        group_ids: Group IDs to search within
        cyber_law_categories: Specific cyber law categories to filter
        case_law_only: Only return case law entities
        statutes_only: Only return statute entities
        limit: Maximum results to return
        
    Returns:
        SearchResults with filtered legal entities
    """
    # Build search filters based on legal criteria
    search_filter = SearchFilters()
    
    if case_law_only:
        search_filter.entity_types = ['CaseLaw']
    elif statutes_only:
        search_filter.entity_types = ['Statute']
    
    # Use hybrid search with cross-encoder for best results
    config = COMBINED_HYBRID_SEARCH_CROSS_ENCODER
    config.limit = limit
    
    # Perform the search
    results = await self.search(
        query=query,
        group_ids=group_ids or [],
        config=config,
        search_filter=search_filter
    )
    
    # Post-process for cyber law relevance if categories specified
    if cyber_law_categories and results.nodes:
        # Filter nodes by cyber law relevance
        filtered_nodes = []
        for node in results.nodes:
            if hasattr(node, 'cyber_law_category') and node.cyber_law_category in cyber_law_categories:
                filtered_nodes.append(node)
        results.nodes = filtered_nodes
    
    return results


# Monkey-patch these methods onto the Graphiti class
# This approach allows extending Graphiti without modifying the core class
def extend_graphiti_with_web_capabilities():
    """Extend Graphiti class with web crawling capabilities."""
    from graphiti_core.graphiti import Graphiti
    from graphiti_core.helpers import semaphore_gather
    from graphiti_core.search.search_config import SearchResults
    from graphiti_core.search.search_filters import SearchFilters
    
    # Add the methods to Graphiti class
    Graphiti.add_legal_document_from_web = add_legal_document_from_web
    Graphiti.add_legal_documents_bulk_from_web = add_legal_documents_bulk_from_web
    Graphiti.search_legal_knowledge = search_legal_knowledge
    
    logger.info("Extended Graphiti with web crawling capabilities")