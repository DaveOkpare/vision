from pydantic_ai import Agent
from pydantic_ai.messages import ImageUrl
import os
import base64
import io
import json
import re
from PIL import Image
from typing import Dict, List


class SimpleAIAgent:
    """AI agent for analyzing grid images and detecting objects."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the AI agent.
        
        Args:
            api_key: OpenAI API key. If None, will use environment variable.
        """
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize pydantic-ai Agent with OpenAI GPT-4o model
        self.agent = Agent('openai:gpt-4o')
        
    def analyze_grid(self, grid_image: Image.Image, object_description: str) -> Dict[str, List]:
        """
        Analyze a grid image to find cells containing the target object.
        
        Args:
            grid_image: PIL Image with grid overlay
            object_description: Description of object to find
            
        Returns:
            Dict with 'cells' and 'confidence_scores' lists
        """
        # Convert PIL Image to base64 data URL for multimodal input
        buffer = io.BytesIO()
        grid_image.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        data_url = f"data:image/png;base64,{img_base64}"
        
        # Create prompt for grid analysis
        prompt = f"""You are analyzing an image with a numbered grid overlay. Your task is to identify which grid cells contain any part of: {object_description}

Look at each numbered cell and determine:
1. Does this cell contain any portion of the target object?
2. What's your confidence percentage (0-100%)?

Return ONLY this format:
{{
    'cells': [cell_numbers_with_object],
    'confidence_scores': [confidence_for_each_cell]
}}

Confidence guidelines:
- 90-100%: Most of cell contains object
- 80-89%: About half the cell contains object  
- 70-79%: Substantial portion but less than half
- 60-69%: Small edge or corner of object
- Below 60%: Too uncertain - omit cell

Only include cells with confidence ≥60%. Sort cell numbers in ascending order."""

        # Send multimodal message using ImageUrl with data URL
        result = self.agent.run_sync([
            prompt,
            ImageUrl(url=data_url)
        ])
        
        # Parse the response to extract structured data
        return self._parse_response(result.output)
    
    def _parse_response(self, response: str) -> Dict[str, List]:
        """
        Parse AI response to extract cells and confidence scores.
        
        Args:
            response: Raw AI response string
            
        Returns:
            Dict with 'cells' and 'confidence_scores' lists
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # Replace single quotes with double quotes for valid JSON
                json_str = json_str.replace("'", '"')
                parsed = json.loads(json_str)
                
                # Ensure we have the expected keys
                if 'cells' in parsed and 'confidence_scores' in parsed:
                    return {
                        'cells': parsed['cells'],
                        'confidence_scores': parsed['confidence_scores']
                    }
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            print(f"Response was: {response}")
        
        # Fallback: return empty response
        return {'cells': [], 'confidence_scores': []}