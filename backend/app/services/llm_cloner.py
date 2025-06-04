from openai import AsyncOpenAI
import os
from typing import Dict, Any
import json

class LLMCloner:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    async def generate_html(self, design_context: Dict[str, Any]) -> str:
        """Generate HTML for the cloned website using OpenAI."""
        try:
            # Prepare the prompt
            prompt = self._create_prompt(design_context)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Using GPT-4 for best results
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert web developer specializing in HTML and CSS. 
                        Your task is to create a pixel-perfect clone of a website based on the provided design context.
                        Focus on matching the visual appearance, layout, and styling as closely as possible.
                        Include all necessary CSS inline or in a style tag.
                        Ensure the HTML is valid and follows best practices."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            # Extract the generated HTML
            generated_html = response.choices[0].message.content
            
            # Clean up the response (remove markdown code blocks if present)
            if generated_html.startswith('```html'):
                generated_html = generated_html[7:]
            if generated_html.endswith('```'):
                generated_html = generated_html[:-3]
            
            return generated_html.strip()
            
        except Exception as e:
            raise Exception(f"Error generating HTML: {str(e)}")
    
    def _create_prompt(self, design_context: Dict[str, Any]) -> str:
        """Create a detailed prompt for the LLM based on the design context."""
        prompt = f"""Please create a clone of the website at {design_context['url']} based on the following information:

1. Website Structure:
{json.dumps(design_context['structure'], indent=2)}

2. Meta Information:
- Title: {design_context['meta']['title']}
- Description: {design_context['meta']['description']}
- Viewport: {design_context['meta']['viewport']}

3. Color Scheme:
{json.dumps(design_context['colors'], indent=2)}

4. Original HTML Structure:
{design_context['html'][:1000]}...  # First 1000 characters for reference

Please create a complete HTML document that closely matches the original website's appearance.
Include all necessary CSS inline or in a style tag.
Focus on matching the visual appearance, layout, and styling as closely as possible.
Ensure the HTML is valid and follows best practices.

Return only the HTML code without any additional explanation or markdown formatting."""
        
        return prompt 