#!/usr/bin/env python3
"""
Debug script to test web search issues
"""

import requests
import asyncio
from bs4 import BeautifulSoup

def test_duckduckgo_parsing():
    """Test DuckDuckGo HTML parsing directly"""
    
    print("🧪 Testing DuckDuckGo Parsing")
    print("=" * 40)
    
    # Test the same query that's failing
    query = "Find all the job openings of SDE Intern at Big Tech Companies"
    search_url = f"https://html.duckduckgo.com/html/?q={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"\n🔍 Testing search for: {query}")
        print(f"🌐 URL: {search_url}")
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Got response: {response.status_code}")
            print(f"📄 Content length: {len(response.text)} characters")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Debug: Find all divs with 'result' in class
            result_divs = soup.find_all('div', class_=lambda x: 'result' in str(x.get('class', [])))
            print(f"🔍 Found {len(result_divs)} result divs")
            
            # Show first few results
            for i, div in enumerate(result_divs[:5]):
                print(f"\n--- Result {i+1} ---")
                print(f"Classes: {div.get('class', [])}")
                
                # Try different selectors
                title_elem = div.find('a', class_='result__url')
                if not title_elem:
                    title_elem = div.find('a', class_='result__a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    print(f"Title: {title}")
                    print(f"URL: {url}")
                else:
                    print("❌ No title found")
                    
                # Try finding any link
                links = div.find_all('a')
                print(f"Links found: {len(links)}")
                for j, link in enumerate(links[:3]):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if href and text:
                        print(f"  Link {j+1}: {text} -> {href}")
                        
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 40)

def test_simple_search():
    """Test with a simpler query"""
    
    print("\n🧪 Testing Simple Query")
    print("=" * 40)
    
    # Try a simple query
    simple_query = "python programming"
    search_url = f"https://html.duckduckgo.com/html/?q={simple_query}"
    
    try:
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for any result-like content
            all_links = soup.find_all('a', href=True)
            print(f"🔗 Found {len(all_links)} links total")
            
            # Show first few
            for i, link in enumerate(all_links[:5]):
                text = link.get_text(strip=True)
                href = link.get('href', '')
                if text and href and not href.startswith('#'):
                    print(f"  {i+1}. {text} -> {href}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_duckduckgo_parsing()
    test_simple_search()
