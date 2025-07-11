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

from typing import List, Optional

from pydantic import BaseModel, Field


class CaseLaw(BaseModel):
    """
    Case law entity for legal knowledge graph.
    Represents court decisions and judgments.
    """
    uuid: str = Field(description="Unique identifier")
    name: str = Field(description="Case name (e.g., 'State v. Defendant')")
    summary: str = Field(description="Brief summary of the case")
    citation: str = Field(description="Legal citation (e.g., '2023 SCC 45')")
    court: str = Field(description="Court name (e.g., 'Supreme Court of India')")
    date: str = Field(description="Decision date in ISO format")
    judges: List[str] = Field(default_factory=list, description="Names of judges")
    key_holding: str = Field(description="Primary legal holding of the case")
    cyber_law_category: str = Field(
        description="Category: data_protection, cybercrime, digital_evidence, etc."
    )
    cyber_law_relevance: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score to cyber law (0-1)"
    )
    precedential_value: str = Field(
        default="medium",
        description="Precedential value: binding, persuasive, informative"
    )
    legal_reasoning: List[str] = Field(
        default_factory=list,
        description="Key legal reasoning points"
    )
    applied_principles: List[str] = Field(
        default_factory=list,
        description="Legal principles applied in this case"
    )
    distinguished_cases: List[str] = Field(
        default_factory=list,
        description="Cases distinguished or overruled"
    )


class Statute(BaseModel):
    """
    Statute or regulation entity.
    Represents laws, acts, and regulations.
    """
    uuid: str = Field(description="Unique identifier")
    name: str = Field(description="Statute name (e.g., 'Information Technology Act, 2000')")
    summary: str = Field(description="Brief summary of the statute or section")
    section: str = Field(description="Section number (e.g., 'Section 66A')")
    act_name: str = Field(description="Full name of the Act")
    jurisdiction: str = Field(description="Applicable jurisdiction")
    enactment_date: Optional[str] = Field(description="Date of enactment")
    amendment_dates: List[str] = Field(default_factory=list, description="Amendment dates")
    cyber_law_relevance: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score to cyber law (0-1)"
    )
    status: str = Field(
        default="active",
        description="Status: active, repealed, amended"
    )
    interpretations: List[str] = Field(
        default_factory=list,
        description="Notable judicial interpretations"
    )
    related_sections: List[str] = Field(
        default_factory=list,
        description="Related statutory provisions"
    )


class LegalPrinciple(BaseModel):
    """
    Legal principle or doctrine entity.
    Represents established legal principles and doctrines.
    """
    uuid: str = Field(description="Unique identifier")
    name: str = Field(description="Principle name (e.g., 'Reasonable Expectation of Privacy')")
    summary: str = Field(description="Description of the principle")
    established_by: str = Field(description="Case or statute that established this principle")
    application_area: str = Field(description="Area of law where this principle applies")
    cyber_law_context: str = Field(description="How this principle applies to cyber law")
    examples: List[str] = Field(default_factory=list, description="Example applications")
    evolution: List[str] = Field(
        default_factory=list,
        description="Evolution of this principle over time"
    )
    exceptions: List[str] = Field(
        default_factory=list,
        description="Known exceptions to this principle"
    )


class LegalProcedure(BaseModel):
    """
    Legal procedure or process entity.
    Represents procedural requirements and processes.
    """
    uuid: str = Field(description="Unique identifier")
    name: str = Field(description="Procedure name (e.g., 'Digital Evidence Collection')")
    summary: str = Field(description="Description of the procedure")
    steps: List[str] = Field(description="Ordered list of procedural steps")
    applicable_to: str = Field(description="When/where this procedure applies")
    legal_basis: str = Field(description="Statute or case establishing this procedure")
    cyber_law_specific: bool = Field(
        default=False,
        description="Whether this is specific to cyber law"
    )
    compliance_requirements: List[str] = Field(
        default_factory=list,
        description="Compliance requirements"
    )
    best_practices: List[str] = Field(
        default_factory=list,
        description="Best practices for following this procedure"
    )
    common_mistakes: List[str] = Field(
        default_factory=list,
        description="Common mistakes to avoid"
    )


