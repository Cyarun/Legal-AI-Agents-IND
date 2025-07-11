"""
Enhanced legal web crawler with support for multiple Indian legal websites.
Extends the base crawler with specialized extractors for each legal source.
"""

import asyncio
import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from bs4 import BeautifulSoup
import logging

from .web_crawler import WebCrawler, LegalDocument, LegalDocumentMetadata, LegalDocumentSection
from ..legal_analysis_prompts import LegalWebsiteSchema

logger = logging.getLogger(__name__)


class EnhancedLegalCrawler(WebCrawler):
    """Enhanced crawler with support for multiple Indian legal websites."""
    
    SUPPORTED_SITES = {
        "indiankanoon.org": "indian_kanoon",
        "main.sci.gov.in": "supreme_court", 
        "lobis.nic.in": "lok_sabha",
        "rajyasabha.nic.in": "rajya_sabha",
        "highcourtchd.gov.in": "high_court_chandigarh",
        "delhihighcourt.nic.in": "high_court_delhi",
        "bombayhighcourt.nic.in": "high_court_bombay",
        "egazette.gov.in": "gazette",
        "lawcommissionofindia.nic.in": "law_commission",
        "nclt.gov.in": "nclt",
        "nclat.nic.in": "nclat",
        "tdsat.gov.in": "tdsat",
        "consumeraffairs.nic.in/ncdrc": "ncdrc",
        "mca.gov.in": "mca",
        "sebi.gov.in": "sebi",
        "rbi.org.in": "rbi"
    }
    
    def __init__(self, llm_provider: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize enhanced crawler with site-specific configurations."""
        super().__init__(llm_provider, api_key)
        self.site_extractors = self._initialize_extractors()
        
    def _initialize_extractors(self) -> Dict[str, callable]:
        """Initialize site-specific extractors."""
        return {
            "indian_kanoon": self._extract_indian_kanoon,
            "supreme_court": self._extract_supreme_court,
            "high_court_chandigarh": self._extract_high_court,
            "high_court_delhi": self._extract_high_court,
            "high_court_bombay": self._extract_high_court,
            "lok_sabha": self._extract_parliament,
            "rajya_sabha": self._extract_parliament,
            "gazette": self._extract_gazette,
            "law_commission": self._extract_law_commission,
            "nclt": self._extract_tribunal,
            "nclat": self._extract_tribunal,
            "tdsat": self._extract_tribunal,
            "ncdrc": self._extract_consumer_forum,
            "mca": self._extract_regulatory,
            "sebi": self._extract_regulatory,
            "rbi": self._extract_regulatory
        }
    
    async def extract_legal_document(self, url: str) -> LegalDocument:
        """Extract legal document from any supported website."""
        # Identify the website
        site_type = self._identify_site(url)
        if not site_type:
            # Fall back to LLM extraction for unsupported sites
            return await self._llm_extract(url)
        
        # Use site-specific extractor
        extractor = self.site_extractors.get(site_type)
        if extractor:
            return await extractor(url)
        else:
            return await self._llm_extract(url)
    
    def _identify_site(self, url: str) -> Optional[str]:
        """Identify which legal website the URL belongs to."""
        for domain, site_type in self.SUPPORTED_SITES.items():
            if domain in url:
                return site_type
        return None
    
    async def _extract_indian_kanoon(self, url: str) -> LegalDocument:
        """Extract from Indian Kanoon."""
        async with self:
            result = await self.crawler.arun(url=url)
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Extract metadata
            title = soup.select_one('h2.doc_title')
            title_text = title.text.strip() if title else "Unknown Case"
            
            court = soup.select_one('div.docsource_main')
            court_text = court.text.strip() if court else "Unknown Court"
            
            date = soup.select_one('div.doc_date')
            date_text = date.text.strip() if date else None
            
            # Extract citation
            citation = soup.select_one('div.doc_cite')
            citation_text = citation.text.strip() if citation else None
            
            # Extract judges
            judges = soup.select_one('div.doc_author')
            judge_list = [judges.text.strip()] if judges else []
            
            # Extract content sections
            content = soup.select_one('div.judgments')
            sections = self._parse_judgment_sections(content) if content else []
            
            # Extract cited cases
            cited_cases = [a.text.strip() for a in soup.select('a.case_title')]
            
            # Identify cyber law relevance
            full_text = content.text if content else ""
            cyber_relevance = self._analyze_cyber_law_relevance(full_text)
            
            # Extract key holdings
            holdings = self._extract_key_holdings(sections)
            
            metadata = LegalDocumentMetadata(
                title=title_text,
                document_type="case_law",
                jurisdiction=self._determine_jurisdiction(court_text),
                case_number=self._extract_case_number(title_text),
                date=date_text,
                citation=citation_text,
                judge_names=judge_list,
                parties=self._extract_parties(title_text),
                keywords=self._extract_keywords(full_text)
            )
            
            return LegalDocument(
                metadata=metadata,
                sections=sections,
                summary=self._generate_summary(sections),
                cyber_law_relevance=cyber_relevance,
                key_holdings=holdings
            )
    
    async def _extract_supreme_court(self, url: str) -> LegalDocument:
        """Extract from Supreme Court of India website."""
        async with self:
            result = await self.crawler.arun(url=url)
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Supreme Court specific selectors
            title = soup.select_one('div.judgment-title, h1.case-title')
            bench = soup.select_one('div.bench-info, div.coram')
            date = soup.select_one('span.judgment-date, div.date-of-judgment')
            content = soup.select_one('div.judgment-text, div.judgment-content')
            
            # Process similar to Indian Kanoon
            sections = self._parse_judgment_sections(content) if content else []
            
            metadata = LegalDocumentMetadata(
                title=title.text.strip() if title else "SC Judgment",
                document_type="case_law",
                jurisdiction="supreme_court",
                date=date.text.strip() if date else None,
                judge_names=self._extract_bench_names(bench.text if bench else ""),
                keywords=["supreme court"] + self._extract_keywords(content.text if content else "")
            )
            
            return LegalDocument(
                metadata=metadata,
                sections=sections,
                summary=self._generate_summary(sections),
                cyber_law_relevance=self._analyze_cyber_law_relevance(content.text if content else ""),
                key_holdings=self._extract_key_holdings(sections)
            )
    
    async def _extract_high_court(self, url: str) -> LegalDocument:
        """Extract from High Court websites."""
        async with self:
            result = await self.crawler.arun(url=url)
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # High Court specific selectors (common patterns)
            title = soup.select_one('h1.case-title, h2.judgment-title, .case-name')
            bench = soup.select_one('.bench, .coram, .judges')
            date = soup.select_one('.date, .judgment-date, .decision-date')
            content = soup.select_one('.judgment-content, .full-text, .case-content')
            
            # Determine specific high court
            court_name = "High Court"
            if "chandigarh" in url:
                court_name = "High Court of Punjab & Haryana at Chandigarh"
            elif "delhi" in url:
                court_name = "High Court of Delhi"
            elif "bombay" in url:
                court_name = "High Court of Bombay"
            
            sections = self._parse_judgment_sections(content) if content else []
            
            metadata = LegalDocumentMetadata(
                title=title.text.strip() if title else f"{court_name} Judgment",
                document_type="case_law",
                jurisdiction="high_court",
                date=date.text.strip() if date else None,
                judge_names=self._extract_bench_names(bench.text if bench else ""),
                keywords=["high court"] + self._extract_keywords(content.text if content else "")
            )
            
            return LegalDocument(
                metadata=metadata,
                sections=sections,
                summary=self._generate_summary(sections),
                cyber_law_relevance=self._analyze_cyber_law_relevance(content.text if content else ""),
                key_holdings=self._extract_key_holdings(sections)
            )
    
    async def _extract_parliament(self, url: str) -> LegalDocument:
        """Extract from Lok Sabha/Rajya Sabha websites."""
        async with self:
            result = await self.crawler.arun(url=url)
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Parliamentary document specific extraction
            if "bill" in url.lower():
                return await self._extract_bill(soup, url)
            elif "act" in url.lower():
                return await self._extract_act(soup, url)
            else:
                return await self._extract_debate(soup, url)
    
    async def _extract_gazette(self, url: str) -> LegalDocument:
        """Extract from e-Gazette notifications."""
        async with self:
            result = await self.crawler.arun(url=url)
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Gazette notifications have specific structure
            metadata = LegalDocumentMetadata(
                title="Government Notification",
                document_type="regulation",
                jurisdiction="central_government",
                date=datetime.now().strftime("%Y-%m-%d"),
                keywords=["gazette", "notification", "government"]
            )
            
            sections = [
                LegalDocumentSection(
                    section_type="notification",
                    heading="Gazette Notification",
                    content=soup.get_text(),
                    legal_principles=[]
                )
            ]
            
            return LegalDocument(
                metadata=metadata,
                sections=sections,
                summary="Government gazette notification",
                cyber_law_relevance=self._analyze_cyber_law_relevance(soup.get_text()),
                key_holdings=[]
            )
    
    async def _extract_tribunal(self, url: str) -> LegalDocument:
        """Extract from NCLT/NCLAT/TDSAT websites."""
        async with self:
            result = await self.crawler.arun(url=url)
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Identify tribunal type
            tribunal_name = "Tribunal"
            if "nclt" in url:
                tribunal_name = "National Company Law Tribunal"
            elif "nclat" in url:
                tribunal_name = "National Company Law Appellate Tribunal"
            elif "tdsat" in url:
                tribunal_name = "Telecom Disputes Settlement & Appellate Tribunal"
            
            # Common tribunal selectors
            title = soup.select_one('h1, h2.case-title, .order-title')
            bench = soup.select_one('.bench, .members, .coram')
            date = soup.select_one('.date, .order-date, .judgment-date')
            content = soup.select_one('.order-content, .judgment-text, .full-text')
            
            sections = self._parse_judgment_sections(content) if content else []
            
            metadata = LegalDocumentMetadata(
                title=title.text.strip() if title else f"{tribunal_name} Order",
                document_type="tribunal_order",
                jurisdiction="tribunal",
                date=date.text.strip() if date else None,
                judge_names=self._extract_bench_names(bench.text if bench else ""),
                keywords=[tribunal_name.lower(), "tribunal", "order"] + self._extract_keywords(content.text if content else "")
            )
            
            return LegalDocument(
                metadata=metadata,
                sections=sections,
                summary=self._generate_summary(sections),
                cyber_law_relevance=self._analyze_cyber_law_relevance(content.text if content else ""),
                key_holdings=self._extract_key_holdings(sections)
            )
    
    async def _extract_regulatory(self, url: str) -> LegalDocument:
        """Extract from regulatory body websites (SEBI/RBI/MCA)."""
        async with self:
            result = await self.crawler.arun(url=url)
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Identify document type
            doc_type = "regulation"
            if "circular" in url.lower():
                doc_type = "circular"
            elif "notification" in url.lower():
                doc_type = "notification"
            elif "guideline" in url.lower():
                doc_type = "guideline"
            
            # Extract title and content
            title = soup.find(['h1', 'h2', 'h3'])
            title_text = title.text.strip() if title else "Regulatory Document"
            
            # Regulatory body
            if "sebi.gov.in" in url:
                regulator = "SEBI"
            elif "rbi.org.in" in url:
                regulator = "RBI"
            elif "mca.gov.in" in url:
                regulator = "MCA"
            else:
                regulator = "Unknown"
            
            metadata = LegalDocumentMetadata(
                title=title_text,
                document_type=doc_type,
                jurisdiction=f"{regulator.lower()}_regulatory",
                date=self._extract_date_from_text(soup.get_text()),
                keywords=[regulator.lower(), doc_type, "regulatory"]
            )
            
            sections = self._parse_regulatory_sections(soup)
            
            return LegalDocument(
                metadata=metadata,
                sections=sections,
                summary=f"{regulator} {doc_type}: {title_text}",
                cyber_law_relevance=self._analyze_cyber_law_relevance(soup.get_text()),
                key_holdings=self._extract_regulatory_requirements(sections)
            )
    
    def _parse_judgment_sections(self, content) -> List[LegalDocumentSection]:
        """Parse judgment into structured sections."""
        if not content:
            return []
        
        sections = []
        text = content.get_text()
        
        # Common section patterns in judgments
        section_patterns = {
            "facts": r"(?i)(facts|background|factual background)",
            "issues": r"(?i)(issues|questions|points for determination)",
            "arguments": r"(?i)(arguments|submissions|contentions)",
            "judgment": r"(?i)(judgment|decision|order|findings)",
            "precedents": r"(?i)(precedents|authorities|cases cited)"
        }
        
        # Extract sections based on patterns
        for section_type, pattern in section_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                start = match.start()
                # Find next section or end of text
                end = len(text)
                for other_pattern in section_patterns.values():
                    next_match = re.search(other_pattern, text[start+100:])
                    if next_match:
                        end = min(end, start + 100 + next_match.start())
                
                section_content = text[start:end].strip()
                if len(section_content) > 100:  # Meaningful content
                    sections.append(LegalDocumentSection(
                        section_type=section_type,
                        heading=match.group(),
                        content=section_content[:2000],  # Limit length
                        legal_principles=self._extract_principles(section_content),
                        cited_cases=self._extract_case_citations(section_content)
                    ))
        
        # If no sections found, create a general section
        if not sections:
            sections.append(LegalDocumentSection(
                section_type="general",
                heading="Full Text",
                content=text[:2000],
                legal_principles=[],
                cited_cases=[]
            ))
        
        return sections
    
    def _analyze_cyber_law_relevance(self, text: str) -> str:
        """Analyze relevance to cyber law."""
        cyber_keywords = [
            "information technology", "cyber", "digital", "electronic",
            "data protection", "privacy", "internet", "online",
            "computer", "software", "intermediary", "encryption",
            "cyber crime", "hacking", "phishing", "identity theft",
            "electronic evidence", "digital signature", "e-commerce",
            "social media", "blockchain", "artificial intelligence",
            "machine learning", "cloud computing", "iot"
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in cyber_keywords if kw in text_lower]
        
        if not found_keywords:
            return "No direct cyber law relevance identified"
        
        relevance = f"Relevant to cyber law - Keywords found: {', '.join(found_keywords[:5])}"
        
        # Check for specific acts
        if "information technology act" in text_lower or "it act" in text_lower:
            relevance += ". Discusses IT Act provisions."
        if "data protection" in text_lower:
            relevance += ". Relates to data protection laws."
        if "cyber crime" in text_lower:
            relevance += ". Involves cyber crime aspects."
        
        return relevance
    
    def _extract_key_holdings(self, sections: List[LegalDocumentSection]) -> List[str]:
        """Extract key legal holdings from judgment sections."""
        holdings = []
        
        for section in sections:
            if section.section_type in ["judgment", "decision", "findings"]:
                # Look for holding patterns
                patterns = [
                    r"(?i)held that[^.]+\.",
                    r"(?i)court holds[^.]+\.",
                    r"(?i)we hold[^.]+\.",
                    r"(?i)it is held[^.]+\.",
                    r"(?i)decided that[^.]+\.",
                    r"(?i)court finds[^.]+\."
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, section.content)
                    holdings.extend(matches)
        
        # Clean and deduplicate
        holdings = list(set([h.strip() for h in holdings]))[:5]
        
        return holdings
    
    def _extract_principles(self, text: str) -> List[str]:
        """Extract legal principles from text."""
        principles = []
        
        # Common principle patterns
        patterns = [
            r"(?i)principle of[^.]+\.",
            r"(?i)doctrine of[^.]+\.",
            r"(?i)rule of[^.]+\.",
            r"(?i)test of[^.]+\."
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            principles.extend([m.strip() for m in matches])
        
        return list(set(principles))[:3]
    
    def _extract_case_citations(self, text: str) -> List[str]:
        """Extract case citations from text."""
        # Common citation patterns
        patterns = [
            r"\d{4}\s+\(\d+\)\s+\w+\s+\d+",  # 2024 (5) SCC 123
            r"\d{4}\s+\w+\s+\d+",  # 2024 SCC 123
            r"AIR\s+\d{4}\s+\w+\s+\d+",  # AIR 2024 SC 123
            r"\[\d{4}\]\s+\d+\s+\w+\s+\d+"  # [2024] 5 SCC 123
        ]
        
        citations = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            citations.extend(matches)
        
        return list(set(citations))[:10]
    
    def _determine_jurisdiction(self, court_text: str) -> str:
        """Determine jurisdiction from court name."""
        court_lower = court_text.lower()
        
        if "supreme court" in court_lower:
            return "supreme_court"
        elif "high court" in court_lower:
            for state in ["delhi", "bombay", "madras", "calcutta", "karnataka", "kerala"]:
                if state in court_lower:
                    return f"high_court_{state}"
            return "high_court"
        elif "tribunal" in court_lower:
            return "tribunal"
        elif "commission" in court_lower:
            return "commission"
        else:
            return "other"
    
    def _extract_case_number(self, title: str) -> Optional[str]:
        """Extract case number from title."""
        # Common case number patterns
        patterns = [
            r"No\.\s*\d+\s*of\s*\d{4}",
            r"Case No\.\s*\d+/\d{4}",
            r"\d+/\d{4}",
            r"[A-Z]+\s+No\.\s*\d+"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                return match.group()
        
        return None
    
    def _extract_parties(self, title: str) -> List[str]:
        """Extract parties from case title."""
        # Common patterns: "A vs B", "A v. B"
        patterns = [
            r"(.+?)\s+v(?:s)?\.?\s+(.+)",
            r"(.+?)\s+versus\s+(.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return [match.group(1).strip(), match.group(2).strip()]
        
        return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        # Cyber law specific keywords
        keywords = []
        cyber_terms = [
            "cyber", "digital", "electronic", "internet", "online",
            "data", "privacy", "security", "information technology"
        ]
        
        text_lower = text.lower()
        for term in cyber_terms:
            if term in text_lower:
                keywords.append(term)
        
        return keywords[:10]
    
    def _generate_summary(self, sections: List[LegalDocumentSection]) -> str:
        """Generate summary from sections."""
        if not sections:
            return "No summary available"
        
        # Find judgment section
        for section in sections:
            if section.section_type in ["judgment", "decision"]:
                # Return first 200 characters
                return section.content[:200] + "..."
        
        # Fallback to first section
        return sections[0].content[:200] + "..."
    
    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """Extract date from text."""
        # Common date patterns
        patterns = [
            r"\d{1,2}[/-]\d{1,2}[/-]\d{4}",
            r"\d{1,2}\s+\w+\s+\d{4}",
            r"\w+\s+\d{1,2},\s+\d{4}"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        
        return None
    
    def _extract_bench_names(self, bench_text: str) -> List[str]:
        """Extract judge names from bench information."""
        # Common patterns for judge names
        judges = []
        
        # Remove common prefixes
        bench_text = re.sub(r"(?i)(coram|bench|before):\s*", "", bench_text)
        
        # Split by common separators
        parts = re.split(r"[,&]|and", bench_text)
        
        for part in parts:
            part = part.strip()
            if part and len(part) > 3:
                # Remove honorifics
                part = re.sub(r"(?i)(hon'ble|justice|judge|mr\.|mrs\.|dr\.)\s*", "", part)
                if part:
                    judges.append(part.strip())
        
        return judges
    
    def _parse_regulatory_sections(self, soup) -> List[LegalDocumentSection]:
        """Parse regulatory document into sections."""
        sections = []
        
        # Look for numbered sections
        for element in soup.find_all(['h2', 'h3', 'h4', 'p']):
            text = element.get_text().strip()
            
            # Check if it's a section heading
            if re.match(r"^\d+\.?\s+", text) or re.match(r"^[A-Z]\.\s+", text):
                # Get content until next section
                content = []
                for sibling in element.find_next_siblings():
                    if sibling.name in ['h2', 'h3', 'h4']:
                        sibling_text = sibling.get_text().strip()
                        if re.match(r"^\d+\.?\s+", sibling_text) or re.match(r"^[A-Z]\.\s+", sibling_text):
                            break
                    content.append(sibling.get_text().strip())
                
                if content:
                    sections.append(LegalDocumentSection(
                        section_type="regulation",
                        heading=text,
                        content=" ".join(content)[:2000],
                        legal_principles=[]
                    ))
        
        return sections
    
    def _extract_regulatory_requirements(self, sections: List[LegalDocumentSection]) -> List[str]:
        """Extract regulatory requirements."""
        requirements = []
        
        for section in sections:
            # Look for requirement patterns
            patterns = [
                r"(?i)shall[^.]+\.",
                r"(?i)must[^.]+\.",
                r"(?i)required to[^.]+\.",
                r"(?i)obligated to[^.]+\."
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, section.content)
                requirements.extend(matches)
        
        return list(set([r.strip() for r in requirements]))[:10]
    
    async def _extract_bill(self, soup, url: str) -> LegalDocument:
        """Extract bill information."""
        metadata = LegalDocumentMetadata(
            title=soup.find('h1').text if soup.find('h1') else "Bill",
            document_type="bill",
            jurisdiction="parliament",
            date=self._extract_date_from_text(soup.get_text()),
            keywords=["bill", "legislation", "parliament"]
        )
        
        sections = self._parse_bill_sections(soup)
        
        return LegalDocument(
            metadata=metadata,
            sections=sections,
            summary="Parliamentary Bill",
            cyber_law_relevance=self._analyze_cyber_law_relevance(soup.get_text()),
            key_holdings=[]
        )
    
    async def _extract_act(self, soup, url: str) -> LegalDocument:
        """Extract act information."""
        metadata = LegalDocumentMetadata(
            title=soup.find('h1').text if soup.find('h1') else "Act",
            document_type="statute",
            jurisdiction="parliament",
            date=self._extract_date_from_text(soup.get_text()),
            keywords=["act", "statute", "legislation"]
        )
        
        sections = self._parse_act_sections(soup)
        
        return LegalDocument(
            metadata=metadata,
            sections=sections,
            summary="Parliamentary Act",
            cyber_law_relevance=self._analyze_cyber_law_relevance(soup.get_text()),
            key_holdings=[]
        )
    
    async def _extract_debate(self, soup, url: str) -> LegalDocument:
        """Extract parliamentary debate."""
        metadata = LegalDocumentMetadata(
            title="Parliamentary Debate",
            document_type="debate",
            jurisdiction="parliament",
            date=self._extract_date_from_text(soup.get_text()),
            keywords=["debate", "parliament", "discussion"]
        )
        
        sections = [
            LegalDocumentSection(
                section_type="debate",
                heading="Parliamentary Debate",
                content=soup.get_text()[:2000],
                legal_principles=[]
            )
        ]
        
        return LegalDocument(
            metadata=metadata,
            sections=sections,
            summary="Parliamentary debate transcript",
            cyber_law_relevance=self._analyze_cyber_law_relevance(soup.get_text()),
            key_holdings=[]
        )
    
    def _parse_bill_sections(self, soup) -> List[LegalDocumentSection]:
        """Parse bill into sections."""
        # Implementation would parse bill structure
        return self._parse_regulatory_sections(soup)
    
    def _parse_act_sections(self, soup) -> List[LegalDocumentSection]:
        """Parse act into sections."""
        # Implementation would parse act structure
        return self._parse_regulatory_sections(soup)
    
    async def _extract_law_commission(self, url: str) -> LegalDocument:
        """Extract from Law Commission reports."""
        async with self:
            result = await self.crawler.arun(url=url)
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Law Commission specific extraction
            title = soup.select_one('h1, h2, .report-title')
            report_number = soup.select_one('.report-number, .report-no')
            date = soup.select_one('.date, .published-date')
            content = soup.select_one('.report-content, .full-text, .content')
            
            # Extract report number from title or dedicated field
            report_num = ""
            if report_number:
                report_num = report_number.text.strip()
            elif title and "report" in title.text.lower():
                import re
                match = re.search(r'report\s+no\.?\s*(\d+)', title.text, re.IGNORECASE)
                if match:
                    report_num = f"Report No. {match.group(1)}"
            
            sections = self._parse_regulatory_sections(soup)
            
            metadata = LegalDocumentMetadata(
                title=title.text.strip() if title else "Law Commission Report",
                document_type="report",
                jurisdiction="law_commission",
                date=date.text.strip() if date else None,
                case_number=report_num,
                keywords=["law commission", "report", "reform"] + self._extract_keywords(content.text if content else "")
            )
            
            return LegalDocument(
                metadata=metadata,
                sections=sections,
                summary=f"Law Commission {report_num}: {title.text[:100] if title else 'Report'}...",
                cyber_law_relevance=self._analyze_cyber_law_relevance(content.text if content else ""),
                key_holdings=self._extract_regulatory_requirements(sections)
            )
    
    async def _extract_consumer_forum(self, url: str) -> LegalDocument:
        """Extract from consumer forum decisions."""
        async with self:
            result = await self.crawler.arun(url=url)
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Consumer forum specific extraction
            title = soup.select_one('h1, h2, .case-title, .order-title')
            case_number = soup.select_one('.case-number, .case-no')
            date = soup.select_one('.date, .order-date, .judgment-date')
            content = soup.select_one('.order-content, .judgment-text, .full-text')
            
            # Extract parties (consumer vs service provider)
            parties = []
            if title:
                parties = self._extract_parties(title.text)
            
            sections = self._parse_judgment_sections(content) if content else []
            
            metadata = LegalDocumentMetadata(
                title=title.text.strip() if title else "Consumer Forum Order",
                document_type="consumer_order",
                jurisdiction="consumer_forum",
                case_number=case_number.text.strip() if case_number else None,
                date=date.text.strip() if date else None,
                parties=parties,
                keywords=["consumer", "forum", "redressal"] + self._extract_keywords(content.text if content else "")
            )
            
            return LegalDocument(
                metadata=metadata,
                sections=sections,
                summary=self._generate_summary(sections),
                cyber_law_relevance=self._analyze_cyber_law_relevance(content.text if content else ""),
                key_holdings=self._extract_key_holdings(sections)
            )
    
    async def _llm_extract(self, url: str) -> LegalDocument:
        """Fallback to LLM extraction for unsupported sites."""
        strategy = self._create_legal_extraction_strategy()
        
        async with self:
            result = await self.crawler.arun(
                url=url,
                extraction_strategy=strategy
            )
            
            # Parse the extracted data
            if result.extracted_content:
                return LegalDocument(**result.extracted_content)
            else:
                # Create minimal document
                return LegalDocument(
                    metadata=LegalDocumentMetadata(
                        title="Unknown Document",
                        document_type="unknown",
                        jurisdiction="unknown",
                        keywords=[]
                    ),
                    sections=[],
                    summary="Unable to extract document",
                    cyber_law_relevance="Unknown",
                    key_holdings=[]
                )
    
    async def batch_extract_documents(self, urls: List[str]) -> List[LegalDocument]:
        """Extract multiple legal documents concurrently."""
        tasks = [self.extract_legal_document(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        documents = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error extracting document: {result}")
                continue
            documents.append(result)
        
        return documents
    
    def get_supported_domains(self) -> List[str]:
        """Get list of supported legal website domains."""
        return list(self.SUPPORTED_SITES.keys())
    
    def is_supported_url(self, url: str) -> bool:
        """Check if a URL is from a supported legal website."""
        return any(domain in url for domain in self.SUPPORTED_SITES.keys())
    
    async def test_extraction(self, url: str) -> Dict[str, Any]:
        """Test extraction on a URL and return diagnostic information."""
        try:
            start_time = asyncio.get_event_loop().time()
            document = await self.extract_legal_document(url)
            end_time = asyncio.get_event_loop().time()
            
            return {
                "status": "success",
                "url": url,
                "extraction_time": end_time - start_time,
                "document_type": document.metadata.document_type,
                "title": document.metadata.title,
                "sections_count": len(document.sections),
                "cyber_law_relevance": document.cyber_law_relevance,
                "keywords": document.metadata.keywords,
                "site_type": self._identify_site(url),
                "supported": self.is_supported_url(url)
            }
        except Exception as e:
            return {
                "status": "error",
                "url": url,
                "error": str(e),
                "site_type": self._identify_site(url),
                "supported": self.is_supported_url(url)
            }


# Convenience functions for easy usage
async def extract_legal_document(url: str, llm_provider: str = "openai", api_key: str = None) -> LegalDocument:
    """Convenience function to extract a single legal document."""
    async with EnhancedLegalCrawler(llm_provider, api_key) as crawler:
        return await crawler.extract_legal_document(url)


async def batch_extract_legal_documents(urls: List[str], llm_provider: str = "openai", api_key: str = None) -> List[LegalDocument]:
    """Convenience function to extract multiple legal documents."""
    async with EnhancedLegalCrawler(llm_provider, api_key) as crawler:
        return await crawler.batch_extract_documents(urls)


def get_supported_legal_sites() -> Dict[str, str]:
    """Get mapping of supported legal websites."""
    return EnhancedLegalCrawler.SUPPORTED_SITES.copy()