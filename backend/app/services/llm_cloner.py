import google.generativeai as genai
import os
from typing import Dict, Any, Optional, List, Tuple
import json
import asyncio
import logging
from dataclasses import dataclass, field
import re
from enum import Enum
import base64
from PIL import Image
import io

def make_json_safe(obj):
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    elif 'bs4' in str(type(obj)):  # Catch BeautifulSoup, Tag, etc.
        return str(obj)
    else:
        return obj


class CloneAccuracy(Enum):
    BASIC = "basic"
    HIGH = "high"
    PIXEL_PERFECT = "pixel_perfect"

@dataclass
class PrecisionCloneConfig:
    """Advanced configuration for high-precision website cloning."""
    model: str = "gemini-1.5-pro"
    temperature: float = 0.1
    max_tokens: int = 8192
    accuracy_level: CloneAccuracy = CloneAccuracy.PIXEL_PERFECT
    
    # Visual fidelity options
    preserve_exact_spacing: bool = True
    preserve_exact_colors: bool = True
    preserve_exact_typography: bool = True
    preserve_animations: bool = True
    preserve_interactions: bool = True
    
    # Technical options
    use_css_grid: bool = True
    use_flexbox: bool = True
    include_responsive: bool = True
    optimize_for_performance: bool = False
    
    # Advanced features
    multi_pass_generation: bool = True
    include_accessibility: bool = True
    preserve_exact_dimensions: bool = True
    use_screenshots: bool = True  # New: Use screenshots for visual reference
    
    # Debug options
    include_debug_comments: bool = False
    verbose_logging: bool = True

