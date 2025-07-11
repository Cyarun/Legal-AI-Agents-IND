#!/usr/bin/env python3
"""
Test script for the Enhanced Legal Crawler.
This script tests the crawler with various Indian legal websites.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

from graphiti_core.utils.enhanced_legal_crawler import EnhancedLegalCrawler, get_supported_legal_sites


async def test_single_extraction():
    """Test single document extraction."""
    print("Testing single document extraction...")
    
    # Test URLs (these should be real URLs that work)
    test_urls = [
        "https://indiankanoon.org/doc/1766147/",  # Sample case
        "https://main.sci.gov.in/supremecourt/2023/9994/9994_2023_Order_21-Apr-2023.pdf",  # Sample SC case
    ]
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not set. Using mock extraction.")
        api_key = "mock_key"
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        
        async with EnhancedLegalCrawler("openai", api_key) as crawler:
            try:
                # Test the diagnostic function first
                diagnostic = await crawler.test_extraction(url)
                print(f"Diagnostic: {diagnostic}")
                
                # If supported, try full extraction
                if diagnostic.get("supported"):
                    print("URL is supported, attempting full extraction...")
                    document = await crawler.extract_legal_document(url)
                    print(f"Document extracted successfully:")
                    print(f"- Title: {document.metadata.title}")
                    print(f"- Type: {document.metadata.document_type}")
                    print(f"- Sections: {len(document.sections)}")
                    print(f"- Keywords: {document.metadata.keywords}")
                    print(f"- Cyber Law Relevance: {document.cyber_law_relevance}")
                else:
                    print("URL not supported by enhanced crawler")
                    
            except Exception as e:
                print(f"Error: {e}")


async def test_batch_extraction():
    """Test batch document extraction."""
    print("\nTesting batch document extraction...")
    
    # Multiple test URLs
    test_urls = [
        "https://indiankanoon.org/doc/1766147/",
        "https://indiankanoon.org/doc/6121622/",
        "https://main.sci.gov.in/supremecourt/2023/9994/9994_2023_Order_21-Apr-2023.pdf",
    ]
    
    api_key = os.getenv("OPENAI_API_KEY", "mock_key")
    
    async with EnhancedLegalCrawler("openai", api_key) as crawler:
        try:
            documents = await crawler.batch_extract_documents(test_urls)
            print(f"Batch extraction completed. {len(documents)} documents extracted.")
            
            for i, doc in enumerate(documents):
                print(f"\nDocument {i+1}:")
                print(f"- Title: {doc.metadata.title}")
                print(f"- Type: {doc.metadata.document_type}")
                print(f"- Jurisdiction: {doc.metadata.jurisdiction}")
                
        except Exception as e:
            print(f"Batch extraction error: {e}")


def test_supported_sites():
    """Test supported sites functionality."""
    print("\nTesting supported sites functionality...")
    
    sites = get_supported_legal_sites()
    print(f"Supported sites ({len(sites)}):")
    for domain, site_type in sites.items():
        print(f"- {domain}: {site_type}")
    
    # Test URL classification
    test_urls = [
        "https://indiankanoon.org/doc/123456/",
        "https://main.sci.gov.in/judgment/xyz",
        "https://example.com/not-supported",
        "https://sebi.gov.in/some-circular",
    ]
    
    crawler = EnhancedLegalCrawler()
    
    print("\nURL classification tests:")
    for url in test_urls:
        site_type = crawler._identify_site(url)
        supported = crawler.is_supported_url(url)
        print(f"- {url}")
        print(f"  Site type: {site_type}")
        print(f"  Supported: {supported}")


async def test_site_specific_extractors():
    """Test site-specific extraction methods."""
    print("\nTesting site-specific extractors...")
    
    # Mock HTML content for testing
    mock_html_content = {
        "indian_kanoon": """
        <html>
        <head><title>Test Case</title></head>
        <body>
        <h2 class="doc_title">Test vs. Example Ltd.</h2>
        <div class="docsource_main">Supreme Court of India</div>
        <div class="doc_date">2023-12-01</div>
        <div class="judgments">This is a test judgment content with information technology and cyber security implications.</div>
        <div class="doc_cite">2023 SCC Online SC 1234</div>
        </body>
        </html>
        """,
        "supreme_court": """
        <html>
        <head><title>SC Judgment</title></head>
        <body>
        <h1 class="case-title">ABC vs. XYZ</h1>
        <div class="bench-info">Hon'ble Justice A.K. Sharma</div>
        <span class="judgment-date">2023-11-15</span>
        <div class="judgment-content">Supreme Court judgment on digital privacy and data protection rights.</div>
        </body>
        </html>
        """
    }
    
    print("Site-specific extractor tests would require mocking web responses.")
    print("This is typically done with pytest and mock frameworks.")
    print("For now, we've implemented the extraction logic.")


async def main():
    """Run all tests."""
    print("Enhanced Legal Crawler Test Suite")
    print("=" * 50)
    
    # Test supported sites first (doesn't require network)
    test_supported_sites()
    
    # Test site-specific extractors
    await test_site_specific_extractors()
    
    # Test actual extraction (requires network and API key)
    if os.getenv("OPENAI_API_KEY") and os.getenv("TEST_NETWORK", "").lower() == "true":
        await test_single_extraction()
        await test_batch_extraction()
    else:
        print("\nSkipping network tests.")
        print("Set OPENAI_API_KEY and TEST_NETWORK=true to run network tests.")
    
    print("\nTest suite completed!")


if __name__ == "__main__":
    asyncio.run(main())