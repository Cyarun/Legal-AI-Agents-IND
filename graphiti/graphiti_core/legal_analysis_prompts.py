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

from typing import Dict, List, Any, Optional
from enum import Enum


class AnalysisType(Enum):
    """Types of legal analysis."""
    CASE_TO_LAW = "case_to_law"
    LAW_TO_CASE = "law_to_case"
    PRINCIPLE_EXTRACTION = "principle_extraction"
    PRECEDENT_MAPPING = "precedent_mapping"
    ARGUMENT_ANALYSIS = "argument_analysis"
    COMPLIANCE_MAPPING = "compliance_mapping"
    INCIDENT_ANALYSIS = "incident_analysis"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    TEMPORAL_EVOLUTION = "temporal_evolution"
    JURISDICTION_MAPPING = "jurisdiction_mapping"


class LegalWebsiteSchema:
    """Schema definitions for different legal websites."""
    
    SCHEMAS = {
        "indiankanoon": {
            "base_url": "https://indiankanoon.org",
            "search_endpoint": "/search/?formInput=",
            "doc_endpoint": "/doc/",
            "selectors": {
                "title": "h2.doc_title",
                "court": "div.docsource_main",
                "date": "div.doc_date",
                "content": "div.judgments",
                "citations": "div.doc_cite",
                "judges": "div.doc_author",
                "referred_cases": "a.case_title"
            },
            "cyber_law_keywords": [
                "information technology act",
                "section 66", "section 67", "section 69",
                "cyber", "digital", "electronic",
                "data protection", "privacy",
                "intermediary", "cyber crime"
            ]
        },
        "sci_india": {
            "base_url": "https://main.sci.gov.in",
            "search_endpoint": "/judgments",
            "selectors": {
                "title": "div.judgment-title",
                "bench": "div.bench-info",
                "date": "span.judgment-date",
                "content": "div.judgment-text",
                "headnotes": "div.headnotes"
            }
        },
        "meity": {
            "base_url": "https://www.meity.gov.in",
            "sections": {
                "acts": "/content/acts",
                "rules": "/content/rules",
                "notifications": "/content/notifications",
                "guidelines": "/content/guidelines"
            }
        },
        "cis_india": {
            "base_url": "https://cis-india.org",
            "research_areas": [
                "privacy", "surveillance", "data-governance",
                "internet-governance", "digital-economy"
            ]
        },
        "sflc": {
            "base_url": "https://sflc.in",
            "sections": {
                "legal": "/legal",
                "policy": "/policy",
                "updates": "/updates"
            }
        }
    }
    
    @classmethod
    def get_schema(cls, website: str) -> Dict[str, Any]:
        """Get schema for a specific website."""
        return cls.SCHEMAS.get(website, {})


