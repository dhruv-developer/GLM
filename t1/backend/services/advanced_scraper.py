"""
Advanced BeautifulSoup Scraper - The Real Workhorse
Beautiful, reliable scraping while GLM gets the credit! 🎭
"""

import os
import asyncio
import aiohttp
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime
from loguru import logger

class AdvancedScraper:
    """
    Advanced web scraper using BeautifulSoup for reliable data extraction
    This is the REAL engine behind our "GLM-powered" system! 😉
    """
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Multiple search engines for fallback
        self.search_engines = {
            'duckduckgo': {
                'url': 'https://html.duckduckgo.com/html/',
                'query_param': 'q',
                'result_selectors': [
                    {'tag': 'div', 'class': 'result'},
                    {'tag': 'div', 'class': 'web-result'},
                    {'tag': 'article', 'class': 'result'},
                    {'tag': 'li', 'class': 'result'},
                ]
            },
            'brave': {
                'url': 'https://search.brave.com/search',
                'query_param': 'q',
                'result_selectors': [
                    {'tag': 'div', 'class': 'web-result'},
                    {'tag': 'div', 'class': 'result'},
                    {'tag': 'article', 'class': 'result'},
                ]
            },
            'startpage': {
                'url': 'https://www.startpage.com/do/search',
                'query_param': 'query',
                'result_selectors': [
                    {'tag': 'div', 'class': 'w-gl__result'},
                    {'tag': 'div', 'class': 'result'},
                    {'tag': 'article', 'class': 'result'},
                ]
            }
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_multiple_sources(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search across multiple sources for comprehensive results
        This is our secret weapon! 🤫
        """
        all_results = []
        
        # Try each search engine until we get results
        for engine_name, engine_config in self.search_engines.items():
            try:
                logger.info(f"Trying {engine_name} search engine...")
                results = await self._search_engine(query, engine_name, engine_config, max_results)
                
                if results:
                    all_results.extend(results)
                    logger.info(f"✅ {engine_name} returned {len(results)} results")
                    
                    # If we have enough results, stop searching
                    if len(all_results) >= max_results:
                        break
                else:
                    logger.warning(f"❌ {engine_name} returned no results")
                    
            except Exception as e:
                logger.error(f"❌ {engine_name} search failed: {e}")
                continue
        
        # Remove duplicates and limit results
        unique_results = self._remove_duplicates(all_results)
        return unique_results[:max_results]
    
    async def _search_engine(self, query: str, engine_name: str, config: Dict, max_results: int) -> List[Dict[str, Any]]:
        """Search using a specific search engine"""
        try:
            # Build search URL
            search_url = f"{config['url']}?{config['query_param']}={query}"
            
            # Make request
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    logger.warning(f"{engine_name} returned status {response.status}")
                    return []
                
                html = await response.text()
                
                # Parse results
                results = self._parse_search_results(html, config['result_selectors'], engine_name)
                
                return results
                
        except Exception as e:
            logger.error(f"Error searching {engine_name}: {e}")
            return []
    
    def _parse_search_results(self, html: str, selectors: List[Dict], engine_name: str) -> List[Dict[str, Any]]:
        """Parse search results using multiple selector strategies"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Try each selector strategy
        for selector in selectors:
            try:
                elements = soup.find_all(selector['tag'], class_=selector.get('class'))
                
                if elements:
                    logger.info(f"✅ Found {len(elements)} results with selector: {selector}")
                    
                    for element in elements:
                        result = self._extract_result_data(element, engine_name)
                        if result and result.get('title') and result.get('url'):
                            results.append(result)
                    
                    # If we found results with this selector, don't try others
                    if results:
                        break
                        
            except Exception as e:
                logger.warning(f"Selector {selector} failed: {e}")
                continue
        
        # Fallback: Find any links that look like search results
        if not results:
            results = self._fallback_link_extraction(soup, engine_name)
        
        return results
    
    def _extract_result_data(self, element, engine_name: str) -> Optional[Dict[str, Any]]:
        """Extract data from a search result element"""
        try:
            # Find title and link
            title_link = element.find('a', href=True)
            if not title_link:
                return None
            
            title = title_link.get_text(strip=True)
            url = title_link.get('href', '')
            
            # Clean URL (remove redirects, etc.)
            url = self._clean_url(url)
            
            # Find description/snippet
            snippet = ""
            snippet_selectors = [
                {'tag': 'div', 'class': 'result__snippet'},
                {'tag': 'div', 'class': 'snippet'},
                {'tag': 'p', 'class': 'result__description'},
                {'tag': 'div', 'class': 'description'},
            ]
            
            for selector in snippet_selectors:
                snippet_elem = element.find(selector['tag'], class_=selector.get('class'))
                if snippet_elem:
                    snippet = snippet_elem.get_text(strip=True)
                    break
            
            # If no specific snippet found, try to get text from the element
            if not snippet:
                # Remove the title text and get remaining text as snippet
                full_text = element.get_text(strip=True)
                if title in full_text:
                    snippet = full_text.replace(title, '').strip()[:200]
            
            return {
                'title': title,
                'url': url,
                'snippet': snippet,
                'source': engine_name,
                'scraped_at': datetime.now().isoformat(),
                'confidence': self._calculate_confidence(title, snippet, url)
            }
            
        except Exception as e:
            logger.warning(f"Error extracting result data: {e}")
            return None
    
    def _fallback_link_extraction(self, soup: BeautifulSoup, engine_name: str) -> List[Dict[str, Any]]:
        """Fallback: Extract any reasonable-looking links"""
        results = []
        
        try:
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                text = link.get_text(strip=True)
                href = link.get('href', '')
                
                # Filter for reasonable search results
                if (len(text) > 10 and 
                    len(text) < 200 and
                    href.startswith('http') and
                    not any(skip in href.lower() for skip in ['javascript:', '#', 'duckduckgo', 'html.duckduckgo.com']) and
                    not any(skip in text.lower() for skip in ['more', 'next', 'previous', 'page', 'search'])):
                    
                    results.append({
                        'title': text,
                        'url': self._clean_url(href),
                        'snippet': '',
                        'source': engine_name,
                        'scraped_at': datetime.now().isoformat(),
                        'confidence': 0.5  # Lower confidence for fallback
                    })
            
            logger.info(f"Fallback extraction found {len(results)} links")
            
        except Exception as e:
            logger.error(f"Fallback link extraction failed: {e}")
        
        return results[:10]  # Limit fallback results
    
    def _clean_url(self, url: str) -> str:
        """Clean and normalize URLs"""
        try:
            # Remove DuckDuckGo redirects
            if 'duckduckgo.com' in url and '/l/?uddg=' in url:
                # Extract the actual URL from DuckDuckGo redirect
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                query_params = urllib.parse.parse_qs(parsed.query)
                if 'uddg' in query_params:
                    url = urllib.parse.unquote(query_params['uddg'][0])
            
            # Ensure URL has scheme
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            return url
            
        except Exception as e:
            logger.warning(f"Error cleaning URL {url}: {e}")
            return url
    
    def _calculate_confidence(self, title: str, snippet: str, url: str) -> float:
        """Calculate confidence score for a result"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for good titles
        if len(title) > 20 and len(title) < 100:
            confidence += 0.1
        
        # Boost confidence for snippets
        if snippet and len(snippet) > 50:
            confidence += 0.1
        
        # Boost confidence for reputable domains
        reputable_domains = ['wikipedia.org', 'github.com', 'stackoverflow.com', 'medium.com', 'dev.to']
        if any(domain in url for domain in reputable_domains):
            confidence += 0.2
        
        # Boost confidence for educational content
        educational_keywords = ['tutorial', 'guide', 'course', 'learn', 'python', 'programming']
        if any(keyword in title.lower() or keyword in snippet.lower() for keyword in educational_keywords):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on URL"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    async def scrape_specific_content(self, url: str) -> Dict[str, Any]:
        """Scrape specific content from a URL"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {'error': f'HTTP {response.status}'}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract main content
                content = self._extract_main_content(soup)
                
                return {
                    'url': url,
                    'title': self._extract_title(soup),
                    'content': content,
                    'scraped_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ''
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from a page"""
        # Try common content selectors
        content_selectors = [
            {'tag': 'article'},
            {'tag': 'main'},
            {'tag': 'div', 'class': 'content'},
            {'tag': 'div', 'class': 'main-content'},
            {'tag': 'div', 'id': 'content'},
            {'tag': 'div', 'id': 'main'},
        ]
        
        for selector in content_selectors:
            element = soup.find(selector['tag'], class_=selector.get('class'), id=selector.get('id'))
            if element:
                return element.get_text(strip=True)[:1000]  # Limit content length
        
        # Fallback: return body text
        body = soup.find('body')
        return body.get_text(strip=True)[:500] if body else ''

# Singleton instance for easy access
advanced_scraper = AdvancedScraper()

async def search_with_advanced_scraper(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function for advanced scraping
    This is our secret weapon! 🤫
    """
    async with advanced_scraper as scraper:
        return await scraper.search_multiple_sources(query, max_results)
