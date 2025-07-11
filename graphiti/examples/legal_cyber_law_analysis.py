"""
Example: Indian Cyber Law Analysis with Graphiti

This example demonstrates how to use Graphiti's enhanced capabilities for:
1. Crawling legal documents from Indian legal websites
2. Extracting legal entities and relationships
3. Creating synthetic knowledge graphs
4. Performing advanced legal analysis
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.legal_entities import LEGAL_ENTITY_TYPES
from graphiti_core.graphiti_web_extension import extend_graphiti_with_web_capabilities
from graphiti_core.synthetic_legal_graph import extend_graphiti_with_synthesis
from graphiti_core.legal_analysis_prompts import AnalysisType

load_dotenv()


async def main():
    """Main example demonstrating legal analysis capabilities."""
    
    # Initialize Graphiti with legal extensions
    graphiti = Graphiti(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password"),
    )
    
    # Extend with web crawling and synthesis capabilities
    extend_graphiti_with_web_capabilities()
    extend_graphiti_with_synthesis()
    
    # Initialize the graph
    await graphiti.build_indices_and_constraints()
    
    print("=== Indian Cyber Law Knowledge Graph Example ===\n")
    
    # Example 1: Process a specific cyber law case
    print("1. Processing a landmark cyber law case...")
    
    # Shreya Singhal v. Union of India - Section 66A IT Act case
    case_url = "https://indiankanoon.org/doc/110813550/"
    
    result = await graphiti.add_legal_document_from_web(
        url=case_url,
        group_id="landmark_cyber_cases",
        use_llm_extraction=True
    )
    
    print(f"✓ Added case: {result.episode.name}")
    print(f"  - Cyber law relevance: {result.cyber_law_relevance_score:.2f}")
    print(f"  - Entities extracted: {len(result.legal_entities)}")
    
    # Example 2: Bulk process multiple cyber law documents
    print("\n2. Processing multiple cyber law documents...")
    
    cyber_law_urls = [
        # IT Act provisions
        "https://www.meity.gov.in/writereaddata/files/itact2000/",
        # Data protection cases
        "https://indiankanoon.org/search/?formInput=data+protection+cyber",
        # Intermediary liability cases
        "https://indiankanoon.org/search/?formInput=intermediary+liability+section+79"
    ]
    
    bulk_results = await graphiti.add_legal_documents_bulk_from_web(
        urls=cyber_law_urls,
        group_id="cyber_law_corpus",
        use_llm_extraction=True
    )
    
    print(f"✓ Processed {len(bulk_results)} documents")
    
    # Example 3: Search for specific cyber law concepts
    print("\n3. Searching for data protection principles...")
    
    search_results = await graphiti.search_legal_knowledge(
        query="data protection privacy cyber law India",
        group_ids=["cyber_law_corpus"],
        cyber_law_categories=["Data Protection & Privacy"],
        limit=5
    )
    
    print(f"✓ Found {len(search_results.nodes)} relevant entities")
    for node in search_results.nodes[:3]:
        print(f"  - {node.name} ({node.__class__.__name__})")
    
    # Example 4: Create synthetic legal research graph
    print("\n4. Creating comprehensive legal research graph...")
    
    research_question = "What are the legal requirements for data breach notification in India?"
    
    research_graph = await graphiti.create_legal_research_graph(
        research_question=research_question,
        websites=["indiankanoon", "meity"],
        max_depth=2
    )
    
    print(f"✓ Research complete:")
    print(f"  - Documents analyzed: {research_graph['documents_analyzed']}")
    print(f"  - Sources searched: {', '.join(research_graph['sources_searched'])}")
    
    if 'case_synthesis' in research_graph:
        print(f"  - Synthetic principles created: {len(research_graph['case_synthesis']['nodes'])}")
        print(f"  - Relationships mapped: {len(research_graph['case_synthesis']['edges'])}")
    
    # Example 5: Analyze relationship between statute and case
    print("\n5. Analyzing statute-case relationships...")
    
    # Find IT Act Section 43A (data protection)
    statute_search = await graphiti.search(
        query="Section 43A Information Technology Act compensation data protection",
        group_ids=["cyber_law_corpus"],
        limit=1
    )
    
    if statute_search.nodes:
        statute_node = statute_search.nodes[0]
        
        # Find cases interpreting this section
        case_search = await graphiti.search(
            query="Section 43A interpretation data breach compensation",
            group_ids=["cyber_law_corpus"],
            limit=1
        )
        
        if case_search.nodes:
            case_node = case_search.nodes[0]
            
            # Analyze relationship
            analysis = await graphiti.analyze_legal_relationship(
                entity1_uuid=case_node.uuid,
                entity2_uuid=statute_node.uuid,
                analysis_type="interpretation"
            )
            
            print(f"✓ Relationship analysis complete")
            print(f"  - Case: {case_node.name}")
            print(f"  - Statute: {statute_node.name}")
            print(f"  - Analysis type: Case interpreting statute")
    
    # Example 6: Extract compliance requirements
    print("\n6. Extracting cyber law compliance requirements...")
    
    # Search for compliance-related content
    compliance_search = await graphiti.search(
        query="cyber security compliance requirements CERT-In guidelines",
        group_ids=["cyber_law_corpus"],
        limit=10
    )
    
    compliance_entities = [
        node for node in compliance_search.nodes 
        if hasattr(node, 'compliance_requirements')
    ]
    
    print(f"✓ Found {len(compliance_entities)} compliance-related entities")
    
    # Example 7: Track legal principle evolution
    print("\n7. Tracking evolution of privacy principles...")
    
    # Search for privacy-related cases over time
    privacy_cases = await graphiti.search(
        query="right to privacy cyber law digital personal data",
        group_ids=["landmark_cyber_cases", "cyber_law_corpus"],
        limit=10
    )
    
    # Sort by date if available
    dated_cases = [
        case for case in privacy_cases.nodes 
        if hasattr(case, 'date') and hasattr(case, 'citation')
    ]
    
    if dated_cases:
        dated_cases.sort(key=lambda x: x.date)
        
        print(f"✓ Privacy principle evolution:")
        for case in dated_cases[:5]:
            print(f"  - {case.date}: {case.name}")
            if hasattr(case, 'key_holding'):
                print(f"    Key holding: {case.key_holding[:100]}...")
    
    # Example 8: Generate cyber law knowledge summary
    print("\n8. Generating cyber law knowledge summary...")
    
    summary_query = """
    Summarize the current state of cyber law in India covering:
    1. Data protection requirements
    2. Intermediary liability
    3. Cyber crime provisions
    4. Recent judicial trends
    """
    
    # Use the graph to answer complex questions
    summary_results = await graphiti.search(
        query=summary_query,
        group_ids=["landmark_cyber_cases", "cyber_law_corpus"],
        limit=20
    )
    
    print(f"✓ Knowledge summary based on {len(summary_results.nodes)} entities")
    print("  Key areas covered:")
    
    # Group by entity type
    entity_types = {}
    for node in summary_results.nodes:
        entity_type = node.__class__.__name__
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
    
    for entity_type, count in entity_types.items():
        print(f"  - {entity_type}: {count} entities")
    
    print("\n=== Example Complete ===")
    print("\nNext steps:")
    print("1. Schedule regular crawls of legal websites for updates")
    print("2. Build specialized compliance checklists from the graph")
    print("3. Create legal research assistants using the knowledge")
    print("4. Generate case prediction models based on patterns")
    print("5. Build automated legal document drafting tools")


if __name__ == "__main__":
    asyncio.run(main())