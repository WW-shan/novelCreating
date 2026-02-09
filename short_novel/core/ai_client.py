"""
Claude API wrapper with retry logic
"""
import os
import time
from pathlib import Path
import httpx
from anthropic import Anthropic

# Load .env file if exists (check multiple locations)
def _load_dotenv():
    """Load environment variables from .env file."""
    env_locations = [
        Path(__file__).parent.parent / ".env",  # short_novel/.env
        Path(__file__).parent.parent.parent / ".env",  # project root/.env
    ]

    for env_path in env_locations:
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and key not in os.environ:  # Don't override existing
                            os.environ[key] = value
            break

_load_dotenv()

# Direct config to avoid import issues when run as script
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "")  # 支持自定义 API 中转
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-6")  # 支持自定义模型
API_TIMEOUT = int(os.environ.get("ANTHROPIC_TIMEOUT", "300"))  # 超时时间（秒），默认5分钟


def generate(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 4096,
    retries: int = 3,
    retry_delay: float = 5.0,
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

    Environment variables:
        ANTHROPIC_API_KEY: Your API key (required)
        ANTHROPIC_BASE_URL: Custom API base URL for proxy (optional)
        ANTHROPIC_MODEL: Model to use (default: claude-opus-4-6)
        ANTHROPIC_TIMEOUT: Request timeout in seconds (default: 300)
    """
    if not API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    # Create client with optional base_url and extended timeout
    timeout = httpx.Timeout(API_TIMEOUT, connect=60.0)

    if API_BASE_URL:
        client = Anthropic(api_key=API_KEY, base_url=API_BASE_URL, timeout=timeout)
    else:
        client = Anthropic(api_key=API_KEY, timeout=timeout)

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
            error_str = str(e)

            # Check for proxy timeout errors
            if "524" in error_str or "timeout" in error_str.lower():
                error_msg = "代理服务器超时 (Error 524) - 服务器可能过载，请稍后重试"
            elif "<!DOCTYPE" in error_str or "<html" in error_str:
                error_msg = "代理服务器返回了HTML错误页面 - 请检查代理服务器状态"
            else:
                error_msg = error_str[:200] if len(error_str) > 200 else error_str

            if attempt < retries - 1:
                print(f"API调用失败 (尝试 {attempt + 1}/{retries}): {error_msg}")
                print(f"{retry_delay}秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 1.5  # Exponential backoff

    raise last_error
