import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, Any, List, Optional, Tuple
import re
import cssutils
from urllib.parse import urljoin, urlparse
import logging
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
from PIL import Image
import io

# Suppress cssutils warnings
cssutils.log.setLevel(logging.ERROR)

@dataclass
class ScrapingConfig:
    """Configuration for website scraping."""
    include_screenshots: bool = True
    extract_computed_styles: bool = True
    extract_fonts: bool = True
    extract_animations: bool = True
    extract_responsive_data: bool = True
    extract_interactions: bool = True
    max_css_file_size: int = 1024 * 1024  # 1MB
    screenshot_width: int = 1920
    screenshot_height: int = 1080
    mobile_width: int = 375
    mobile_height: int = 667
    tablet_width: int = 768
    tablet_height: int = 1024

class AdvancedWebsiteScraper:
    def __init__(self, config: Optional[ScrapingConfig] = None):
        """Initialize the advanced website scraper."""
        self.config = config or ScrapingConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
        
    def scrape_comprehensive(self, url: str) -> Dict[str, Any]:
        """Scrape a website comprehensively for pixel-perfect cloning."""
        try:
            print(f"Starting comprehensive scrape of {url}")
            
            # Initialize Selenium driver for dynamic content
            self._setup_selenium()
            
            # Step 1: Basic HTML scraping with BeautifulSoup
            html_data = self._scrape_basic_html(url)
            
            # Step 2: Extract computed styles using Selenium
            computed_styles = self._extract_computed_styles(url) if self.config.extract_computed_styles else {}
            
            # Step 3: Extract precise measurements
            measurements = self._extract_measurements(url)
            
            # Step 4: Extract typography information
            typography = self._extract_typography(url) if self.config.extract_fonts else {}
            
            # Step 5: Extract color palette
            colors = self._extract_comprehensive_colors(html_data['styles'], computed_styles)
            
            # Step 6: Extract layout structure with positioning
            layout_structure = self._extract_layout_structure(url)
            
            # Step 7: Extract responsive breakpoints
            responsive_data = self._extract_responsive_data(url) if self.config.extract_responsive_data else {}
            
            # Step 8: Extract animations and transitions
            animations = self._extract_animations(html_data['styles']) if self.config.extract_animations else {}
            
            # Step 9: Extract interactive elements
            interactions = self._extract_interactions(url) if self.config.extract_interactions else {}
            
            # Step 10: Extract assets (images, icons, etc.)
            assets = self._extract_assets(url, html_data['soup'])
            
            # Step 11: Take screenshots
            screenshots = self._take_screenshots(url) if self.config.include_screenshots else {}
            
            # Combine all data
            comprehensive_context = {
                **html_data,
                'computed_styles': computed_styles,
                'measurements': measurements,
                'typography': typography,
                'colors': colors,
                'layout_structure': layout_structure,
                'responsive_breakpoints': responsive_data,
                'animations': animations,
                'interactions': interactions,
                'assets': assets,
                'screenshots': screenshots,
                'extraction_timestamp': time.time(),
                'scraper_version': '2.0'
            }
            
            return comprehensive_context
            
        except Exception as e:
            raise Exception(f"Error in comprehensive scraping: {str(e)}")
        finally:
            self._cleanup_selenium()
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver."""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'--window-size={self.config.screenshot_width},{self.config.screenshot_height}')
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                print(f"Warning: Could not initialize Chrome driver: {e}")
                print("Some features requiring JavaScript execution will be unavailable")
    
    def _cleanup_selenium(self):
        """Cleanup Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def _scrape_basic_html(self, url: str) -> Dict[str, Any]:
        """Enhanced basic HTML scraping."""
        response = self.session.get(url)
        response.raise_for_status()
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        
        # Convert relative image URLs to absolute URLs
        for img_tag in soup.find_all('img'):
            src = img_tag.get('src')
            if src:
                img_tag['src'] = urljoin(url, src)
        
        # Extract all CSS (inline, internal, and external)
        styles = self._extract_all_css(url, soup)
        
        # Extract comprehensive meta information
        meta_info = self._extract_comprehensive_meta(soup)
        
        # Extract detailed structure
        structure = self._extract_detailed_structure(soup)
        
        return {
            'url': url,
            'html': content,
            'soup': soup,  # Keep for further processing
            'styles': styles,
            'meta': meta_info,
            'structure': structure,
            'elements': self._extract_all_elements(soup)
        }
    
    def _extract_all_css(self, base_url: str, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract all CSS from the page including external stylesheets."""
        styles = {
            'inline': [],
            'internal': [],
            'external': {}
        }
        
        # Internal CSS
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                styles['internal'].append(style_tag.string)
        
        # External CSS
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                try:
                    css_url = urljoin(base_url, href)
                    css_response = self.session.get(css_url)
                    if css_response.status_code == 200 and len(css_response.content) < self.config.max_css_file_size:
                        styles['external'][css_url] = css_response.text
                    else:
                        styles['external'][css_url] = f"/* CSS file too large or unavailable: {css_url} */"
                except Exception as e:
                    styles['external'][href] = f"/* Error loading CSS: {str(e)} */"
        
        # Inline styles
        for element in soup.find_all(style=True):
            styles['inline'].append({
                'element': element.name,
                'selector': self._generate_css_selector(element),
                'styles': element.get('style')
            })
        
        return styles
    
    def _extract_computed_styles(self, url: str) -> Dict[str, Dict[str, str]]:
        """Extract computed styles for all visible elements."""
        if not self.driver:
            return {}
        
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get all visible elements
            elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
            computed_styles = {}
            
            important_properties = [
                'width', 'height', 'margin', 'padding', 'border', 'position',
                'top', 'left', 'right', 'bottom', 'display', 'flex-direction',
                'justify-content', 'align-items', 'background-color', 'color',
                'font-family', 'font-size', 'font-weight', 'line-height',
                'text-align', 'z-index', 'opacity', 'transform', 'transition'
            ]
            
            for i, element in enumerate(elements[:100]):  # Limit to first 100 elements
                try:
                    if element.is_displayed():
                        tag_name = element.tag_name
                        element_id = element.get_attribute('id')
                        element_classes = element.get_attribute('class')
                        
                        # Generate unique selector
                        selector = self._generate_selenium_selector(element, tag_name, element_id, element_classes)
                        
                        # Get computed styles for important properties
                        element_styles = {}
                        for prop in important_properties:
                            try:
                                value = element.value_of_css_property(prop.replace('_', '-'))
                                if value and value != 'none' and value != 'auto':
                                    element_styles[prop] = value
                            except:
                                continue
                        
                        if element_styles:
                            computed_styles[selector] = element_styles
                            
                except Exception:
                    continue
            
            return computed_styles
            
        except Exception as e:
            print(f"Error extracting computed styles: {e}")
            return {}
    
    def _extract_measurements(self, url: str) -> Dict[str, str]:
        """Extract precise measurements of key elements."""
        if not self.driver:
            return {}
        
        try:
            self.driver.get(url)
            measurements = {}
            
            # Key elements to measure
            key_selectors = [
                'body', 'header', 'main', 'footer', 'nav',
                '.container', '.wrapper', '.content',
                'h1', 'h2', 'h3', 'button', 'a'
            ]
            
            for selector in key_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        element = elements[0]  # Take first match
                        size = element.size
                        location = element.location
                        
                        measurements[selector] = {
                            'width': f"{size['width']}px",
                            'height': f"{size['height']}px",
                            'x': f"{location['x']}px",
                            'y': f"{location['y']}px"
                        }
                except Exception:
                    continue
            
            return measurements
            
        except Exception as e:
            print(f"Error extracting measurements: {e}")
            return {}
    
    def _extract_typography(self, url: str) -> Dict[str, Dict[str, str]]:
        """Extract detailed typography information."""
        if not self.driver:
            return {}
        
        try:
            self.driver.get(url)
            typography = {}
            
            # Text elements to analyze
            text_selectors = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'a', 'button', 'label']
            
            for selector in text_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        element = elements[0]  # Analyze first occurrence
                        
                        typography[selector] = {
                            'font-family': element.value_of_css_property('font-family'),
                            'font-size': element.value_of_css_property('font-size'),
                            'font-weight': element.value_of_css_property('font-weight'),
                            'font-style': element.value_of_css_property('font-style'),
                            'line-height': element.value_of_css_property('line-height'),
                            'letter-spacing': element.value_of_css_property('letter-spacing'),
                            'text-transform': element.value_of_css_property('text-transform'),
                            'text-decoration': element.value_of_css_property('text-decoration'),
                            'color': element.value_of_css_property('color')
                        }
                except Exception:
                    continue
            
            return typography
            
        except Exception as e:
            print(f"Error extracting typography: {e}")
            return {}
    
    def _extract_comprehensive_colors(self, styles: Dict[str, Any], computed_styles: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        """Extract comprehensive color palette from all sources."""
        colors = {}
        color_pattern = re.compile(r'#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})|rgb\([^)]+\)|rgba\([^)]+\)|hsl\([^)]+\)|hsla\([^)]+\)')
        
        # Extract from CSS styles
        all_css = ""
        if isinstance(styles.get('internal'), list):
            all_css += " ".join(styles['internal'])
        if isinstance(styles.get('external'), dict):
            all_css += " ".join(styles['external'].values())
        
        # Find all color values
        found_colors = color_pattern.findall(all_css)
        
        # Extract from computed styles
        for selector, style_props in computed_styles.items():
            for prop, value in style_props.items():
                if 'color' in prop.lower() and value:
                    colors[f"{selector}_{prop}"] = value
        
        # Create a clean color palette
        unique_colors = set()
        for match in re.finditer(color_pattern, all_css):
            unique_colors.add(match.group())
        
        # Organize colors by type
        organized_colors = {
            'primary_colors': list(unique_colors)[:10],  # First 10 unique colors
            'background_colors': [],
            'text_colors': [],
            'border_colors': []
        }
        
        # Categorize colors from computed styles
        for selector, style_props in computed_styles.items():
            if 'background-color' in style_props:
                organized_colors['background_colors'].append(style_props['background-color'])
            if 'color' in style_props:
                organized_colors['text_colors'].append(style_props['color'])
            if 'border-color' in style_props:
                organized_colors['border_colors'].append(style_props['border-color'])
        
        # Remove duplicates
        for category in organized_colors:
            organized_colors[category] = list(set(organized_colors[category]))
        
        return organized_colors
    
    def _extract_layout_structure(self, url: str) -> Dict[str, Any]:
        """Extract detailed layout structure with positioning."""
        if not self.driver:
            return {}
        
        try:
            self.driver.get(url)
            
            layout = {
                'page_structure': {},
                'grid_systems': [],
                'flexbox_containers': [],
                'positioning': {}
            }
            
            # Analyze main layout containers
            containers = self.driver.find_elements(By.CSS_SELECTOR, 'body > *, header, main, footer, nav, .container, .wrapper')
            
            for container in containers:
                try:
                    display = container.value_of_css_property('display')
                    position = container.value_of_css_property('position')
                    
                    container_info = {
                        'tag': container.tag_name,
                        'display': display,
                        'position': position,
                        'size': container.size,
                        'location': container.location
                    }
                    
                    if 'grid' in display:
                        layout['grid_systems'].append(container_info)
                    elif 'flex' in display:
                        layout['flexbox_containers'].append(container_info)
                    
                    if position in ['absolute', 'fixed', 'relative']:
                        layout['positioning'][f"{container.tag_name}_{container.get_attribute('class') or 'no-class'}"] = {
                            'position': position,
                            'top': container.value_of_css_property('top'),
                            'left': container.value_of_css_property('left'),
                            'right': container.value_of_css_property('right'),
                            'bottom': container.value_of_css_property('bottom'),
                            'z-index': container.value_of_css_property('z-index')
                        }
                        
                except Exception:
                    continue
            
            return layout
            
        except Exception as e:
            print(f"Error extracting layout structure: {e}")
            return {}
    
    def _extract_responsive_data(self, url: str) -> Dict[str, Any]:
        """Extract responsive design information."""
        if not self.driver:
            return {}
        
        try:
            responsive_data = {}
            
            # Test different viewport sizes
            viewports = [
                ('desktop', self.config.screenshot_width, self.config.screenshot_height),
                ('tablet', self.config.tablet_width, self.config.tablet_height),
                ('mobile', self.config.mobile_width, self.config.mobile_height)
            ]
            
            for viewport_name, width, height in viewports:
                self.driver.set_window_size(width, height)
                self.driver.get(url)
                time.sleep(2)  # Wait for responsive changes
                
                # Capture key measurements at this viewport
                body = self.driver.find_element(By.TAG_NAME, 'body')
                responsive_data[viewport_name] = {
                    'viewport_size': {'width': width, 'height': height},
                    'body_size': body.size,
                    'scroll_height': self.driver.execute_script("return document.body.scrollHeight"),
                    'visible_elements': len(self.driver.find_elements(By.CSS_SELECTOR, "*:not([style*='display: none'])")),
                }
            
            # Reset to default size
            self.driver.set_window_size(self.config.screenshot_width, self.config.screenshot_height)
            
            return responsive_data
            
        except Exception as e:
            print(f"Error extracting responsive data: {e}")
            return {}
    
    def _extract_animations(self, styles: Dict[str, Any]) -> Dict[str, Any]:
        """Extract animation and transition information."""
        animations = {
            'css_animations': [],
            'transitions': [],
            'transforms': []
        }
        
        # Combine all CSS
        all_css = ""
        if isinstance(styles.get('internal'), list):
            all_css += " ".join(styles['internal'])
        if isinstance(styles.get('external'), dict):
            all_css += " ".join(styles['external'].values())
        
        # Find keyframe animations
        keyframe_pattern = re.compile(r'@keyframes\s+([^{]+)\s*{([^}]+)}', re.MULTILINE)
        keyframes = keyframe_pattern.findall(all_css)
        
        for name, rules in keyframes:
            animations['css_animations'].append({
                'name': name.strip(),
                'rules': rules.strip()
            })
        
        # Find transitions
        transition_pattern = re.compile(r'transition[^;]*:[^;]*;', re.IGNORECASE)
        transitions = transition_pattern.findall(all_css)
        animations['transitions'] = [t.strip() for t in transitions]
        
        # Find transforms
        transform_pattern = re.compile(r'transform[^;]*:[^;]*;', re.IGNORECASE)
        transforms = transform_pattern.findall(all_css)
        animations['transforms'] = [t.strip() for t in transforms]
        
        return animations
    
    def _extract_interactions(self, url: str) -> Dict[str, Any]:
        """Extract interactive elements and their states."""
        if not self.driver:
            return {}
        
        try:
            self.driver.get(url)
            interactions = {
                'clickable_elements': [],
                'form_elements': [],
                'hover_effects': []
            }
            
            # Find clickable elements
            clickable = self.driver.find_elements(By.CSS_SELECTOR, 'a, button, [onclick], [role="button"]')
            for element in clickable[:20]:  # Limit to first 20
                try:
                    interactions['clickable_elements'].append({
                        'tag': element.tag_name,
                        'text': element.text[:50],  # First 50 chars
                        'href': element.get_attribute('href') if element.tag_name == 'a' else None,
                        'size': element.size,
                        'location': element.location
                    })
                except Exception:
                    continue
            
            # Find form elements
            form_elements = self.driver.find_elements(By.CSS_SELECTOR, 'input, textarea, select, button[type="submit"]')
            for element in form_elements:
                try:
                    interactions['form_elements'].append({
                        'tag': element.tag_name,
                        'type': element.get_attribute('type'),
                        'placeholder': element.get_attribute('placeholder'),
                        'name': element.get_attribute('name'),
                        'size': element.size
                    })
                except Exception:
                    continue
            
            return interactions
            
        except Exception as e:
            print(f"Error extracting interactions: {e}")
            return {}
    
    def _extract_assets(self, base_url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract information about images and other assets."""
        assets = {
            'images': [],
            'icons': [],
            'videos': [],
            'fonts': []
        }
        
        # Extract images
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                assets['images'].append({
                    'src': urljoin(base_url, src),
                    'alt': img.get('alt', ''),
                    'width': img.get('width'),
                    'height': img.get('height'),
                    'loading': img.get('loading'),
                    'sizes': img.get('sizes'),
                    'srcset': img.get('srcset')
                })
        
        # Extract icons (SVG, icon fonts, etc.)
        for svg in soup.find_all('svg'):
            assets['icons'].append({
                'type': 'svg',
                'viewBox': svg.get('viewBox'),
                'width': svg.get('width'),
                'height': svg.get('height'),
                'content': str(svg)[:200]  # First 200 chars
            })
        
        # Extract videos
        for video in soup.find_all('video'):
            assets['videos'].append({
                'src': video.get('src'),
                'poster': video.get('poster'),
                'width': video.get('width'),
                'height': video.get('height'),
                'autoplay': video.get('autoplay') is not None,
                'controls': video.get('controls') is not None
            })
        
        return assets
    
    def _take_screenshots(self, url: str) -> Dict[str, str]:
        """Take screenshots at different viewport sizes."""
        if not self.driver:
            return {}
        
        try:
            screenshots = {}
            
            viewports = [
                ('desktop', self.config.screenshot_width, self.config.screenshot_height),
                ('tablet', self.config.tablet_width, self.config.tablet_height),
                ('mobile', self.config.mobile_width, self.config.mobile_height)
            ]
            
            for viewport_name, width, height in viewports:
                self.driver.set_window_size(width, height)
                self.driver.get(url)
                time.sleep(3)  # Wait for page to fully load
                
                # Take screenshot
                screenshot = self.driver.get_screenshot_as_png()
                screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
                screenshots[viewport_name] = f"data:image/png;base64,{screenshot_b64}"
            
            return screenshots
            
        except Exception as e:
            print(f"Error taking screenshots: {e}")
            return {}
    
    # Helper methods
    def _extract_comprehensive_meta(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract comprehensive meta information."""
        meta = {}
        
        # Basic meta tags
        if soup.title:
            meta['title'] = soup.title.string
        
        meta_tags = {
            'description': 'description',
            'keywords': 'keywords',
            'author': 'author',
            'viewport': 'viewport',
            'charset': 'charset'
        }
        
        for key, name in meta_tags.items():
            tag = soup.find('meta', attrs={'name': name}) or soup.find('meta', attrs={'property': name})
            if tag:
                meta[key] = tag.get('content', '')
        
        # Open Graph and Twitter meta
        og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
        for tag in og_tags:
            meta[tag.get('property')] = tag.get('content', '')
        
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        for tag in twitter_tags:
            meta[tag.get('name')] = tag.get('content', '')
        
        return meta
    
    def _extract_detailed_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed structural information."""
        structure = {}
        
        # Main structural elements
        structural_elements = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
        
        for element_name in structural_elements:
            elements = soup.find_all(element_name)
            if elements:
                structure[element_name] = []
                for elem in elements:
                    structure[element_name].append({
                        'classes': elem.get('class', []),
                        'id': elem.get('id'),
                        'children_count': len(elem.find_all(recursive=False)),
                        'text_content_length': len(elem.get_text(strip=True))
                    })
        
        return structure
    
    def _extract_all_elements(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract information about all elements."""
        elements = []
        
        for element in soup.find_all(True)[:200]:  # Limit to first 200 elements
            if element.name not in ['script', 'style', 'meta', 'link']:
                elem_info = {
                    'tag': element.name,
                    'classes': element.get('class', []),
                    'id': element.get('id'),
                    'text_length': len(element.get_text(strip=True)),
                    'has_children': len(element.find_all(recursive=False)) > 0,
                    'attributes': {k: v for k, v in element.attrs.items() if k not in ['class', 'id']}
                }
                
                if element.get('style'):
                    elem_info['inline_styles'] = element.get('style')
                
                elements.append(elem_info)
        
        return elements
    
    def _generate_css_selector(self, element) -> str:
        """Generate a CSS selector for an element."""
        selector_parts = [element.name]
        
        if element.get('id'):
            selector_parts.append(f"#{element.get('id')}")
        
        if element.get('class'):
            classes = element.get('class')
            if isinstance(classes, list):
                selector_parts.append('.' + '.'.join(classes))
        
        return ''.join(selector_parts)
    
    def _generate_selenium_selector(self, element, tag_name: str, element_id: str, element_classes: str) -> str:
        """Generate a unique selector for Selenium elements."""
        if element_id:
            return f"#{element_id}"
        elif element_classes:
            classes = element_classes.split()
            return f"{tag_name}.{'.'.join(classes[:2])}"  # Use first 2 classes
        else:
            return tag_name

# Example usage
async def example_comprehensive_scrape():
    """Example of comprehensive website scraping."""
    config = ScrapingConfig(
        include_screenshots=True,
        extract_computed_styles=True,
        extract_fonts=True,
        extract_animations=True,
        extract_responsive_data=True
    )
    
    scraper = AdvancedWebsiteScraper(config)
    
    try:
        # Scrape a website comprehensively
        result = scraper.scrape_comprehensive('https://example.com')
        
        print("Comprehensive scraping completed!")
        print(f"Extracted {len(result.get('computed_styles', {}))} computed styles")
        print(f"Found {len(result.get('colors', {}).get('primary_colors', []))} primary colors")
        print(f"Detected {len(result.get('elements', []))} elements")
        print(f"Captured {len(result.get('screenshots', {}))} screenshots")
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_comprehensive_scrape())