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

from typing import Any, Protocol, TypedDict

from pydantic import BaseModel, Field

from .models import Message, PromptFunction, PromptVersion


class LegalEntity(BaseModel):
    """Base model for legal entities."""
    name: str = Field(..., description='Name of the legal entity')
    entity_type: str = Field(..., description='Type: case_law, statute, principle, procedure, party, judge')
    description: str = Field(..., description='Brief description of the entity')
    cyber_law_relevance: float = Field(
        default=0.0, 
        ge=0.0, 
        le=1.0,
        description='Relevance score to cyber law (0-1)'
    )


class CaseLawEntity(LegalEntity):
    """Case law specific entity."""
    citation: str = Field(..., description='Legal citation')
    court: str = Field(..., description='Court name')
    date: str = Field(..., description='Decision date')
    key_holding: str = Field(..., description='Key legal holding')


class StatuteEntity(LegalEntity):
    """Statute or regulation entity."""
    section: str = Field(..., description='Section number')
    act_name: str = Field(..., description='Name of the Act')
    jurisdiction: str = Field(..., description='Applicable jurisdiction')


class LegalPrincipleEntity(LegalEntity):
    """Legal principle or doctrine entity."""
    established_by: str = Field(..., description='Case or statute that established this principle')
    application_area: str = Field(..., description='Area of law where this principle applies')


class ExtractedLegalEntities(BaseModel):
    """Container for all extracted legal entities."""
    case_laws: list[CaseLawEntity] = Field(default_factory=list)
    statutes: list[StatuteEntity] = Field(default_factory=list)
    principles: list[LegalPrincipleEntity] = Field(default_factory=list)
    general_entities: list[LegalEntity] = Field(default_factory=list)


class LegalRelationship(BaseModel):
    """Relationship between legal entities."""
    source_entity: str = Field(..., description='Name of the source entity')
    target_entity: str = Field(..., description='Name of the target entity')
    relationship_type: str = Field(
        ..., 
        description='Type: cites, overrules, distinguishes, applies, interprets, amends'
    )
    description: str = Field(..., description='Description of the relationship')


class ExtractedLegalRelationships(BaseModel):
    """Container for extracted legal relationships."""
    relationships: list[LegalRelationship] = Field(default_factory=list)


class ExtractLegalEntitiesPromptInputs(Protocol):
    """Input protocol for legal entity extraction."""
    context: str
    cyber_law_focus: bool
    jurisdiction: str
    entity_types: list[str]


async def extract_legal_entities_prompt_v1(
    inputs: ExtractLegalEntitiesPromptInputs,
) -> list[Message]:
    """Extract legal entities from legal documents with focus on cyber law."""
    
    context = f"""
You are a legal AI assistant specialized in Indian Cyber Law. Extract legal entities from the provided text.

Focus Areas for Cyber Law:
1. Information Technology Act, 2000 and amendments
2. Data protection and privacy laws
3. Cybercrime and electronic evidence
4. Digital signatures and electronic contracts
5. Intermediary liability
6. Cyber security regulations

Text to analyze:
{inputs.context}

Jurisdiction: {inputs.jurisdiction}
Entity types to extract: {', '.join(inputs.entity_types)}
Cyber law focus: {'Yes - prioritize cyber law relevance' if inputs.cyber_law_focus else 'No - general legal extraction'}

Instructions:
1. Identify all legal entities (cases, statutes, principles, procedures)
2. For each entity, assess its relevance to cyber law (0-1 score)
3. Extract key relationships between entities
4. Focus on precedents that shape cyber law jurisprudence
5. Identify procedures relevant to cyber law practice
"""

    return [
        Message(
            role='system',
            content='You are an expert legal analyst specializing in Indian Cyber Law. '
            'Extract structured legal information that can be used to build a comprehensive legal knowledge graph.'
        ),
        Message(role='user', content=context),
    ]


async def extract_legal_relationships_prompt_v1(
    entities: list[LegalEntity],
    context: str,
) -> list[Message]:
    """Extract relationships between legal entities."""
    
    entities_list = '\n'.join([f"- {e.name} ({e.entity_type})" for e in entities])
    
    prompt = f"""
Given the following legal entities and context, identify relationships between them:

Entities:
{entities_list}

Context:
{context}

Identify relationships such as:
- Citation relationships (case A cites case B)
- Overruling relationships (case A overrules case B)
- Statutory interpretation (case interprets statute)
- Principle application (case applies legal principle)
- Procedural relationships (procedure derives from statute/case)

For cyber law, pay special attention to:
- How cases interpret IT Act provisions
- Evolution of data protection principles
- Cybercrime investigation procedures
- Digital evidence admissibility standards
"""

    return [
        Message(
            role='system',
            content='You are a legal relationship analyst. Identify and categorize relationships between legal entities.'
        ),
        Message(role='user', content=prompt),
    ]


