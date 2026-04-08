"""
LLM client wrapper for generating insights
"""

from openai import OpenAI
from typing import Optional
import re


def format_numbers_in_text(text: str) -> str:
    """
    Format numbers in text to include thousand separators.
    Examples:
        1000 -> 1,000
        15000 -> 15,000
        1234567 -> 1,234,567
    
    Args:
        text: Input text with numbers
        
    Returns:
        Text with formatted numbers
    """
    def format_number(match):
        num_str = match.group(0)
        # Skip if already has comma or is part of a decimal
        if ',' in num_str or '.' in num_str:
            return num_str
        
        try:
            num = int(num_str)
            # Only format numbers >= 1000
            if num >= 1000:
                return f"{num:,}"
            return num_str
        except ValueError:
            return num_str
    
    # Match standalone numbers (not part of URLs, dates, or already formatted)
    # Negative lookbehind: not preceded by . or /
    # Negative lookahead: not followed by . or /
    pattern = r'(?<![.,/])\b(\d{4,})\b(?![.,/])'
    return re.sub(pattern, format_number, text)


class LLMClient:
    """Wrapper for OpenAI-compatible LLM client"""
    
    def __init__(self, api_key: str, base_url: str, model: str, 
                 temperature: float = 0.2, system_prompt: str = ""):
        """
        Initialize LLM client
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for API endpoint
            model: Model name to use
            temperature: Temperature for generation
            system_prompt: Default system prompt
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
    
    def generate_insight(self, prompt: str, 
                         system_prompt: Optional[str] = None,
                         format_numbers: bool = True) -> str:
        """
        Generate insight using LLM
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt override
            format_numbers: Whether to format numbers with thousand separators
            
        Returns:
            Generated text
        """
        sys_prompt = system_prompt or self.system_prompt
        
        import time
        start_time = time.time()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature
        )
        
        elapsed = time.time() - start_time
        print(f"         → API call completed in {elapsed:.1f}s")
        
        result = response.choices[0].message.content.strip()
        
        # Format numbers in the result
        if format_numbers:
            result = format_numbers_in_text(result)
        
        return result
