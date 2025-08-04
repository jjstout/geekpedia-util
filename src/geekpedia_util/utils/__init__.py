import re
import textwrap
import unicodedata

def slugify(value: str, max_length: int = 50) -> str:
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated dashes to single dashes.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase and strip leading/trailing whitespace.
    """
    value = value[:max_length]
    
    # Cribbed from Django's slugify implementation
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value).strip("-_")


def wrap_text(text: str, width: int = 80) -> str:
    """
    Wraps each paragraph in `text` so that no line exceeds `width` characters.
    
    Args:
        text:       The input string, potentially containing multiple paragraphs.
        width:      Maximum characters per line (default: 80).
    
    Returns:
        A new string with lines wrapped at the specified width, paragraphs separated
        by blank lines.
    """
    # From ChatGPT's response
    wrapper = textwrap.TextWrapper(width=width)
    wrapped_paragraphs = []
    
    # Split on two (or more) newlines to preserve paragraph structure
    paragraphs = text.split('\n\n')
    for para in paragraphs:
        # collapse any internal newlines to spaces so wrapping is smooth
        single_line = ' '.join(para.splitlines())
        wrapped = wrapper.fill(single_line)
        wrapped_paragraphs.append(wrapped)
    
    # Re-join paragraphs with double newline
    return '\n\n'.join(wrapped_paragraphs)

__all__ = ["slugify"]