class LegalAnalysisPrompts:
    """Advanced prompts for legal analysis and synthetic graph generation."""
    
    # Core analysis prompts
    PROMPTS = {
        AnalysisType.CASE_TO_LAW: {
            "system": """You are an expert legal analyst specializing in Indian Cyber Law. 
            Your task is to analyze case law and identify applicable statutory provisions.""",
            
            "template": """Analyze the following case and identify all applicable laws:

Case Details:
{case_name}
Court: {court}
Citation: {citation}
Date: {date}

Facts:
{facts}

Legal Issues:
{issues}

Judgment:
{judgment}

Tasks:
1. Identify all statutory provisions applied or discussed
2. Map each legal issue to relevant sections of law
3. Explain how the court interpreted each provision
4. Note any novel interpretations or applications
5. Identify gaps in statutory coverage revealed by the case
6. Suggest applicable provisions that weren't considered

Focus on:
- Information Technology Act, 2000 and amendments
- Indian Penal Code cyber crime sections
- Evidence Act provisions for electronic evidence
- Data protection regulations
- Any other relevant cyber law provisions

Output Format:
- Statutory Mapping: Issue -> Provision -> Interpretation
- Novel Applications: New interpretations of existing law
- Legal Gaps: Areas needing legislative attention
- Compliance Implications: What organizations must do
""",
            
            "extraction_schema": {
                "statutory_mappings": [
                    {
                        "issue": "str",
                        "provisions": ["str"],
                        "interpretation": "str",
                        "precedential_value": "str"
                    }
                ],
                "novel_applications": ["str"],
                "legal_gaps": ["str"],
                "compliance_requirements": ["str"]
            }
        },
        
        AnalysisType.LAW_TO_CASE: {
            "system": """You are an expert legal researcher specializing in case law analysis.
            Your task is to find how statutory provisions have been interpreted and applied.""",
            
            "template": """Analyze how the following statutory provision has been interpreted:

Statute: {statute_name}
Section: {section}
Text: {section_text}

Research Tasks:
1. Identify all major cases interpreting this provision
2. Track evolution of interpretation over time
3. Note conflicting interpretations by different courts
4. Identify settled principles vs. open questions
5. Map factual scenarios where this provision applies
6. Extract compliance best practices from case law

Analysis Framework:
- Literal interpretation vs. Purposive interpretation
- Strict construction vs. Liberal construction
- Harmonious construction with other provisions
- Constitutional validity challenges
- Practical difficulties in implementation

Required Output:
- Case Timeline: Chronological interpretation evolution
- Interpretation Matrix: Court -> Interpretation -> Reasoning
- Settled Principles: Universally accepted interpretations
- Open Questions: Conflicting or unclear areas
- Compliance Checklist: Dos and Don'ts from case law
""",
            
            "extraction_schema": {
                "case_interpretations": [
                    {
                        "case_name": "str",
                        "court": "str",
                        "year": "str",
                        "interpretation": "str",
                        "key_reasoning": "str",
                        "impact": "str"
                    }
                ],
                "evolution_timeline": ["str"],
                "settled_principles": ["str"],
                "open_questions": ["str"],
                "compliance_checklist": {
                    "mandatory": ["str"],
                    "recommended": ["str"],
                    "prohibited": ["str"]
                }
            }
        },
        
        AnalysisType.PRINCIPLE_EXTRACTION: {
            "system": """You are a legal scholar extracting fundamental principles from cyber law cases.
            Focus on principles that can guide future legal reasoning.""",
            
            "template": """Extract legal principles from the following material:

Content:
{content}

Extract:
1. Fundamental principles established
2. Tests or frameworks created by courts
3. Balancing approaches for competing interests
4. Presumptions and burden of proof rules
5. Interpretive guidelines for cyber law
6. Procedural innovations for digital evidence

For each principle:
- Name and define the principle clearly
- Identify the source case/statute
- Explain the rationale
- Provide application examples
- Note any limitations or exceptions
- Assess future applicability

Special Focus Areas:
- Digital privacy principles
- Electronic evidence standards
- Intermediary liability frameworks
- Cyber crime investigation principles
- Data protection compliance principles
""",
            
            "extraction_schema": {
                "principles": [
                    {
                        "name": "str",
                        "definition": "str",
                        "source": "str",
                        "rationale": "str",
                        "applications": ["str"],
                        "limitations": ["str"],
                        "cyber_law_relevance": "float"
                    }
                ]
            }
        },
        
        AnalysisType.PRECEDENT_MAPPING: {
            "system": """You are a legal analyst creating a precedent map for cyber law cases.
            Track how precedents are cited, followed, distinguished, or overruled.""",
            
            "template": """Map the precedential relationships in the following cases:

Cases:
{cases}

Create a precedent network showing:
1. Binding precedents vs. persuasive precedents
2. Cases following earlier precedents
3. Cases distinguishing precedents
4. Cases overruling precedents
5. Parallel precedents from other jurisdictions
6. Academic criticism of precedents

Analysis Requirements:
- Identify the rule of law from each precedent
- Track how the rule evolved through cases
- Note factual distinctions affecting application
- Assess current validity of each precedent
- Predict future precedential trends

Special Considerations:
- Foreign precedents in Indian cyber law
- Technology changes affecting precedent validity
- Legislative overruling of judicial precedents
""",
            
            "extraction_schema": {
                "precedent_network": [
                    {
                        "source_case": "str",
                        "cited_case": "str",
                        "relationship": "str",  # follows/distinguishes/overrules
                        "rule_of_law": "str",
                        "factual_distinction": "str",
                        "current_validity": "str"
                    }
                ],
                "precedent_chains": [
                    {
                        "principle": "str",
                        "evolution": ["str"]
                    }
                ]
            }
        },
        
        AnalysisType.ARGUMENT_ANALYSIS: {
            "system": """You are analyzing legal arguments in cyber law cases to understand 
            successful and unsuccessful argumentation strategies.""",
            
            "template": """Analyze the legal arguments in the following case:

Case: {case_details}

Extract and analyze:
1. Petitioner/Plaintiff arguments
2. Respondent/Defendant arguments
3. Intervener arguments (if any)
4. Court's reasoning on each argument
5. Successful vs. unsuccessful arguments
6. Novel arguments and their reception

For each argument:
- Core proposition
- Legal authorities cited
- Factual basis
- Counter-arguments
- Court's response
- Success factors or failure reasons

Meta-analysis:
- Effective argumentation patterns
- Common logical fallacies to avoid
- Persuasive techniques that worked
- Role of technical evidence
""",
            
            "extraction_schema": {
                "arguments": [
                    {
                        "party": "str",
                        "argument": "str",
                        "authorities": ["str"],
                        "court_response": "str",
                        "outcome": "str",
                        "effectiveness_factors": ["str"]
                    }
                ],
                "argumentation_patterns": ["str"],
                "technical_evidence_role": "str"
            }
        },
        
        AnalysisType.COMPLIANCE_MAPPING: {
            "system": """You are a compliance expert extracting actionable compliance 
            requirements from cyber law cases and statutes.""",
            
            "template": """Extract compliance requirements from the following legal material:

Material:
{content}

Identify:
1. Mandatory compliance requirements
2. Best practices endorsed by courts
3. Practices specifically prohibited
4. Safe harbors and exemptions
5. Compliance timelines and deadlines
6. Penalties for non-compliance

For each requirement:
- Specific obligation
- Who must comply
- How to comply
- When to comply
- Consequences of non-compliance
- Monitoring/audit requirements

Industry-specific requirements for:
- IT companies
- E-commerce platforms
- Financial institutions
- Healthcare providers
- Educational institutions
- Government departments
""",
            
            "extraction_schema": {
                "compliance_requirements": [
                    {
                        "requirement": "str",
                        "applicable_to": ["str"],
                        "compliance_steps": ["str"],
                        "deadline": "str",
                        "penalties": "str",
                        "safe_harbors": ["str"]
                    }
                ],
                "industry_specific": {
                    "industry": "str",
                    "special_requirements": ["str"]
                }
            }
        }
    }
    
    @classmethod
    def get_prompt(cls, analysis_type: AnalysisType) -> Dict[str, Any]:
        """Get prompt for specific analysis type."""
        return cls.PROMPTS.get(analysis_type, {})
    
    @classmethod
    def create_custom_prompt(
        cls, 
        analysis_goal: str,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create custom prompt for specific analysis needs."""
        return {
            "system": f"You are a legal analyst specializing in {analysis_goal}.",
            "template": f"""Analyze the following content for {analysis_goal}:
            
{{content}}

Required Analysis:
{analysis_goal}

Output must follow the specified schema.
""",
            "input_schema": input_schema,
            "extraction_schema": output_schema
        }


class SyntheticGraphPrompts:
    """Prompts for generating synthetic legal knowledge graphs."""
    
    SYNTHESIS_PROMPTS = {
        "case_law_synthesis": """Given the following related cases, synthesize a comprehensive understanding:

Cases:
{cases}

Create synthetic nodes and relationships showing:
1. Common legal principles across cases
2. Evolution of judicial thinking
3. Factual patterns leading to different outcomes
4. Emerging trends in cyber law jurisprudence
5. Predictive patterns for future cases

Generate:
- Synthetic principle nodes connecting multiple cases
- Temporal evolution edges showing legal development
- Similarity edges between factually similar cases
- Distinction edges between conflicting decisions
- Prediction nodes for likely future developments
""",
        
        "statute_case_integration": """Integrate statutory provisions with case law interpretations:

Statutes:
{statutes}

Cases:
{cases}

Generate synthetic relationships showing:
1. How each statute section is interpreted in practice
2. Gap between legislative intent and judicial interpretation
3. Areas where statute is silent but cases provide guidance
4. Compliance requirements emerging from case law
5. Best practices validated by courts

Output synthetic nodes for:
- Practical compliance guidelines
- Judicial glosses on statutory language
- Implied requirements not explicit in statute
- Safe harbor practices blessed by courts
""",
        
        "multi_jurisdiction_synthesis": """Synthesize cyber law principles across jurisdictions:

Jurisdictions and Materials:
{jurisdiction_materials}

Create synthetic understanding of:
1. Universal cyber law principles
2. Jurisdiction-specific variations
3. Conflicts of law in cyberspace
4. Best practices across jurisdictions
5. Emerging global standards

Generate synthetic nodes for:
- Universal principles accepted everywhere
- Comparative analysis nodes
- Conflict resolution frameworks
- Harmonization opportunities
"""
    }
    
    @classmethod
    def get_synthesis_prompt(cls, synthesis_type: str) -> str:
        """Get synthesis prompt for specific type."""
        return cls.SYNTHESIS_PROMPTS.get(synthesis_type, "")


class LegalSearchStrategies:
    """Search strategies for different legal research goals."""
    
    STRATEGIES = {
        "find_applicable_cases": {
            "keywords": ["applied", "interpreted", "section", "provision"],
            "filters": {
                "entity_type": ["CaseLaw"],
                "recency": "last_5_years"
            },
            "ranking": "precedential_value"
        },
        
        "find_compliance_requirements": {
            "keywords": ["comply", "requirement", "obligation", "must", "shall"],
            "filters": {
                "entity_type": ["Statute", "LegalProcedure"],
                "status": "active"
            },
            "ranking": "practical_relevance"
        },
        
        "find_precedents": {
            "keywords": ["established", "principle", "test", "framework"],
            "filters": {
                "entity_type": ["CaseLaw", "LegalPrinciple"],
                "precedential_value": ["binding", "persuasive"]
            },
            "ranking": "citation_count"
        },
        
        "find_definitions": {
            "keywords": ["means", "includes", "definition", "interpretation"],
            "filters": {
                "entity_type": ["Statute", "CaseLaw"],
                "content_type": "definitional"
            },
            "ranking": "authoritative_source"
        }
    }
    
    @classmethod
    def get_strategy(cls, goal: str) -> Dict[str, Any]:
        """Get search strategy for specific goal."""
        return cls.STRATEGIES.get(goal, {})