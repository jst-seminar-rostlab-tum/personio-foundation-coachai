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
