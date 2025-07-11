# Legal AI Integration for Graphiti

This document describes the integration of Crawl4AI and advanced legal analysis capabilities into Graphiti for building Indian Cyber Law knowledge graphs.

## Overview

The integration adds the following capabilities to Graphiti:

1. **Web Crawling**: Automated extraction of legal documents from Indian legal websites
2. **Legal Entity Recognition**: Specialized entities for case law, statutes, principles, etc.
3. **Advanced Prompt Engineering**: Sophisticated analysis prompts for legal reasoning
4. **Synthetic Graph Generation**: Creating derived knowledge from multiple sources
5. **Bi-directional Analysis**: Case-to-law and law-to-case relationship mapping

## Architecture

### New Modules

1. **`graphiti_core/utils/web_crawler.py`**
   - WebCrawler class using Crawl4AI
   - Legal document extraction strategies
   - Support for both LLM and CSS-based extraction

2. **`graphiti_core/legal_entities.py`**
   - CaseLaw, Statute, LegalPrinciple, LegalProcedure entities
   - LegalAuthority, CyberIncident, LegalArgument, LegalConcept entities
   - Cyber law relevance scoring

3. **`graphiti_core/legal_analysis_prompts.py`**
   - AnalysisType enum for different analysis modes
   - LegalWebsiteSchema for Indian legal websites
   - LegalAnalysisPrompts dictionary with reusable prompts
   - SyntheticGraphPrompts for knowledge synthesis

4. **`graphiti_core/synthetic_legal_graph.py`**
   - LegalGraphSynthesizer for advanced analysis
   - Methods for case-to-law and law-to-case analysis
   - Synthetic node and edge generation
   - Multi-source knowledge integration

5. **`graphiti_core/graphiti_web_extension.py`**
   - Extensions to Graphiti class for web capabilities
   - Legal document crawling methods
   - Specialized legal search functionality

## Supported Legal Websites

### Configured Schemas

1. **Indian Kanoon** (`indiankanoon`)
   - Search endpoint: `/search/?formInput=`
   - Document endpoint: `/doc/`
   - CSS selectors for title, court, date, content, citations
   - Cyber law keywords for filtering

2. **Supreme Court of India** (`sci_india`)
   - Judgments endpoint: `/judgments`
   - Selectors for judgment components

3. **MeitY** (`meity`)
   - Acts, rules, notifications, guidelines sections
   - IT Act and related regulations

4. **CIS India** (`cis_india`)
   - Research areas: privacy, surveillance, data governance

5. **SFLC.in** (`sflc`)
   - Legal updates and policy analysis

## Legal Analysis Types

### 1. Case-to-Law Analysis
Analyzes court cases to identify:
- Applicable statutory provisions
- Judicial interpretations
- Compliance implications
- Legal gaps revealed

### 2. Law-to-Case Analysis
Tracks how statutes are interpreted:
- Evolution of interpretation
- Conflicting court views
- Settled principles
- Compliance best practices

### 3. Principle Extraction
Extracts fundamental legal principles:
- Tests and frameworks
- Balancing approaches
- Procedural innovations
- Digital evidence standards

### 4. Precedent Mapping
Maps precedential relationships:
- Binding vs persuasive precedents
- Following/distinguishing/overruling
- Precedent evolution chains

### 5. Argument Analysis
Analyzes legal argumentation:
- Successful strategies
- Counter-arguments
- Technical evidence role
- Persuasive techniques

### 6. Compliance Mapping
Extracts actionable compliance:
- Mandatory requirements
- Best practices
- Prohibited actions
- Industry-specific needs

## Usage Examples

### Basic Legal Document Processing

```python
from graphiti_core import Graphiti
from graphiti_core import extend_graphiti_with_web_capabilities

# Initialize and extend Graphiti
graphiti = Graphiti(uri="bolt://localhost:7687", user="neo4j", password="password")
extend_graphiti_with_web_capabilities()

# Process a legal document
result = await graphiti.add_legal_document_from_web(
    url="https://indiankanoon.org/doc/110813550/",
    group_id="cyber_law_cases",
    use_llm_extraction=True
)
```

### Advanced Legal Research

```python
from graphiti_core import extend_graphiti_with_synthesis

# Add synthesis capabilities
extend_graphiti_with_synthesis()

# Create comprehensive research graph
research = await graphiti.create_legal_research_graph(
    research_question="What are the data breach notification requirements in India?",
    websites=["indiankanoon", "meity"],
    max_depth=3
)
```

### Legal Knowledge Search

```python
# Search with legal filters
results = await graphiti.search_legal_knowledge(
    query="data protection privacy",
    cyber_law_categories=["Data Protection & Privacy"],
    case_law_only=True,
    limit=10
)
```

## Prompt Engineering Dictionary

The system maintains reusable prompts in `LegalAnalysisPrompts.PROMPTS`:

- **Case-to-Law**: Maps cases to applicable statutes
- **Law-to-Case**: Tracks statutory interpretation
- **Principle Extraction**: Identifies legal principles
- **Precedent Mapping**: Maps case relationships
- **Argument Analysis**: Analyzes legal arguments
- **Compliance Mapping**: Extracts requirements

Each prompt includes:
- System prompt for context
- Template with placeholders
- Extraction schema for structured output

## Synthetic Graph Generation

The system can create synthetic nodes and edges representing:

1. **Common Principles**: Extracted across multiple cases
2. **Evolution Edges**: Showing legal development over time
3. **Interpretation Edges**: Linking cases to statutes
4. **Compliance Nodes**: Practical guidelines from case law
5. **Prediction Nodes**: Likely future developments

## Integration with Existing Graphiti

The integration is designed to be non-intrusive:

1. All legal functionality is in separate modules
2. Extensions use monkey-patching to add methods
3. Original Graphiti functionality remains unchanged
4. Legal entities are added through standard entity_types parameter

## Next Steps for Legal-AI-Agents-IND Repository

1. **Create Repository Structure**:
   ```
   Legal-AI-Agents-IND/
   ├── crawlers/
   │   ├── sources/
   │   │   ├── indiankanoon.py
   │   │   ├── sci_judgments.py
   │   │   ├── legal_blogs.py
   │   │   └── law_journals.py
   │   └── scheduler.py
   ├── agents/
   │   ├── research_agent.py
   │   ├── compliance_agent.py
   │   ├── case_analysis_agent.py
   │   └── legal_drafting_agent.py
   ├── prompts/
   │   └── (copy legal prompts)
   ├── examples/
   │   └── (legal use cases)
   └── README.md
   ```

2. **Implement Scheduled Crawling**:
   - Daily updates from legal websites
   - Change detection for amended laws
   - New case law monitoring

3. **Build Specialized Agents**:
   - Legal research assistant
   - Compliance checker
   - Case outcome predictor
   - Legal document drafter

4. **Create Claude Context**:
   - .claude/context.md with legal domain knowledge
   - Prompt templates for legal tasks
   - Best practices for legal AI

## Dependencies

Add to requirements:
```
crawl4ai>=0.4.0
```

## Testing

Run the example:
```bash
python examples/legal_cyber_law_analysis.py
```

This will demonstrate:
1. Crawling legal documents
2. Extracting entities
3. Creating synthetic relationships
4. Performing legal analysis
5. Searching legal knowledge