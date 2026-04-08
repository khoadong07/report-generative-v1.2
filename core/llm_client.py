"""
LLM client wrapper for generating insights
"""

from openai import OpenAI
from typing import Optional


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
                         system_prompt: Optional[str] = None) -> str:
        """
        Generate insight using LLM
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt override
            
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
        
        return response.choices[0].message.content.strip()
