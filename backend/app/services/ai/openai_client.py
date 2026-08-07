"""OpenAI API client for LLM interactions"""

import logging
from typing import Optional, Dict, Any
from openai import OpenAI, APIError, RateLimitError
import json

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for OpenAI API interactions"""

    def __init__(self, api_key: str):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Cost-effective model
        self.max_retries = 2

    def analyze_query(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """
        Send prompt to LLM and get analysis
        
        Args:
            prompt: Analysis prompt
            temperature: Temperature for generation
            
        Returns:
            LLM response or None if failed
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business intelligence analyst. Provide clear, concise, and actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        except RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            return None
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI: {str(e)}")
            return None

    def answer_question(self, question: str, context: str = "") -> Optional[str]:
        """
        Answer a question with optional context
        
        Args:
            question: User question
            context: Relevant context
            
        Returns:
            Answer or None if failed
        """
        prompt = f"""Context:
{context}

Question: {question}

Provide a concise, business-focused answer."""
        
        return self.analyze_query(prompt, temperature=0.5)

    def extract_summary(self, text: str, summary_length: str = "short") -> Optional[str]:
        """
        Extract a summary from text
        
        Args:
            text: Text to summarize
            summary_length: 'short' (1-2 sentences), 'medium' (3-5 sentences), or 'long'
            
        Returns:
            Summary or None
        """
        length_instructions = {
            "short": "1-2 sentences",
            "medium": "3-5 sentences",
            "long": "8-10 sentences"
        }
        
        prompt = f"""Summarize the following text in {length_instructions.get(summary_length, '2-3 sentences')}:

{text}

Summary:"""
        
        return self.analyze_query(prompt, temperature=0.3)

    def format_json_response(self, data: Dict[str, Any], prompt_instruction: str = "") -> Optional[str]:
        """
        Format data as a readable response with LLM help
        
        Args:
            data: Data to format
            prompt_instruction: Additional instruction for formatting
            
        Returns:
            Formatted response or JSON string
        """
        json_str = json.dumps(data, default=str, indent=2)
        
        prompt = f"""Format this business data into a clear, readable text response:

Data:
{json_str}

{prompt_instruction}

Provide a well-formatted, business-friendly response:"""
        
        return self.analyze_query(prompt, temperature=0.5)

    def generate_insights(self, metrics: Dict[str, Any], industry_context: str = "") -> Optional[str]:
        """
        Generate insights from metrics
        
        Args:
            metrics: Business metrics dict
            industry_context: Industry context
            
        Returns:
            Generated insights or None
        """
        metrics_str = json.dumps(metrics, default=str, indent=2)
        
        prompt = f"""You are a business analyst. Generate key insights from these metrics.

Context: {industry_context if industry_context else "No specific context provided"}

Metrics:
{metrics_str}

Provide 3-5 key business insights including:
1. What's performing well
2. What needs attention
3. Recommendations for improvement

Format as bullet points."""
        
        return self.analyze_query(prompt, temperature=0.7)

    def health_check(self) -> bool:
        """
        Check if OpenAI API is accessible
        
        Returns:
            True if accessible, False otherwise
        """
        try:
            response = self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
