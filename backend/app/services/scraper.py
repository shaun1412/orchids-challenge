from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from typing import Dict, Any
import asyncio
import base64

class WebsiteScraper:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()

    async def scrape(self, url: str) -> Dict[str, Any]:
        """Scrape a website and return its design context."""
        try:
            # Navigate to the page
            await self.page.goto(url, wait_until="networkidle")
            
            # Get the page content
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract CSS
            styles = []
            for style in soup.find_all('style'):
                styles.append(style.string)
            for link in soup.find_all('link', rel='stylesheet'):
                if link.get('href'):
                    styles.append(link['href'])
            
            # Take a screenshot
            screenshot = await self.page.screenshot(type='jpeg', quality=80)
            screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')
            
            # Extract meta information
            meta_info = {
                'title': soup.title.string if soup.title else '',
                'viewport': soup.find('meta', attrs={'name': 'viewport'}).get('content') if soup.find('meta', attrs={'name': 'viewport'}) else '',
                'description': soup.find('meta', attrs={'name': 'description'}).get('content') if soup.find('meta', attrs={'name': 'description'}) else '',
            }
            
            # Extract color scheme
            colors = []
            for style in styles:
                if isinstance(style, str):
                    # Simple color extraction (can be improved)
                    if 'color:' in style or 'background-color:' in style:
                        colors.extend(style.split(';'))
            
            # Create design context
            design_context = {
                'url': url,
                'html': content,
                'styles': styles,
                'screenshot': screenshot_base64,
                'meta': meta_info,
                'colors': list(set(colors)),
                'structure': self._extract_structure(soup)
            }
            
            return design_context
            
        except Exception as e:
            raise Exception(f"Error scraping website: {str(e)}")

    def _extract_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract the basic structure of the website."""
        structure = {
            'header': self._get_element_info(soup.find('header')),
            'main': self._get_element_info(soup.find('main')),
            'footer': self._get_element_info(soup.find('footer')),
            'navigation': self._get_element_info(soup.find('nav')),
        }
        return structure

    def _get_element_info(self, element) -> Dict[str, Any]:
        """Get basic information about an HTML element."""
        if not element:
            return None
        
        return {
            'tag': element.name,
            'classes': element.get('class', []),
            'id': element.get('id'),
            'children_count': len(element.find_all(recursive=False))
        } 