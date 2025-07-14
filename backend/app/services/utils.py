import unicodedata


# LLMs and user input may use different Unicode quote characters (e.g., curved vs. straight quotes),
# which can cause equality checks and downstream logic to fail if not normalized.
# This ensures all output quotes are consistent and comparable across the codebase.
def normalize_quotes(s: str) -> str:
    """
    Normalize all single quote characters in a string to straight quotes
    and apply Unicode normalization. This helps avoid subtle bugs when comparing LLM output,
    user input, and transcript content.
    """
    return unicodedata.normalize('NFKC', s.replace('’', "'").replace('‘', "'")) if s else s


def strip_markdown_code_block(s: str) -> str:
    """
    Remove markdown code block (```json ... ``` or ``` ... ```) from LLM output, if present.
    Returns the inner JSON string.
    """
    import re

    if not s:
        return s
    # Match ```json ... ``` or ``` ... ```
    match = re.match(r'^```(?:json)?\n([\s\S]*?)\n```$', s.strip())
    if match:
        return match.group(1)
    return s


def auto_strip_markdown_code_block(s: str) -> str:
    """
    Only strip markdown code block if s starts with ``` or ```json, otherwise return as is.
    """
    if not s:
        return s
    s_strip = s.strip()
    if s_strip.startswith('```'):
        return strip_markdown_code_block(s_strip)
    return s
