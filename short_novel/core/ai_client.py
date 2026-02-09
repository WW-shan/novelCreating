"""
Claude API wrapper with retry logic
"""
import os
import time
from anthropic import Anthropic

# Direct config to avoid import issues when run as script
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-opus-4-6"


def generate(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 4096,
    retries: int = 3,
    retry_delay: float = 2.0,
) -> str:
    """
    Generate text using Claude API.

    Args:
        system_prompt: System message for the model
        user_prompt: User message/query
        max_tokens: Maximum tokens in response
        retries: Number of retry attempts on failure
        retry_delay: Seconds to wait between retries

    Returns:
        Generated text response

    Raises:
        Exception: If all retries fail
    """
    if not API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = Anthropic(api_key=API_KEY)

    last_error = None
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                print(f"API call failed (attempt {attempt + 1}/{retries}): {e}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

    raise last_error