async def classify_legal_relevance_prompt_v1(
    text: str,
    cyber_law_categories: list[str],
) -> list[Message]:
    """Classify text relevance to different cyber law categories."""
    
    categories_list = '\n'.join([f"- {cat}" for cat in cyber_law_categories])
    
    prompt = f"""
Analyze the following legal text and classify its relevance to cyber law categories:

Text:
{text}

Cyber Law Categories:
{categories_list}

For each category, provide:
1. Relevance score (0-1)
2. Key points that make it relevant
3. Practical implications for cyber law practice

Also identify:
- Novel legal principles for cyber law
- Procedural insights for cyber cases
- Compliance requirements mentioned
"""

    return [
        Message(
            role='system',
            content='You are a cyber law classification expert. Analyze legal texts for their relevance to various aspects of cyber law.'
        ),
        Message(role='user', content=prompt),
    ]


def extract_legal_entities(context: dict[str, Any]) -> list[Message]:
    """Extract legal entities from legal documents."""
    
    sys_prompt = """You are a legal AI assistant specialized in Indian Cyber Law. 
    Extract legal entities from the provided text with focus on cyber law relevance."""
    
    user_prompt = f"""
<TEXT>
{context['content']}
</TEXT>

Focus Areas for Cyber Law:
1. Information Technology Act, 2000 and amendments
2. Data protection and privacy laws
3. Cybercrime and electronic evidence
4. Digital signatures and electronic contracts
5. Intermediary liability
6. Cyber security regulations

Extract the following types of legal entities:
- Case Laws (with citations, court, date, key holdings)
- Statutes and Regulations (with sections and provisions)
- Legal Principles and Doctrines
- Legal Procedures and Processes
- Parties, Judges, and Legal Authorities

For each entity:
1. Provide a clear name
2. Classify its type
3. Assess cyber law relevance (0-1 score)
4. Extract key attributes
5. Note relationships to other entities

{context.get('custom_prompt', '')}
"""
    
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def extract_legal_relationships(context: dict[str, Any]) -> list[Message]:
    """Extract relationships between legal entities."""
    
    sys_prompt = """You are a legal relationship analyst. 
    Identify and categorize relationships between legal entities."""
    
    entities_list = '\n'.join([f"- {e['name']} ({e['type']})" for e in context['entities']])
    
    user_prompt = f"""
<ENTITIES>
{entities_list}
</ENTITIES>

<CONTEXT>
{context['content']}
</CONTEXT>

Identify relationships such as:
- Citation relationships (case A cites case B)
- Overruling relationships (case A overrules case B)
- Statutory interpretation (case interprets statute)
- Principle application (case applies legal principle)
- Procedural relationships (procedure derives from statute/case)

For cyber law, pay special attention to:
- How cases interpret IT Act provisions
- Evolution of data protection principles
- Cybercrime investigation procedures
- Digital evidence admissibility standards
"""
    
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def classify_cyber_law_relevance(context: dict[str, Any]) -> list[Message]:
    """Classify content relevance to cyber law categories."""
    
    sys_prompt = """You are a cyber law classification expert. 
    Analyze legal texts for their relevance to various aspects of cyber law."""
    
    categories = context.get('categories', [
        'Data Protection & Privacy',
        'Cybercrime & Electronic Evidence',
        'Digital Contracts & E-Commerce',
        'Intermediary Liability',
        'Cyber Security Compliance',
        'Digital Rights & Freedom'
    ])
    
    user_prompt = f"""
<TEXT>
{context['content']}
</TEXT>

<CATEGORIES>
{chr(10).join([f"- {cat}" for cat in categories])}
</CATEGORIES>

Analyze the text and for each category provide:
1. Relevance score (0-1)
2. Key points that make it relevant
3. Practical implications for cyber law practice
4. Precedential value

Also identify:
- Novel legal principles for cyber law
- Procedural insights for cyber cases
- Compliance requirements mentioned
"""
    
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


# Version mappings
Versions = TypedDict(
    'Versions',
    {
        'extract_legal_entities': Any,
        'extract_legal_relationships': Any,
        'classify_cyber_law_relevance': Any,
    },
)

Prompt = TypedDict(
    'Prompt',
    {
        'extract_legal_entities': Any,
        'extract_legal_relationships': Any,
        'classify_cyber_law_relevance': Any,
    },
)

versions: Versions = {
    'extract_legal_entities': extract_legal_entities,
    'extract_legal_relationships': extract_legal_relationships,
    'classify_cyber_law_relevance': classify_cyber_law_relevance,
}