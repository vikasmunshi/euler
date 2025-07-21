#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from typing import Match

solution_template: str = r'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem {problem_number}:

Problem Statement:
{problem_content}

Solution Approach:

Test Cases:

URL: https://projecteuler.net/problem={problem_number}
Answer:
"""

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem={problem_number})
problem_number: int = {problem_number}

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={default_kwargs}, answer=None, ),
]

# Register this function as a solution for problem #{problem_number} with test cases
{default_solution}


{main_block}
'''.strip('\n')

default_solution: str = r'''
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def solution_name(*, kwarg: int) -> int:
    print(f'solution_name({kwarg=})' 'Not Implemented')
    raise NotImplementedError
'''.strip('\n')

main_block: str = r'''
if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
'''.strip('\n')


def get_module_content(problem_number: int, problem_content: str) -> str:
    formatted_problem_content = clean_and_format_problem_statement(problem_content)
    return solution_template.format(problem_number=problem_number,
                                    problem_content=formatted_problem_content,
                                    default_kwargs="{'kwarg': None}",
                                    default_solution=default_solution,
                                    main_block=main_block, )


def convert_latex_to_unicode(latex_string: str) -> str:
    r"""
    Convert LaTeX mathematical notation to Unicode characters.

    This function transforms LaTeX mathematical notation into equivalent Unicode characters,
    making mathematical expressions more readable in plain text. It handles Greek letters,
    mathematical operators, superscripts/subscripts, and other common LaTeX symbols.

    Args:
        latex_string: A string containing LaTeX mathematical notation

    Returns:
        A string with LaTeX notation converted to Unicode characters

    Example:
        >>> convert_latex_to_unicode(r'\alpha + \beta^2 \leq \gamma_n \times \sqrt{\pi}')
        'α + β² ≤ γₙ × √π'
    """
    # Greek letters
    greek_letters = {
        r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
        r'\epsilon': 'ε', r'\varepsilon': 'ε', r'\zeta': 'ζ', r'\eta': 'η',
        r'\theta': 'θ', r'\vartheta': 'ϑ', r'\iota': 'ι', r'\kappa': 'κ',
        r'\lambda': 'λ', r'\mu': 'μ', r'\nu': 'ν', r'\xi': 'ξ',
        r'\pi': 'π', r'\varpi': 'ϖ', r'\rho': 'ρ', r'\varrho': 'ϱ',
        r'\sigma': 'σ', r'\varsigma': 'ς', r'\tau': 'τ', r'\upsilon': 'υ',
        r'\phi': 'φ', r'\varphi': 'φ', r'\chi': 'χ', r'\psi': 'ψ', r'\omega': 'ω',
        r'\Gamma': 'Γ', r'\Delta': 'Δ', r'\Theta': 'Θ', r'\Lambda': 'Λ',
        r'\Xi': 'Ξ', r'\Pi': 'Π', r'\Sigma': 'Σ', r'\Upsilon': 'Υ',
        r'\Phi': 'Φ', r'\Psi': 'Ψ', r'\Omega': 'Ω',
    }

    # Comparison and mathematical operators
    operators = {
        r'\leq': '≤', r'\geq': '≥', r'\neq': '≠', r'\approx': '≈',
        r'\equiv': '≡', r'\sim': '∼', r'\simeq': '≃', r'\cong': '≅',
        r'\times': '×', r'\div': '÷', r'\pm': '±', r'\mp': '∓',
        r'\cdot': '·', r'\circ': '∘', r'\bullet': '•',
        r'\propto': '∝', r'\infty': '∞', r'\neg': '¬', r'\wedge': '∧', r'\vee': '∨',
        r'\subset': '⊂', r'\supset': '⊃', r'\subseteq': '⊆', r'\supseteq': '⊇',
        r'\cup': '∪', r'\cap': '∩', r'\setminus': '\\', r'\emptyset': '∅',
        r'\in': '∈', r'\ni': '∋', r'\notin': '∉',
        r'\forall': '∀', r'\exists': '∃', r'\nexists': '∄',
        r'\Rightarrow': '⇒', r'\Leftarrow': '⇐', r'\Leftrightarrow': '⇔',
        r'\rightarrow': '→', r'\leftarrow': '←', r'\leftrightarrow': '↔',
        r'\mapsto': '↦', r'\uparrow': '↑', r'\downarrow': '↓',
        r'\langle': '⟨', r'\rangle': '⟩', r'\lfloor': '⌊', r'\rfloor': '⌋',
        r'\lceil': '⌈', r'\rceil': '⌉',
        r'\sum': '∑', r'\prod': '∏', r'\int': '∫',
        r'\sqrt': '√', r'\partial': '∂', r'\nabla': '∇',
    }

    # Superscripts and subscripts (single characters only)
    superscripts = {
        '^0': '⁰', '^1': '¹', '^2': '²', '^3': '³', '^4': '⁴',
        '^5': '⁵', '^6': '⁶', '^7': '⁷', '^8': '⁸', '^9': '⁹',
        '^+': '⁺', '^-': '⁻', '^=': '⁼', '^(': '⁽', '^)': '⁾',
        '^n': 'ⁿ', '^i': 'ⁱ',
    }

    subscripts = {
        '_0': '₀', '_1': '₁', '_2': '₂', '_3': '₃', '_4': '₄',
        '_5': '₅', '_6': '₆', '_7': '₇', '_8': '₈', '_9': '₉',
        '_+': '₊', '_-': '₋', '_=': '₌', '_(': '₍', '_)': '₎',
        '_a': 'ₐ', '_e': 'ₑ', '_i': 'ᵢ', '_o': 'ₒ', '_u': 'ᵤ',
        '_x': 'ₓ', '_n': 'ₙ',
    }

    # First, replace the standard LaTeX symbols
    all_replacements = {**greek_letters, **operators}
    for latex_symbol, unicode_char in all_replacements.items():
        latex_string = latex_string.replace(latex_symbol, unicode_char)

    # Handle basic superscripts and subscripts (only works for single characters)
    for sup_pattern, sup_char in superscripts.items():
        latex_string = latex_string.replace(sup_pattern, sup_char)

    for sub_pattern, sub_char in subscripts.items():
        latex_string = latex_string.replace(sub_pattern, sub_char)

    # Handle \frac{numerator}{denominator}
    frac_pattern = r'\\frac\{([^}]*)\}\{([^}]*)\}'
    latex_string = re.sub(frac_pattern, r'\1/\2', latex_string)

    # Handle \text{...}
    text_pattern = r'\\text\{([^}]*)\}'
    latex_string = re.sub(text_pattern, r'\1', latex_string)

    # Remove remaining curly braces (simplified approach)
    latex_string = latex_string.replace('{', '').replace('}', '')

    return latex_string


def parse_html_tags(text: str) -> str:
    """
    Parse HTML tags and convert special characters to their text representation.

    This function processes HTML content from Project Euler problems, handling:
    - Common HTML tags (p, br, div, table, etc.)
    - HTML entities (both named and numeric)
    - LaTeX-style math notation frequently used in Project Euler
    - Code blocks and special formatting

    The goal is to create clean, readable plain text while preserving the
    mathematical expressions and problem structure.

    Args:
        text: HTML text to parse from a Project Euler problem

    Returns:
        Text with HTML tags properly processed and special characters converted
        to their text representation

    Example:
        >>> parse_html_tags("<p>Find the value of &sum;<sub>n</sub>.</p>")
        'Find the value of ∑ₙ.'
    """
    if not text:
        return ''

    # Step 1: Handle structured content (tables, lists, code blocks)

    # Process tables to maintain their structure
    def replace_table(match: Match[str]) -> str:
        table_html = match.group(0)
        # Convert each row to a line of text
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
        table_text = []
        for row in rows:
            # Extract cell contents from both th and td elements
            cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL)
            # Join cells with spaces or tabs
            table_text.append('  '.join(re.sub(r'<[^>]*>', '', cell) for cell in cells))
        # Join rows with newlines
        return '\n' + '\n'.join(table_text) + '\n'

    # Replace tables with structured text
    text = re.sub(r'<table[^>]*>.*?</table>', replace_table, text, flags=re.DOTALL)

    # Handle ordered and unordered lists
    def replace_list(match: Match[str]) -> str:
        list_type = 'ol' if match.group(1) == 'o' else 'u'
        list_html = match.group(0)
        items = re.findall(r'<li[^>]*>(.*?)</li>', list_html, re.DOTALL)
        result = '\n'
        for item_num, item in enumerate(items):
            # Use numbers for ordered lists, bullets for unordered
            prefix = f"{item_num + 1}. " if list_type == 'ol' else "• "
            # Clean the item content of any remaining tags
            clean_item = re.sub(r'<[^>]*>', '', item).strip()
            result += f"{prefix}{clean_item}\n"
        return result

    # Replace lists with properly formatted text
    text = re.sub(r'<([ou])l[^>]*>.*?</\1l>', replace_list, text, flags=re.DOTALL)

    # Handle code blocks and pre-formatted text
    def replace_code(match: Match[str]) -> str:
        code = match.group(1)
        # Preserve indentation and line breaks
        return '\n```\n' + code + '\n```\n'

    text = re.sub(r'<pre[^>]*>\s*<code[^>]*>(.*?)</code>\s*</pre>', replace_code, text, flags=re.DOTALL)

    # Step 2: Handle block-level elements and basic formatting

    # Replace heading tags with formatted text
    for i in range(1, 7):
        text = re.sub(f'<h{i}[^>]*>(.*?)</h{i}>', '\n\n\1\n', text, flags=re.DOTALL)

    # Replace paragraph and div tags with newlines
    text = re.sub(r'<(?:p|div)[^>]*>(.*?)</(?:p|div)>', r'\n\1\n', text, flags=re.DOTALL)

    # Replace <br> tags with newlines
    text = re.sub(r'<br\s*/?>', '\n', text)

    # Handle basic text formatting
    text = re.sub(r'<(?:b|strong)[^>]*>(.*?)</(?:b|strong)>', r'**\1**', text, flags=re.DOTALL)  # Bold
    text = re.sub(r'<(?:i|em)[^>]*>(.*?)</(?:i|em)>', r'*\1*', text, flags=re.DOTALL)  # Italic

    # Step 3: Handle superscripts, subscripts, and math notation

    # Convert superscripts to Unicode or ^ notation
    def replace_sup(match: Match[str]) -> str:
        content = match.group(1)
        # For single characters, use Unicode if available
        if len(content) == 1 and content in '0123456789+-=()ni':
            mapping = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
                       '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '+': '⁺', '-': '⁻',
                       '=': '⁼', '(': '⁽', ')': '⁾', 'n': 'ⁿ', 'i': 'ⁱ'}
            return mapping.get(content, f'^{content}')
        return f'^{content}'

    text = re.sub(r'<sup[^>]*>(.*?)</sup>', replace_sup, text, flags=re.DOTALL)

    # Convert subscripts to Unicode or _ notation
    def replace_sub(match: Match[str]) -> str:
        content = match.group(1)
        # For single characters, use Unicode if available
        if len(content) == 1 and content in '0123456789+-=()aeioxun':
            mapping = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅',
                       '6': '₆', '7': '₇', '8': '₈', '9': '₉', '+': '₊', '-': '₋',
                       '=': '₌', '(': '₍', ')': '₎', 'a': 'ₐ', 'e': 'ₑ', 'i': 'ᵢ',
                       'o': 'ₒ', 'x': 'ₓ', 'u': 'ᵤ', 'n': 'ₙ'}
            return mapping.get(content, f'_{content}')
        return f'_{content}'

    text = re.sub(r'<sub[^>]*>(.*?)</sub>', replace_sub, text, flags=re.DOTALL)

    # Step 4: Convert HTML entities

    # Expanded list of common HTML entities
    html_entities = {
        # Basic entities
        '&lt;': '<', '&gt;': '>', '&amp;': '&', '&quot;': '"', '&apos;': "'",
        '&nbsp;': ' ', '&ensp;': ' ', '&emsp;': '  ', '&thinsp;': ' ',

        # Punctuation
        '&mdash;': '—', '&ndash;': '–', '&hellip;': '…',
        '&ldquo;': '"', '&rdquo;': '"', '&lsquo;': "'", '&rsquo;': "'",
        '&laquo;': '«', '&raquo;': '»', '&bull;': '•', '&middot;': '·',

        # Mathematical symbols
        '&plusmn;': '±', '&times;': '×', '&divide;': '÷', '&ne;': '≠',
        '&le;': '≤', '&ge;': '≥', '&equiv;': '≡', '&sum;': '∑',
        '&prod;': '∏', '&int;': '∫', '&part;': '∂', '&infin;': '∞',
        '&therefore;': '∴', '&forall;': '∀', '&exist;': '∃',
        '&empty;': '∅', '&isin;': '∈', '&notin;': '∉',
        '&cap;': '∩', '&cup;': '∪', '&sub;': '⊂', '&sup;': '⊃',
        '&nabla;': '∇', '&radic;': '√', '&prop;': '∝',

        # Greek letters frequently used in math
        '&alpha;': 'α', '&beta;': 'β', '&gamma;': 'γ', '&delta;': 'δ',
        '&epsilon;': 'ε', '&zeta;': 'ζ', '&eta;': 'η', '&theta;': 'θ',
        '&iota;': 'ι', '&kappa;': 'κ', '&lambda;': 'λ', '&mu;': 'μ',
        '&nu;': 'ν', '&xi;': 'ξ', '&omicron;': 'ο', '&pi;': 'π',
        '&rho;': 'ρ', '&sigma;': 'σ', '&tau;': 'τ', '&upsilon;': 'υ',
        '&phi;': 'φ', '&chi;': 'χ', '&psi;': 'ψ', '&omega;': 'ω',
        '&Gamma;': 'Γ', '&Delta;': 'Δ', '&Theta;': 'Θ', '&Lambda;': 'Λ',
        '&Xi;': 'Ξ', '&Pi;': 'Π', '&Sigma;': 'Σ', '&Phi;': 'Φ',
        '&Psi;': 'Ψ', '&Omega;': 'Ω',

        # Arrows and special symbols
        '&larr;': '←', '&rarr;': '→', '&uarr;': '↑', '&darr;': '↓',
        '&harr;': '↔', '&crarr;': '↵', '&lArr;': '⇐', '&rArr;': '⇒',
        '&uArr;': '⇑', '&dArr;': '⇓', '&hArr;': '⇔',
        '&copy;': '©', '&reg;': '®', '&trade;': '™', '&deg;': '°',
        '&prime;': '′', '&Prime;': '″', '&micro;': 'µ'
    }

    # Replace HTML entities
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)

    # Handle numeric HTML entities (like &#39; for apostrophe)
    text = re.sub(r'&#(\d+);', lambda match: chr(int(match.group(1))), text)
    # Handle hex HTML entities
    text = re.sub(r'&#[xX]([0-9a-fA-F]+);', lambda match: chr(int(match.group(1), 16)), text)

    # Step 5: Handle LaTeX-style math notation often used in Project Euler problems

    # Convert common LaTeX commands
    latex_replacements = {
        '\\dots': '...',
        '\\ldots': '...',
        '\\cdot': '·',
        '\\cdots': '···',
        '\\approx': '≈',
        '\\leq': '≤',
        '\\geq': '≥',
        '\\neq': '≠',
        '\\equiv': '≡',
        '\\cong': '≅',
        '\\lfloor': '⌊',
        '\\rfloor': '⌋',
        '\\lceil': '⌈',
        '\\rceil': '⌉',
        '\\left': '',
        '\\right': '',
        '\\middle': '',
        '\\quad': '  ',
        '\\qquad': '    '
    }

    for latex_cmd, replacement in latex_replacements.items():
        text = text.replace(latex_cmd, replacement)

    # Step 6: Clean up any remaining HTML tags and formatting

    # Remove any remaining HTML tags
    text = re.sub(r'<[^>]*>', '', text)

    # Clean up excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple blank lines to one
    text = re.sub(r'^\s+|\s+$', '', text)  # Trim leading/trailing whitespace

    # Final transformations for readability
    text = text.replace('\t', '    ')  # Convert tabs to spaces for consistent formatting

    return text


def clean_and_format_problem_statement(text: str) -> str:
    r"""
    Clean and format a Project Euler problem statement by handling both HTML tags and LaTeX notation.

    This function provides a one-stop solution for processing Project Euler problem statements,
    combining HTML parsing and LaTeX conversion in the correct sequence with optimal settings.
    The result is clean, readable text with proper mathematical notation.

    The processing steps are:
    1. Parse and convert HTML tags and entities to plain text
    2. Handle LaTeX mathematical notation by converting to Unicode equivalents
    3. Apply final formatting for readability

    Args:
        text: The raw problem statement text containing HTML and LaTeX notation

    Returns:
        A cleaned and formatted problem statement with mathematical notation preserved

    Example:
        >>> clean_and_format_problem_statement('<p>Find $\sum_{i=1}^{n} i^2$ for $n = 100$.</p>')
        'Find ∑ᵢ₌₁ⁿ i² for n = 100.'
    """
    if not text:
        return ''

    # First, parse the HTML to handle tags and entities
    cleaned_text: str = parse_html_tags(text)

    # Handle dollar sign delimited LaTeX math
    # Extract math expressions between $ signs for special handling
    def process_math_expr(match: Match[str]) -> str:
        math_expr = match.group(1)
        # Keep the expression for LaTeX conversion but remove the $ delimiters
        return math_expr

    # Handle inline math expressions ($...$)
    cleaned_text = re.sub(r'\$(.*?)\$', process_math_expr, cleaned_text)

    # Handle display math expressions ($$...$$)
    cleaned_text = re.sub(r'\$\$(.*?)\$\$', lambda m: '\n' + m.group(1) + '\n', cleaned_text)

    # Now convert any LaTeX notation to Unicode
    formatted_text: str = convert_latex_to_unicode(cleaned_text)

    # Apply final formatting
    # Fix spacing around special characters
    formatted_text = re.sub(r'\s+([.,;:!?)])', r'\1', formatted_text)  # Remove space before punctuation
    formatted_text = re.sub(r'([({])\s+', r'\1', formatted_text)  # Remove space after opening brackets

    # Ensure consistent paragraph breaks
    formatted_text = re.sub(r'\n{3,}', '\n\n', formatted_text)  # Normalize multiple newlines

    # Special handling for Project Euler problem numbering style
    formatted_text = re.sub(r'(\d+)\.(\s+)', r'\1. \2', formatted_text)  # Ensure space after numbered items

    # Special handling for common Project Euler notations
    # Fix representation of sequences like a₁, a₂, ..., aₙ
    formatted_text = re.sub(r'([a-zA-Z])(₁|_1)\s*,\s*\1(₂|_2)\s*,\s*\.{3}\s*,\s*\1([ₙₘ]|_[nm])',
                            r'\1₁, \1₂, ..., \1\4', formatted_text)

    return formatted_text.strip()