class HighPrecisionLLMCloner:
    def __init__(self, config: Optional[PrecisionCloneConfig] = None):
        """Initialize the high-precision LLM cloner with Gemini."""
        self.config = config or PrecisionCloneConfig()
        self.logger = self._setup_logger()
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=self.config.model,
            generation_config=genai.types.GenerationConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens,
            )
        )
        
    def _setup_logger(self) -> logging.Logger:
        """Setup detailed logging."""
        logger = logging.getLogger(__name__)
        level = logging.DEBUG if self.config.verbose_logging else logging.INFO
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def generate_pixel_perfect_html(self, design_context: Dict[str, Any]) -> str:
        """Generate pixel-perfect HTML with enhanced Gemini prompting."""
        try:
            self.logger.info(f"Starting pixel-perfect generation for {design_context.get('url', 'unknown URL')}")
            
            # Enhanced validation
            self._validate_comprehensive_context(design_context)
            
            if self.config.multi_pass_generation:
                return await self._multi_pass_generation(design_context)
            else:
                return await self._single_pass_generation(design_context)
                
        except Exception as e:
            self.logger.error(f"Error in pixel-perfect generation: {str(e)}")
            raise Exception(f"Error generating pixel-perfect HTML: {str(e)}")
    
    async def _multi_pass_generation(self, design_context: Dict[str, Any]) -> str:
        """Generate multiple versions with different approaches."""
        self.logger.info("Starting multi-pass generation")
        
        # Pass 1: Structure-focused
        structure_html = await self._generate_structure_focused(design_context)
        
        # Pass 2: Visual-focused with screenshots
        visual_html = await self._generate_visual_focused(design_context)
        
        # Pass 3: Refinement pass
        refined_html = await self._generate_refinement_pass(design_context, structure_html, visual_html)
        
        return refined_html
    
    async def _generate_structure_focused(self, design_context: Dict[str, Any]) -> str:
        """Generate HTML focusing on structure and layout."""
        prompt = self._create_structure_prompt(design_context)
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return self._clean_html_response(response.text)
        except Exception as e:
            self.logger.error(f"Structure generation failed: {e}")
            raise
    
    async def _generate_visual_focused(self, design_context: Dict[str, Any]) -> str:
        """Generate HTML with visual accuracy focus using screenshots."""
        prompt_parts = [self._create_visual_prompt(design_context)]
        
        # Add screenshots if available
        if self.config.use_screenshots and 'screenshots' in design_context:
            screenshots = design_context['screenshots']
            for viewport, screenshot_data in screenshots.items():
                if screenshot_data.startswith('data:image'):
                    # Extract base64 data
                    image_data = screenshot_data.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    
                    # Create PIL Image
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    prompt_parts.append(f"\n\n🖼️ SCREENSHOT ({viewport.upper()}):")
                    prompt_parts.append(image)
                    prompt_parts.append(f"This is the {viewport} view of the website. Recreate this EXACTLY.")
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt_parts)
            return self._clean_html_response(response.text)
        except Exception as e:
            self.logger.error(f"Visual generation failed: {e}")
            # Fallback without images
            response = await asyncio.to_thread(self.model.generate_content, prompt_parts[0])
            return self._clean_html_response(response.text)
    
    async def _generate_refinement_pass(self, design_context: Dict[str, Any], 
                                       structure_html: str, visual_html: str) -> str:
        """Final refinement pass combining best of both approaches."""
        prompt = f"""
🎯 FINAL REFINEMENT PASS - PIXEL PERFECT WEBSITE CLONE

You are tasked with creating the FINAL, PIXEL-PERFECT version of a website clone.
I have two draft versions generated with different approaches:

VERSION 1 (Structure-focused):
```html
{structure_html[:4000]}...
```

VERSION 2 (Visual-focused):
```html
{visual_html[:4000]}...
```

DESIGN CONTEXT:
{json.dumps(make_json_safe(design_context), indent=2)[:3000]}...

🎯 YOUR MISSION:
Create a FINAL version that combines the best elements from both versions while achieving PIXEL-PERFECT accuracy.

🔥 CRITICAL REQUIREMENTS:
1. EXACT VISUAL MATCHING - Every pixel must match the original
2. PERFECT SPACING - Use exact measurements from the design context
3. PRECISE COLORS - Match all colors exactly using provided values
4. EXACT TYPOGRAPHY - Font families, sizes, weights must be identical
5. RESPONSIVE PERFECTION - Must work flawlessly on all devices
6. SMOOTH INTERACTIONS - All hover effects and animations must work

🛠️ TECHNICAL SPECIFICATIONS:
- Use modern CSS (Grid, Flexbox, Custom Properties)
- Implement exact pixel values from measurements
- Include all computed styles for precision
- Add smooth transitions and hover effects
- Ensure cross-browser compatibility
- Optimize for performance while maintaining accuracy

🎨 VISUAL FIDELITY CHECKLIST:
□ Header height and positioning exact
□ Navigation styling and spacing precise
□ Color scheme matches perfectly
□ Typography is pixel-perfect
□ Button styles and hover states correct
□ Layout spacing and alignment exact
□ Images and icons positioned correctly
□ Footer matches original exactly

OUTPUT: Return ONLY the complete, pixel-perfect HTML document.
NO explanations, NO markdown formatting, NO additional text.
"""
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return self._clean_html_response(response.text)
        except Exception as e:
            self.logger.error(f"Refinement generation failed: {e}")
            # Return the better of the two versions
            return visual_html if len(visual_html) > len(structure_html) else structure_html
    
    async def _single_pass_generation(self, design_context: Dict[str, Any]) -> str:
        """Single pass generation with comprehensive prompting."""
        prompt = self._create_comprehensive_prompt(design_context)
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return self._clean_html_response(response.text)
        except Exception as e:
            self.logger.error(f"Single pass generation failed: {e}")
            raise
    
    def _create_structure_prompt(self, design_context: Dict[str, Any]) -> str:
        """Create structure-focused prompt."""
        return f"""
🏗️ STRUCTURE-PERFECT WEBSITE CLONE

Create a pixel-perfect HTML structure for: {design_context.get('url', 'website')}

LAYOUT STRUCTURE:
{json.dumps(design_context.get('layout_structure', {}), indent=2)}

COMPUTED STYLES:
{json.dumps(design_context.get('computed_styles', {}), indent=2)}

MEASUREMENTS:
{json.dumps(design_context.get('measurements', {}), indent=2)}

ELEMENTS:
{json.dumps(design_context.get('elements', [])[:20], indent=2)}

🎯 FOCUS: Perfect HTML structure with semantic elements and exact CSS layout.
Create a complete, self-contained HTML document with embedded CSS.
"""
    
    def _create_visual_prompt(self, design_context: Dict[str, Any]) -> str:
        """Create visual-focused prompt."""
        return f"""
🎨 VISUAL-PERFECT WEBSITE CLONE

Target URL: {design_context.get('url', 'website')}

COLORS (EXACT MATCH REQUIRED):
{json.dumps(design_context.get('colors', {}), indent=2)}

TYPOGRAPHY (PIXEL-PERFECT):
{json.dumps(design_context.get('typography', {}), indent=2)}

VISUAL STYLES:
{json.dumps(design_context.get('computed_styles', {}), indent=2)}

ANIMATIONS & INTERACTIONS:
{json.dumps(design_context.get('animations', {}), indent=2)}

🎯 FOCUS: Perfect visual appearance with exact colors, fonts, and styling.
The screenshots above show EXACTLY how it should look.
Match every visual detail precisely.
"""
    
    def _create_comprehensive_prompt(self, design_context: Dict[str, Any]) -> str:
        """Create comprehensive single-pass prompt."""
        sections = []
        
        sections.append("🚀 PIXEL-PERFECT WEBSITE CLONE GENERATOR")
        sections.append("=" * 60)
        sections.append(f"Target: {design_context.get('url', 'website')}")
        sections.append("")
        
        # Add visual reference if screenshots available
        if 'screenshots' in design_context and design_context['screenshots']:
            sections.append("📸 VISUAL REFERENCE:")
            sections.append("The provided screenshots show EXACTLY how the website should look.")
            sections.append("Your HTML must match these visuals PERFECTLY.")
            sections.append("")
        
        # Critical measurements
        if 'measurements' in design_context:
            sections.append("📏 EXACT MEASUREMENTS (CRITICAL):")
            for selector, measurements in design_context['measurements'].items():
                sections.append(f"  {selector}: {measurements}")
            sections.append("")
        
        # Color specifications
        if 'colors' in design_context:
            sections.append("🎨 COLOR PALETTE (EXACT VALUES):")
            colors = design_context['colors']
            for category, color_list in colors.items():
                if color_list:
                    sections.append(f"  {category}: {color_list[:5]}")  # Show first 5
            sections.append("")
        
        # Typography
        if 'typography' in design_context:
            sections.append("📝 TYPOGRAPHY (PIXEL-PERFECT):")
            for element, styles in design_context['typography'].items():
                sections.append(f"  {element}:")
                for prop, value in styles.items():
                    if value and value != 'none':
                        sections.append(f"    {prop}: {value}")
            sections.append("")
        
        # Layout structure
        if 'layout_structure' in design_context:
            sections.append("🏗️ LAYOUT STRUCTURE:")
            sections.append(json.dumps(design_context['layout_structure'], indent=2))
            sections.append("")
        
        # Computed styles (most critical)
        if 'computed_styles' in design_context:
            sections.append("💎 COMPUTED STYLES (EXACT VALUES):")
            styles = design_context['computed_styles']
            for selector, style_props in list(styles.items())[:15]:  # Limit to first 15
                sections.append(f"  {selector}:")
                for prop, value in style_props.items():
                    sections.append(f"    {prop}: {value}")
                sections.append("")
        
        # Responsive breakpoints
        if 'responsive_breakpoints' in design_context:
            sections.append("📱 RESPONSIVE BREAKPOINTS:")
            sections.append(json.dumps(design_context['responsive_breakpoints'], indent=2))
            sections.append("")
        
        # Critical instructions
        instructions = [
            "🎯 CRITICAL INSTRUCTIONS:",
            "",
            "1. VISUAL PERFECTION:",
            "   - Match screenshots EXACTLY if provided",
            "   - Use precise pixel values from measurements",
            "   - Implement exact colors and typography",
            "   - Preserve all spacing and proportions",
            "",
            "2. TECHNICAL EXCELLENCE:",
            "   - Modern HTML5 semantic structure",
            "   - CSS Grid and Flexbox for layout",
            "   - Responsive design with exact breakpoints",
            "   - Smooth animations and transitions",
            "",
            "3. CODE QUALITY:",
            "   - Clean, maintainable CSS",
            "   - Proper accessibility attributes",
            "   - Cross-browser compatibility",
            "   - Performance optimized",
            "",
            "4. VALIDATION:",
            "   - Every measurement must be exact",
            "   - All colors must match precisely",
            "   - Typography must be pixel-perfect",
            "   - Layout must be structurally identical",
            "",
            "🚨 CRITICAL: Return ONLY the complete HTML document.",
            "NO explanations, NO markdown, NO additional text.",
            "The HTML must be complete and self-contained with embedded CSS.",
        ]
        
        sections.extend(instructions)
        
        return "\n".join(sections)
    
    def _validate_comprehensive_context(self, design_context: Dict[str, Any]) -> None:
        """Enhanced validation for comprehensive data."""
        critical_fields = ['url']
        high_quality_fields = ['computed_styles', 'measurements', 'colors', 'typography']
        
        # Check critical fields
        missing_critical = [field for field in critical_fields if field not in design_context]
        if missing_critical:
            raise ValueError(f"Missing critical fields: {missing_critical}")
        
        # Check data quality
        total_data_points = 0
        for field in high_quality_fields:
            if field in design_context and design_context[field]:
                if isinstance(design_context[field], dict):
                    total_data_points += len(design_context[field])
                elif isinstance(design_context[field], list):
                    total_data_points += len(design_context[field])
        
        if total_data_points < 10:
            self.logger.warning(f"Low data quality: only {total_data_points} data points extracted")
            self.logger.warning("Consider improving scraping configuration for better results")
    
    def _clean_html_response(self, html_content: str) -> str:
        """Clean and enhance HTML response from Gemini."""
        if not html_content:
            raise ValueError("Received empty HTML response")
        
        # Remove markdown formatting
        html_content = re.sub(r'^```html\n?', '', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^```\n?$', '', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'```$', '', html_content)
        html_content = html_content.strip()
        
        # Ensure proper HTML structure
        if not html_content.lower().startswith('<!doctype') and not html_content.lower().startswith('<html'):
            # Add basic HTML structure if missing
            if '<html' not in html_content.lower():
                html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloned Website</title>
</head>
<body>
{html_content}
</body>
</html>"""
        
        # Add viewport meta tag if missing and responsive is enabled
        if self.config.include_responsive and 'viewport' not in html_content.lower():
            html_content = html_content.replace(
                '</head>', 
                '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n</head>'
            )
        
        return html_content
    
    def analyze_clone_quality(self, generated_html: str, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of the generated clone."""
        analysis = {
            'html_length': len(generated_html),
            'has_complete_structure': self._has_complete_html_structure(generated_html),
            'estimated_elements': generated_html.count('<') - generated_html.count('</'),
            'has_inline_styles': '<style>' in generated_html or 'style=' in generated_html,
            'has_responsive_meta': 'viewport' in generated_html.lower(),
            'css_properties_count': len(re.findall(r'[a-zA-Z-]+\s*:\s*[^;]+;', generated_html)),
            'color_usage': len(re.findall(r'#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)', generated_html)),
        }
        
        # Check for key elements from design context
        if 'elements' in design_context:
            expected_elements = len(design_context['elements'])
            analysis['expected_elements'] = expected_elements
            analysis['element_coverage'] = min(analysis['estimated_elements'] / expected_elements, 1.0) if expected_elements > 0 else 0
        
        # Quality score calculation
        quality_score = 0
        if analysis['has_complete_structure']:
            quality_score += 25
        if analysis['has_inline_styles']:
            quality_score += 25
        if analysis['has_responsive_meta']:
            quality_score += 20
        if analysis['css_properties_count'] > 50:
            quality_score += 20
        if analysis['color_usage'] > 5:
            quality_score += 10
        
        analysis['quality_score'] = quality_score
        analysis['quality_rating'] = (
            'Excellent' if quality_score >= 90 else
            'Good' if quality_score >= 70 else
            'Fair' if quality_score >= 50 else
            'Poor'
        )
        
        return analysis
    
    def _has_complete_html_structure(self, html_content: str) -> bool:
        """Check if HTML has complete structure."""
        html_lower = html_content.lower()
        required_tags = ['<html', '</html>', '<head', '</head>', '<body', '</body>']
        return all(tag in html_lower for tag in required_tags)

# Enhanced example usage
async def example_enhanced_clone():
    """Example of enhanced pixel-perfect cloning."""
    config = PrecisionCloneConfig(
        model="gemini-1.5-pro",
        accuracy_level=CloneAccuracy.PIXEL_PERFECT,
        multi_pass_generation=True,
        use_screenshots=True,
        preserve_exact_dimensions=True,
        verbose_logging=True
    )
    
    cloner = HighPrecisionLLMCloner(config)
    
    # Enhanced design context example
    design_context = {
        'url': 'https://example.com',
        'computed_styles': {
            'body': {
                'margin': '0px',
                'padding': '0px',
                'font-family': '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
                'font-size': '16px',
                'line-height': '1.6',
                'color': '#1a1a1a',
                'background-color': '#ffffff'
            },
            'header': {
                'height': '72px',
                'background-color': '#ffffff',
                'border-bottom': '1px solid #e5e7eb',
                'padding': '0 32px',
                'display': 'flex',
                'align-items': 'center',
                'justify-content': 'space-between'
            },
            '.nav-link': {
                'color': '#6b7280',
                'text-decoration': 'none',
                'font-weight': '500',
                'padding': '8px 16px',
                'border-radius': '6px',
                'transition': 'all 0.2s ease'
            },
            '.nav-link:hover': {
                'color': '#1f2937',
                'background-color': '#f3f4f6'
            }
        },
        'measurements': {
            'header': {'height': '72px', 'padding': '0 32px'},
            'container': {'max-width': '1200px', 'margin': '0 auto'},
            'button': {'height': '40px', 'padding': '0 24px', 'border-radius': '6px'}
        },
        'colors': {
            'primary_colors': ['#3b82f6', '#1d4ed8', '#ffffff'],
            'text_colors': ['#1a1a1a', '#6b7280', '#9ca3af'],
            'background_colors': ['#ffffff', '#f9fafb', '#f3f4f6'],
            'border_colors': ['#e5e7eb', '#d1d5db']
        },
        'typography': {
            'h1': {
                'font-family': '"Inter", sans-serif',
                'font-size': '48px',
                'font-weight': '700',
                'line-height': '1.1',
                'letter-spacing': '-0.02em'
            },
            'body': {
                'font-family': '"Inter", sans-serif',
                'font-size': '16px',
                'font-weight': '400',
                'line-height': '1.6'
            }
        }
    }
    
    try:
        html_result = await cloner.generate_pixel_perfect_html(design_context)
        quality_analysis = cloner.analyze_clone_quality(html_result, design_context)
        
        print(f"✅ Clone generated successfully!")
        print(f"📊 Quality Score: {quality_analysis['quality_score']}/100 ({quality_analysis['quality_rating']})")
        print(f"📏 HTML Length: {quality_analysis['html_length']:,} characters")
        print(f"🎨 CSS Properties: {quality_analysis['css_properties_count']}")
        print(f"🌈 Colors Used: {quality_analysis['color_usage']}")
        
        return html_result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(example_enhanced_clone())