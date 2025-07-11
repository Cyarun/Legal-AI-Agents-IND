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

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from graphiti_core.edges import EntityEdge
from graphiti_core.nodes import EntityNode
from graphiti_core.legal_entities import LEGAL_ENTITY_TYPES
from graphiti_core.legal_analysis_prompts import (
    AnalysisType,
    LegalAnalysisPrompts,
    LegalWebsiteSchema,
    SyntheticGraphPrompts,
    LegalSearchStrategies
)
from graphiti_core.utils.web_crawler import WebCrawler

logger = logging.getLogger(__name__)


class SyntheticNode(BaseModel):
    """Synthetic node generated from analysis."""
    entity_type: str
    name: str
    properties: Dict[str, Any]
    source_nodes: List[str]  # UUIDs of source nodes
    confidence: float = Field(ge=0.0, le=1.0)
    analysis_type: str
    

class SyntheticEdge(BaseModel):
    """Synthetic edge generated from analysis."""
    source_node: str
    target_node: str
    relationship_type: str
    properties: Dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    derived_from: List[str]  # Source edges or analysis


class LegalGraphSynthesizer:
    """Synthesizes legal knowledge graphs from multiple sources."""
    
    def __init__(self, graphiti_instance):
        """
        Initialize the synthesizer.
        
        Args:
            graphiti_instance: Instance of Graphiti class
        """
        self.graphiti = graphiti_instance
        self.llm_client = graphiti_instance.llm_client
        self.embedder = graphiti_instance.embedder
        self.prompts = LegalAnalysisPrompts()
        self.schemas = LegalWebsiteSchema()
        
    async def analyze_case_to_law(
        self,
        case_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a case to extract applicable laws.
        
        Args:
            case_content: Case details including facts, issues, judgment
            
        Returns:
            Analysis results with statutory mappings
        """
        prompt_data = self.prompts.get_prompt(AnalysisType.CASE_TO_LAW)
        
        # Format the prompt with case data
        formatted_prompt = prompt_data["template"].format(**case_content)
        
        # Get analysis from LLM
        analysis = await self.llm_client.generate_response(
            system_prompt=prompt_data["system"],
            user_prompt=formatted_prompt,
            response_model=prompt_data["extraction_schema"]
        )
        
        return analysis
    
    async def analyze_law_to_case(
        self,
        statute_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze how a statutory provision has been interpreted in cases.
        
        Args:
            statute_content: Statute details including section text
            
        Returns:
            Analysis results with case interpretations
        """
        prompt_data = self.prompts.get_prompt(AnalysisType.LAW_TO_CASE)
        
        formatted_prompt = prompt_data["template"].format(**statute_content)
        
        analysis = await self.llm_client.generate_response(
            system_prompt=prompt_data["system"],
            user_prompt=formatted_prompt,
            response_model=prompt_data["extraction_schema"]
        )
        
        return analysis
    
    async def extract_legal_principles(
        self,
        content: str
    ) -> List[Dict[str, Any]]:
        """
        Extract legal principles from content.
        
        Args:
            content: Legal text to analyze
            
        Returns:
            List of extracted principles
        """
        prompt_data = self.prompts.get_prompt(AnalysisType.PRINCIPLE_EXTRACTION)
        
        formatted_prompt = prompt_data["template"].format(content=content)
        
        analysis = await self.llm_client.generate_response(
            system_prompt=prompt_data["system"],
            user_prompt=formatted_prompt,
            response_model=prompt_data["extraction_schema"]
        )
        
        return analysis.get("principles", [])
    
    async def map_precedents(
        self,
        cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Map precedential relationships between cases.
        
        Args:
            cases: List of case details
            
        Returns:
            Precedent network and chains
        """
        prompt_data = self.prompts.get_prompt(AnalysisType.PRECEDENT_MAPPING)
        
        formatted_prompt = prompt_data["template"].format(
            cases=json.dumps(cases, indent=2)
        )
        
        analysis = await self.llm_client.generate_response(
            system_prompt=prompt_data["system"],
            user_prompt=formatted_prompt,
            response_model=prompt_data["extraction_schema"]
        )
        
        return analysis
    
    async def synthesize_case_law(
        self,
        cases: List[EntityNode]
    ) -> Tuple[List[SyntheticNode], List[SyntheticEdge]]:
        """
        Synthesize understanding from multiple cases.
        
        Args:
            cases: List of case law nodes
            
        Returns:
            Synthetic nodes and edges
        """
        # Prepare case data
        case_data = [
            {
                "name": case.name,
                "summary": case.summary,
                "citation": getattr(case, 'citation', ''),
                "key_holding": getattr(case, 'key_holding', ''),
                "uuid": case.uuid
            }
            for case in cases
        ]
        
        # Get synthesis prompt
        synthesis_prompt = SyntheticGraphPrompts.get_synthesis_prompt("case_law_synthesis")
        formatted_prompt = synthesis_prompt.format(
            cases=json.dumps(case_data, indent=2)
        )
        
        # Generate synthesis
        synthesis = await self.llm_client.generate_response(
            system_prompt="You are a legal analyst creating synthetic understanding from multiple cases.",
            user_prompt=formatted_prompt
        )
        
        # Parse synthesis into nodes and edges
        synthetic_nodes = []
        synthetic_edges = []
        
        # Create synthetic principle nodes
        for principle in synthesis.get("common_principles", []):
            node = SyntheticNode(
                entity_type="LegalPrinciple",
                name=principle["name"],
                properties={
                    "description": principle["description"],
                    "derived_from_cases": principle["source_cases"]
                },
                source_nodes=[case.uuid for case in cases],
                confidence=principle.get("confidence", 0.8),
                analysis_type="case_law_synthesis"
            )
            synthetic_nodes.append(node)
            
            # Create edges from cases to principle
            for case_uuid in principle["source_cases"]:
                edge = SyntheticEdge(
                    source_node=case_uuid,
                    target_node=node.name,  # Will be replaced with actual UUID
                    relationship_type="establishes_principle",
                    properties={
                        "strength": principle.get("strength", "medium")
                    },
                    confidence=principle.get("confidence", 0.8),
                    derived_from=["synthesis"]
                )
                synthetic_edges.append(edge)
        
        # Create evolution edges
        for evolution in synthesis.get("legal_evolution", []):
            edge = SyntheticEdge(
                source_node=evolution["earlier_case"],
                target_node=evolution["later_case"],
                relationship_type="evolved_into",
                properties={
                    "evolution_type": evolution["type"],
                    "changes": evolution["changes"]
                },
                confidence=evolution.get("confidence", 0.7),
                derived_from=["temporal_analysis"]
            )
            synthetic_edges.append(edge)
        
        return synthetic_nodes, synthetic_edges
    
    async def integrate_statute_cases(
        self,
        statutes: List[EntityNode],
        cases: List[EntityNode]
    ) -> Tuple[List[SyntheticNode], List[SyntheticEdge]]:
        """
        Integrate statutory provisions with case law interpretations.
        
        Args:
            statutes: List of statute nodes
            cases: List of case nodes
            
        Returns:
            Synthetic nodes and edges showing integration
        """
        statute_data = [
            {
                "name": statute.name,
                "section": getattr(statute, 'section', ''),
                "summary": statute.summary,
                "uuid": statute.uuid
            }
            for statute in statutes
        ]
        
        case_data = [
            {
                "name": case.name,
                "summary": case.summary,
                "uuid": case.uuid
            }
            for case in cases
        ]
        
        # Get integration prompt
        synthesis_prompt = SyntheticGraphPrompts.get_synthesis_prompt("statute_case_integration")
        formatted_prompt = synthesis_prompt.format(
            statutes=json.dumps(statute_data, indent=2),
            cases=json.dumps(case_data, indent=2)
        )
        
        # Generate integration
        integration = await self.llm_client.generate_response(
            system_prompt="You are integrating statutory law with case law interpretations.",
            user_prompt=formatted_prompt
        )
        
        synthetic_nodes = []
        synthetic_edges = []
        
        # Create compliance guideline nodes
        for guideline in integration.get("compliance_guidelines", []):
            node = SyntheticNode(
                entity_type="LegalProcedure",
                name=guideline["name"],
                properties={
                    "description": guideline["description"],
                    "based_on_statute": guideline["statute"],
                    "validated_by_cases": guideline["cases"],
                    "steps": guideline["steps"]
                },
                source_nodes=[s.uuid for s in statutes] + [c.uuid for c in cases],
                confidence=guideline.get("confidence", 0.85),
                analysis_type="statute_case_integration"
            )
            synthetic_nodes.append(node)
        
        # Create interpretation edges
        for interpretation in integration.get("interpretations", []):
            edge = SyntheticEdge(
                source_node=interpretation["case_uuid"],
                target_node=interpretation["statute_uuid"],
                relationship_type="interprets",
                properties={
                    "interpretation": interpretation["interpretation"],
                    "impact": interpretation["impact"]
                },
                confidence=interpretation.get("confidence", 0.8),
                derived_from=["case_analysis"]
            )
            synthetic_edges.append(edge)
        
        return synthetic_nodes, synthetic_edges
    
    async def crawl_and_synthesize(
        self,
        website: str,
        search_query: str,
        analysis_type: AnalysisType,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Crawl legal website and synthesize knowledge.
        
        Args:
            website: Website identifier (e.g., 'indiankanoon')
            search_query: Search query for the website
            analysis_type: Type of analysis to perform
            limit: Maximum documents to process
            
        Returns:
            Synthesis results with entities and relationships
        """
        # Get website schema
        schema = self.schemas.get_schema(website)
        if not schema:
            raise ValueError(f"Unknown website: {website}")
        
        # Initialize crawler
        crawler = WebCrawler(
            llm_provider=self.llm_client.config.provider if hasattr(self.llm_client.config, 'provider') else 'openai',
            api_key=self.llm_client.config.api_key if hasattr(self.llm_client.config, 'api_key') else None
        )
        
        async with crawler:
            # Build search URL
            search_url = f"{schema['base_url']}{schema['search_endpoint']}{search_query}"
            
            # Crawl search results
            search_results = await crawler.crawl_legal_document(
                search_url,
                use_llm_extraction=False,
                css_selectors=schema.get('selectors', {})
            )
            
            # Extract document URLs (this would need actual implementation based on website)
            doc_urls = self._extract_document_urls(search_results, schema, limit)
            
            # Crawl individual documents
            documents = []
            for url in doc_urls[:limit]:
                try:
                    doc = await crawler.crawl_legal_document(
                        url,
                        use_llm_extraction=True,
                        css_selectors=schema.get('selectors', {})
                    )
                    documents.append(doc)
                except Exception as e:
                    logger.error(f"Error crawling {url}: {e}")
                    continue
            
            # Perform analysis based on type
            if analysis_type == AnalysisType.CASE_TO_LAW:
                results = []
                for doc in documents:
                    if doc.get('metadata', {}).get('document_type') == 'case_law':
                        analysis = await self.analyze_case_to_law(doc)
                        results.append(analysis)
                return {"analyses": results, "documents": documents}
            
            elif analysis_type == AnalysisType.PRINCIPLE_EXTRACTION:
                all_principles = []
                for doc in documents:
                    principles = await self.extract_legal_principles(
                        doc.get('content', '')
                    )
                    all_principles.extend(principles)
                return {"principles": all_principles, "documents": documents}
            
            else:
                # Default: Create episodes for all documents
                episodes = []
                for doc in documents:
                    episode_result = await self.graphiti.add_legal_document_from_web(
                        doc.get('url', ''),
                        group_id=f"{website}_{search_query}",
                        use_llm_extraction=True
                    )
                    episodes.append(episode_result)
                return {"episodes": episodes, "documents": documents}
    
    def _extract_document_urls(
        self,
        search_results: Dict[str, Any],
        schema: Dict[str, Any],
        limit: int
    ) -> List[str]:
        """
        Extract document URLs from search results.
        
        This is a placeholder - actual implementation would depend on website structure.
        """
        # This would parse the search results HTML to extract document URLs
        # For now, return empty list
        return []
    
    async def create_legal_research_graph(
        self,
        research_question: str,
        websites: List[str] = None,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Create comprehensive legal research graph for a question.
        
        Args:
            research_question: Legal research question
            websites: List of websites to search (defaults to all)
            max_depth: Maximum depth of research
            
        Returns:
            Research graph with all findings
        """
        if websites is None:
            websites = list(self.schemas.SCHEMAS.keys())
        
        # Phase 1: Initial search across websites
        initial_results = {}
        for website in websites:
            try:
                results = await self.crawl_and_synthesize(
                    website=website,
                    search_query=research_question,
                    analysis_type=AnalysisType.PRINCIPLE_EXTRACTION,
                    limit=5
                )
                initial_results[website] = results
            except Exception as e:
                logger.error(f"Error searching {website}: {e}")
        
        # Phase 2: Deep analysis of found materials
        all_cases = []
        all_statutes = []
        
        for website, results in initial_results.items():
            for doc in results.get('documents', []):
                if doc.get('metadata', {}).get('document_type') == 'case_law':
                    all_cases.append(doc)
                elif doc.get('metadata', {}).get('document_type') == 'statute':
                    all_statutes.append(doc)
        
        # Phase 3: Synthesize relationships
        synthesis_results = {
            "research_question": research_question,
            "sources_searched": websites,
            "documents_analyzed": len(all_cases) + len(all_statutes),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Create synthetic understanding
        if all_cases:
            case_nodes = [self._doc_to_node(doc) for doc in all_cases]
            synthetic_nodes, synthetic_edges = await self.synthesize_case_law(case_nodes)
            synthesis_results["case_synthesis"] = {
                "nodes": synthetic_nodes,
                "edges": synthetic_edges
            }
        
        if all_cases and all_statutes:
            statute_nodes = [self._doc_to_node(doc) for doc in all_statutes]
            case_nodes = [self._doc_to_node(doc) for doc in all_cases]
            integrated_nodes, integrated_edges = await self.integrate_statute_cases(
                statute_nodes, case_nodes
            )
            synthesis_results["integration"] = {
                "nodes": integrated_nodes,
                "edges": integrated_edges
            }
        
        return synthesis_results
    
    def _doc_to_node(self, doc: Dict[str, Any]) -> EntityNode:
        """Convert document to entity node."""
        metadata = doc.get('metadata', {})
        doc_type = metadata.get('document_type', 'unknown')
        
        # Create appropriate entity based on type
        if doc_type == 'case_law':
            entity_class = LEGAL_ENTITY_TYPES['CaseLaw']
        elif doc_type == 'statute':
            entity_class = LEGAL_ENTITY_TYPES['Statute']
        else:
            entity_class = EntityNode
        
        return entity_class(
            uuid=doc.get('uuid', ''),
            name=metadata.get('title', 'Untitled'),
            summary=doc.get('summary', ''),
            **{k: v for k, v in metadata.items() if k in entity_class.__fields__}
        )


# Extension function to add synthetic graph capabilities to Graphiti
def extend_graphiti_with_synthesis():
    """Extend Graphiti with legal graph synthesis capabilities."""
    from graphiti_core.graphiti import Graphiti
    
    async def create_legal_research_graph(
        self,
        research_question: str,
        websites: List[str] = None,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """Create comprehensive legal research graph."""
        synthesizer = LegalGraphSynthesizer(self)
        return await synthesizer.create_legal_research_graph(
            research_question, websites, max_depth
        )
    
    async def analyze_legal_relationship(
        self,
        entity1_uuid: str,
        entity2_uuid: str,
        analysis_type: str = "relationship"
    ) -> Dict[str, Any]:
        """Analyze relationship between two legal entities."""
        synthesizer = LegalGraphSynthesizer(self)
        
        # Get entities
        entity1 = await EntityNode.get_by_uuid(self.driver, entity1_uuid)
        entity2 = await EntityNode.get_by_uuid(self.driver, entity2_uuid)
        
        # Determine analysis based on entity types
        if hasattr(entity1, 'citation') and hasattr(entity2, 'section'):
            # Case analyzing statute
            return await synthesizer.analyze_case_to_law({
                "case_name": entity1.name,
                "citation": entity1.citation,
                "statute_name": entity2.name,
                "section": entity2.section
            })
        elif hasattr(entity1, 'section') and hasattr(entity2, 'citation'):
            # Statute interpreted by case
            return await synthesizer.analyze_law_to_case({
                "statute_name": entity1.name,
                "section": entity1.section,
                "case_name": entity2.name,
                "citation": entity2.citation
            })
        else:
            # General relationship analysis
            return {
                "entity1": entity1.name,
                "entity2": entity2.name,
                "relationship_type": "general",
                "analysis": "Relationship analysis between these entity types"
            }
    
    # Add methods to Graphiti
    Graphiti.create_legal_research_graph = create_legal_research_graph
    Graphiti.analyze_legal_relationship = analyze_legal_relationship
    
    logger.info("Extended Graphiti with legal synthesis capabilities")