class LegalAuthority(BaseModel):
    """
    Legal authority entity.
    Represents judges, regulatory bodies, and other legal authorities.
    """
    uuid: str = Field(description="Unique identifier")
    name: str = Field(description="Authority name")
    summary: str = Field(description="Description of the authority")
    type: str = Field(description="Type: judge, regulator, tribunal, commission")
    jurisdiction: str = Field(description="Jurisdictional scope")
    cyber_law_expertise: bool = Field(
        default=False,
        description="Known for cyber law expertise"
    )
    notable_decisions: List[str] = Field(
        default_factory=list,
        description="Notable cyber law decisions"
    )
    judicial_philosophy: Optional[str] = Field(
        default=None,
        description="Known judicial philosophy or approach"
    )


class CyberIncident(BaseModel):
    """
    Cyber incident entity.
    Represents specific cyber incidents referenced in legal contexts.
    """
    uuid: str = Field(description="Unique identifier")
    name: str = Field(description="Incident name or identifier")
    summary: str = Field(description="Description of the incident")
    incident_type: str = Field(
        description="Type: data_breach, ransomware, identity_theft, etc."
    )
    date: str = Field(description="Incident date")
    impact: str = Field(description="Impact description")
    legal_implications: List[str] = Field(
        description="Legal implications and outcomes"
    )
    referenced_in: List[str] = Field(
        default_factory=list,
        description="Cases or statutes referencing this incident"
    )
    preventive_measures: List[str] = Field(
        default_factory=list,
        description="Preventive measures derived from this incident"
    )


class LegalArgument(BaseModel):
    """
    Legal argument entity.
    Represents specific legal arguments made in cases.
    """
    uuid: str = Field(description="Unique identifier")
    name: str = Field(description="Argument identifier")
    summary: str = Field(description="Summary of the argument")
    made_by: str = Field(description="Party making the argument")
    in_case: str = Field(description="Case where this argument was made")
    argument_type: str = Field(
        description="Type: prosecution, defense, petitioner, respondent"
    )
    supporting_authorities: List[str] = Field(
        default_factory=list,
        description="Authorities cited in support"
    )
    counter_arguments: List[str] = Field(
        default_factory=list,
        description="Counter arguments made"
    )
    outcome: str = Field(
        description="Whether argument was accepted, rejected, or partially accepted"
    )


class LegalConcept(BaseModel):
    """
    Abstract legal concept entity.
    Represents conceptual legal frameworks and theories.
    """
    uuid: str = Field(description="Unique identifier")
    name: str = Field(description="Concept name")
    summary: str = Field(description="Description of the concept")
    domain: str = Field(description="Legal domain: criminal, civil, constitutional, etc.")
    cyber_law_application: str = Field(
        description="How this concept applies to cyber law"
    )
    related_concepts: List[str] = Field(
        default_factory=list,
        description="Related legal concepts"
    )
    practical_examples: List[str] = Field(
        default_factory=list,
        description="Practical examples of application"
    )


# Entity type definitions for Graphiti
LEGAL_ENTITY_TYPES = {
    'CaseLaw': CaseLaw,
    'Statute': Statute,
    'LegalPrinciple': LegalPrinciple,
    'LegalProcedure': LegalProcedure,
    'LegalAuthority': LegalAuthority,
    'CyberIncident': CyberIncident,
    'LegalArgument': LegalArgument,
    'LegalConcept': LegalConcept
}


def get_legal_entity_type_descriptions():
    """Get descriptions for legal entity types."""
    return {
        'CaseLaw': 'Court decisions, judgments, and case law relevant to cyber law',
        'Statute': 'Laws, acts, regulations, and statutory provisions',
        'LegalPrinciple': 'Established legal principles, doctrines, and jurisprudence',
        'LegalProcedure': 'Legal procedures, processes, and compliance requirements',
        'LegalAuthority': 'Judges, courts, regulatory bodies, and legal authorities',
        'CyberIncident': 'Cyber incidents referenced in legal contexts',
        'LegalArgument': 'Specific legal arguments made in cases',
        'LegalConcept': 'Abstract legal concepts and theoretical frameworks'
    }