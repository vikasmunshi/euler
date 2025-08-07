#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution Info  for Project Euler problems."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from fcntl import LOCK_EX, LOCK_SH, LOCK_UN, flock
from functools import lru_cache
from json import JSONDecodeError, dump as json_dump, load as json_load
from os import getenv
from pathlib import Path
from typing import Any, Literal

from agents import function_tool
from yaml import Dumper, ScalarNode, dump as dump_yaml, safe_load as load_yaml

from euler.logger import logger
from euler.setup.ai_agent import AgenticModel, agentic_ai_tool
from euler.setup.base_dir import base_dir
from euler.setup.cached_requests import get_text_file
from euler.setup.py_module import get_module_source_code
from euler.setup.test_case import MAX_SHARABLE, TestCase, TestCaseCategory


@dataclass(frozen=True, kw_only=True, slots=True, eq=True, order=True)
class SolutionInfo:
    euler_problem: int = field(compare=True, )
    problem_name: str = field(compare=False, default='')
    problem_statement: str = field(compare=False, default='')
    solution_approach: str = field(compare=False, default='')
    solved: bool = field(compare=False, default=False)
    test_cases: list[TestCase] = field(compare=False, default_factory=list)
    __has_unsaved_changes__: bool = field(compare=False, init=False, repr=False, default=False)
    url: str = field(compare=False, default='')

    def __post_init__(self) -> None:
        if not self.url:
            object.__setattr__(self, 'url', f'https://projecteuler.net/problem={self.euler_problem}')
        if not self.problem_name or not self.problem_statement or not self.solution_approach:
            if ai_enrich_problem_info(self):
                logger.info({'action': 'ai_enrich updated SolutionInfo', 'problem': self.euler_problem, })
                self.mark_as_changed()
        if (num_test_cases := len(self.test_cases)) == 0:
            if ai_create_test_cases(self):
                logger.info({'action': 'ai_create_test_cases updated SolutionInfo', 'problem': self.euler_problem, })
                self.mark_as_changed()
        elif (num_test_cases >= 2 and
              sum(tc.test_case_category == TestCaseCategory.MAIN for tc in self.test_cases) != 1):
            if ai_identify_main_test_case(self):
                logger.info({'action': 'ai_identify updated SolutionInfo', 'problem': self.euler_problem, })
                self.mark_as_changed()

    def __enter__(self) -> SolutionInfo:
        if any(not f.exists() for f in self.file_paths):
            self.to_file()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.__has_unsaved_changes__:
            self.to_file()

    @property
    def solution_module(self) -> str:
        return f'euler.{get_file_path_structure(self.euler_problem, sep=".")}.{get_module_name(self.euler_problem)}'

    @property
    def test_case_answers(self) -> dict[str, Any]:
        return get_test_case_answers(self.euler_problem)

    @property
    def file_paths(self) -> tuple[Path, Path, Path, Path]:
        return get_file_paths(self.euler_problem)

    @property
    def answers_file(self) -> Path:
        return self.file_paths[0]

    @property
    def py_file(self) -> Path:
        return self.file_paths[1]

    @property
    def yaml_file(self) -> Path:
        return self.file_paths[2]

    @property
    def shared_py_file(self) -> Path:
        return self.file_paths[3]

    def mark_as_changed(self) -> None:
        if not self.__has_unsaved_changes__:
            object.__setattr__(self, '__has_unsaved_changes__', True)

    def record_answer(self, test_case: TestCase, result: Any, execution_time: float, func_name: str) -> None:
        if test_case.kwargs_str not in self.test_case_answers:
            self.test_case_answers[test_case.kwargs_str] = result
            self.mark_as_changed()
        if test_case.record(result, execution_time, func_name):
            self.mark_as_changed()
        logger.info({'action': 'answer recorded', 'problem': self.euler_problem,
                     'test_case': test_case.kwargs_str, 'result': result, 'time': execution_time, })

    def reset_answers(self) -> None:
        for test_case in self.test_cases:
            for k in list(test_case.solution_execution_time_in_sec.keys()):
                test_case.solution_execution_time_in_sec.pop(k)
        for k in list(self.test_case_answers.keys()):
            self.test_case_answers.pop(k)
        self.mark_as_changed()

    def as_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = asdict(self)
        for i, test_case in enumerate(self.test_cases):
            data['test_cases'][i] = test_case.as_dict()
        for private in [k for k in data.keys() if k.startswith('__')]:
            data.pop(private)
        if not self.solved and self.test_cases and all(test_case.solved for test_case in self.test_cases):
            data['solved'] = True
        return data

    def to_file(self) -> None:
        answers_file, py_file, yaml_file, shared_py_file = self.file_paths
        with open(yaml_file, 'w') as f:
            flock(f.fileno(), LOCK_EX)
            dump_yaml(self.as_dict(), f, indent=4, Dumper=SolutionInfoDumper)
            flock(f.fileno(), LOCK_UN)
        with open(answers_file, 'w') as f:
            flock(f.fileno(), LOCK_EX)
            json_dump(self.test_case_answers, f, indent=4)
            flock(f.fileno(), LOCK_UN)
        source_code: str = get_module_source_code(self, py_file)
        with open(py_file, 'w') as f:
            flock(f.fileno(), LOCK_EX)
            f.write(source_code)
            flock(f.fileno(), LOCK_UN)
        if self.euler_problem > MAX_SHARABLE:
            shared_source_code: str = get_module_source_code(self, shared_py_file, hide_answers=True)
            with open(shared_py_file, 'w') as f:
                flock(f.fileno(), LOCK_EX)
                f.write(shared_source_code)
                flock(f.fileno(), LOCK_UN)
        if self.__has_unsaved_changes__:
            object.__setattr__(self, '__has_unsaved_changes__', False)
        logger.info({'action': 'solution_info saved', 'number': self.euler_problem,
                     'files': (answers_file.name, py_file.name, yaml_file.name)})

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SolutionInfo:
        euler_problem: int = data['euler_problem']
        test_case_answers: dict[str, Any] = get_test_case_answers(euler_problem)
        for i, test_case_data in enumerate(data.get('test_cases', [])):
            data['test_cases'][i] = test_case = TestCase.from_dict(test_case_data)
            if test_case.result is None:
                object.__setattr__(test_case, 'result', test_case_answers.get(test_case.kwargs_str))
        info = cls(**data)
        return info

    @classmethod
    def from_file(cls, euler_problem: int) -> SolutionInfo:
        yaml_file = get_file_paths(euler_problem)[2]
        if yaml_file.exists():
            with open(yaml_file, 'r') as f:
                flock(f.fileno(), LOCK_EX)
                data = load_yaml(f)
                flock(f.fileno(), LOCK_UN)
            return cls.from_dict(data)
        return cls(euler_problem=euler_problem)


class SolutionInfoDumper(Dumper):
    def represent_scalar(self, tag: str, value: Any, style: str | None = None) -> ScalarNode:
        # Ensure all multiline strings (problem_statement, solution_approach) use block literal style '|4-'
        if isinstance(value, str) and ('\n' in value or r'\n' in value):
            style = '|'
            value = '\n'.join(line.rstrip() for line in value.splitlines())
        return super().represent_scalar(tag, value, style)


@lru_cache(maxsize=None)
def get_file_path_structure(euler_problem: int, *, sep: Literal['.', '/']) -> str:
    first: int = (100 * ((euler_problem - 1) // 100)) + 1
    last: int = first + 99
    return f'solutions{sep}solutions_{first:04d}_{last:04d}{sep}solution_{euler_problem:04d}'


@lru_cache(maxsize=None)
def get_module_name(euler_problem: int) -> str:
    _, py_file, _, shared_py_file = get_file_paths(euler_problem)
    if py_file.exists():
        return py_file.stem
    return shared_py_file.stem


@lru_cache(maxsize=None)
def get_test_case_answers(euler_problem: int) -> dict[str, Any]:
    answers_file = get_file_paths(euler_problem)[0]
    try:
        with open(answers_file, 'r') as f:
            flock(f.fileno(), LOCK_SH)
            test_case_answers: dict[str, Any] = json_load(f)
            flock(f.fileno(), LOCK_UN)
    except (FileNotFoundError, JSONDecodeError) as e:
        logger.warning({'action': 'error loading answers', 'euler problem': euler_problem, 'error': e, })
        test_case_answers = {}
    return test_case_answers


@lru_cache(maxsize=None)
def get_file_paths(euler_problem: int) -> tuple[Path, Path, Path, Path]:
    implementation_path: Path = base_dir / get_file_path_structure(euler_problem, sep='/')
    if not implementation_path.exists():
        implementation_path.mkdir(parents=True, exist_ok=True)
        (implementation_path.parent / '__init__.py').touch()
        (implementation_path / '__init__.py').touch()
    file_name_stem: str = 'private' if euler_problem > MAX_SHARABLE else 'solution'
    answers_file: Path = implementation_path / (file_name_stem + '.json')
    py_file: Path = implementation_path / (file_name_stem + '.py')
    yaml_file: Path = implementation_path / 'solution.yaml'
    shared_py_file: Path = implementation_path / 'solution.py'
    return answers_file, py_file, yaml_file, shared_py_file


"""******************************************* Agentic AI ***********************************************************"""


@function_tool
def get_problem_statement(euler_problem: int) -> str:
    """ Retrieve the HTML content of a Project Euler problem page, caching by default. """
    return get_text_file(f'https://projecteuler.net/problem={euler_problem}', force_refresh=False)


def ai_enrich_problem_info(info: SolutionInfo) -> bool:
    if not getenv('OPENAI_API_KEY'):
        logger.warning({'action': 'missing openai api key', 'euler problem': info.euler_problem})
        return False
    enriched_info: SolutionInfo = agentic_ai_tool(f'euler_problem={info.euler_problem}',
                                                  name='Project Euler Information Extractor',
                                                  instructions=project_euler_information_extractor_instructions_text,
                                                  tools=[get_problem_statement],
                                                  output_type=SolutionInfo,
                                                  model=AgenticModel.gpt_4_1_mini, )
    if not isinstance(enriched_info, SolutionInfo):
        logger.error({'action': 'ai_enrich failed', 'euler problem': info.euler_problem,  # type: ignore[unreachable]
                      'enriched_info': enriched_info, 'type': type(enriched_info).__name__, })
        return False
    object.__setattr__(info, 'problem_name', enriched_info.problem_name)
    object.__setattr__(info, 'problem_statement', enriched_info.problem_statement)
    object.__setattr__(info, 'solution_approach', enriched_info.solution_approach)
    return True


def ai_create_test_cases(info: SolutionInfo) -> bool:
    if not getenv('OPENAI_API_KEY'):
        logger.warning({'action': 'missing openai api key', 'euler problem': info.euler_problem})
        return False
    test_cases: list[TestCase] = agentic_ai_tool(f'euler_problem={info.euler_problem}',
                                                 name='Project Euler Test Case Creator',
                                                 instructions=project_euler_test_case_creator_instructions_text,
                                                 tools=[get_problem_statement],
                                                 output_type=list[TestCase],
                                                 model=AgenticModel.gpt_4_1_mini, )
    if (not isinstance(test_cases, list) and
            all(isinstance(test_case, TestCase) for test_case in test_cases)):  # type: ignore[unreachable]
        logger.error({'action': 'ai_create_test_cases failed',  # type: ignore[unreachable]
                      'euler problem': info.euler_problem, 'test_cases': test_cases,
                      'type': [type(test_case).__name__ for test_case in test_cases], })
        return False
    info.test_cases.extend(test_cases)
    return True


def ai_identify_main_test_case(info: SolutionInfo) -> bool:
    if not getenv('OPENAI_API_KEY'):
        logger.warning({'action': 'missing openai api key', 'euler problem': info.euler_problem})
        return False
    test_cases: list[dict[str, Any]] = [test_case.as_dict() for test_case in info.test_cases]
    main_test_case: TestCase = agentic_ai_tool(f'euler_problem={info.euler_problem}, test_cases={test_cases!r}',
                                               name='Project Euler Main Test Case Identifier',
                                               instructions=project_euler_main_test_case_identifier_instructions_text,
                                               tools=[get_problem_statement],
                                               output_type=TestCase,
                                               model=AgenticModel.gpt_4_1_mini, )
    if not isinstance(main_test_case, TestCase):
        logger.error({'action': 'ai_identify failed', 'euler problem': info.euler_problem,  # type: ignore[unreachable]
                      'main_test_case': main_test_case, 'type': type(main_test_case).__name__, })
        return False
    test_case_category = TestCaseCategory.PRELIMINARY
    for test_case in info.test_cases:
        if test_case == main_test_case:
            object.__setattr__(test_case, 'test_case_category', TestCaseCategory.MAIN)
            test_case_category = TestCaseCategory.EXTENDED
        else:
            object.__setattr__(test_case, 'test_case_category', test_case_category)
    return True


project_euler_information_extractor_instructions_text: str = """
You are the 'Project Euler Information Extractor' agent.
Parse a Project Euler problem page and return a structured JSON object with:

1. Problem Name
- Extract the <h2> inside <div id="content">.
- Convert to lowercase snake_case for a Python function:
  - Replace spaces/punctuation with underscores.
  - Remove invalid identifier characters.
  - Collapse multiple underscores; trim leading/trailing underscores.

2. Problem Statement
- Extract from <div class="problem_content">.
- Output is for YAML and Python docstrings.
- Process as follows:
  - Strip all HTML tags.
  - Decode all entities:
    - &lt; → <, &gt; → >, &amp; → &, &quot; → ", &apos; → '
    - &nbsp;, &ensp;, &emsp;, &thinsp; → space
    - &le; → ≤, &ge; → ≥, &ne; → ≠, &times; → ×
    - &alpha; → α, &beta; → β, &pi; → π, etc.
    - Convert Unicode escapes: \u2264 → ≤, \u03c0 → π, etc.
    - Convert numeric entities: &#nnnn; → Unicode
  - Sanitize:
    - Remove control characters (ASCII <32 or >126)
    - Replace × or &times; with " x " (with spaces)
    - Normalize quotes, dashes, and whitespace
    - Preserve math symbols
  - Formatting:
    - Preserve paragraph breaks with blank lines
    - Wrap at 80 characters, indent 4 spaces
    - Return plain text: no triple quotes, no \n escapes, no trailing spaces
    - Must be multiple lines

3. Solution Approach
- Provide an instructive, multi-line outline for solving the problem.
- Do not compute or include the final numeric answer.
- Focus on relevant mathematical concepts, algorithms, or computational techniques.
- Use clear instructional language (e.g., “Consider using dynamic programming…”).
- Wrap text at 80 characters for readability.
- Ensure the output is more than one line.

4. Output Format
Return a JSON object like:
{
  "euler_problem": "<input_euler_problem>",
  "problem_name": "<snake_case_name>",
  "problem_statement": "<formatted_docstring>",
  "solution_approach": "<multi_line_outline>"
}

Final Rules
- Follow PEP 8 naming
- Ignore irrelevant HTML (navigation, ads, etc.)
- Ensure problem_statement and solution_approach are multi-line
"""

project_euler_main_test_case_identifier_instructions_text: str = """
You are the 'Project Euler Main Test Case Identifier' agent.

Your mission is to identify the main test case for Project Euler problem out of a list of TestCase objects.

1. **Input Analysis**:
   - You receive a list of TestCase objects for a specific Project Euler problem
   - Each TestCase contains: euler_problem, kwargs, result, solved, and test_case_category fields
   - Always use the get_problem_statement tool to retrieve the problem description

2. **Identification Process**:
   - Use get_problem_statement to understand the problem requirements
   - Examine each test case's kwargs (inputs) and result (expected output)
   - Compare the test cases against the problem statement to identify which matches the main problem
   - Look for test cases that directly address the problem statement's question
   - The MAIN test case typically uses the exact values mentioned in the problem statement

3. **Selection Criteria**:
   - The MAIN test case should solve the exact problem as stated in the problem description
   - For numerical problems, check which test case uses the specific number mentioned in the problem
   - For optimization problems, identify which test case tests the actual constraints
   - Only ONE test case should be identified as MAIN

4. **Return Structure**:
   - Return a single TestCase object that corresponds to the MAIN test case
   - The returned object should have the exact same structure as received, with all fields preserved
   - Ensure the test_case_category field is set to "main"
   - Do not return the entire list of test cases, only the main one

Example input:
[
  {
    "euler_problem": 42,
    "kwargs": {"max_limit": 10},
    "result": 123,
    "solved": true,
    "test_case_category": "preliminary"
  },
  {
    "euler_problem": 42,
    "kwargs": {"max_limit": 1000},
    "result": 12345,
    "solved": true,
    "test_case_category": "preliminary"
  }
]

Example return:
{
  "euler_problem": 42,
  "kwargs": {"max_limit": 1000},
  "result": 12345,
  "solved": true,
  "test_case_category": "main"
}
"""

project_euler_test_case_creator_instructions_text: str = """
You are the 'Project Euler Test Case Creator' agent.

Your mission is to generate a list of TestCase objects for a given Project Euler problem.

### Instructions:

1. **Retrieve Problem Description**:
   - Use the `get_problem_statement` tool to fetch the problem description for the specified Project Euler problem.

2. **Understand Inputs and Outputs**:
   - Analyze the problem description, paying attention to:
     - Any specific examples of input and output provided.
     - The main question or directive outlined in the problem.

3. **Create Test Cases**:
   - Follow these guidelines to produce the test cases:
     - Use examples from the problem description as **'preliminary'** test cases:
       - `test_case_category`: Set to `"preliminary"`.
       - `kwargs`: Map input arguments as key-value pairs.
       - `result`: Use the example outputs as the expected result.
     - Create a single **'main'** test case that addresses the central question of the problem:
       - `test_case_category`: Set to `"main"`.
       - `kwargs`: Use input values that correspond to the main problem requirements.
       - `result`: Must be `null` (since this is the test case to compute the final solution).

4. **Consistency of Test Cases**:
   - Ensure that all `kwargs` dictionaries in the test cases have the same structure and identical keys.

5. **Output Format**:
   - Return a JSON-like list of test cases, where each test case contains:
     - `euler_problem`: The Project Euler problem number.
     - `kwargs`: Dictionary representing arguments specific to the test case.
     - `result`: The expected result, or `null` for the main test case.
     - `test_case_category`: Category of test case (`"preliminary"`, `"main"`).

### Example Output

    For Problem 6:
    [
        {
            "euler_problem": 6,
            "kwargs": { "n": 10 },
            "result": 2640,
            "test_case_category": "preliminary"
        },
        {
            "euler_problem": 6,
            "kwargs": { "n": 100 },
            "result": null,
            "test_case_category": "main"
        }
    ]

    For Problem 9:
    [
        {
            "euler_problem": 9,
            "kwargs": { "sum_sides": 12 },
            "result": 60,
            "test_case_category": "preliminary"
        },
        {
            "euler_problem": 9,
            "kwargs": { "sum_sides": 1000 },
            "result": null,
            "test_case_category": "main"
        }
    ]

    For Problem 18:
    [
        {
            "euler_problem": 18,
            "kwargs": { "triangle_str": "TRIANGLE_A" },
            "result": 23,
            "test_case_category": "preliminary"
        },
        {
            "euler_problem": 18,
            "kwargs": { "triangle_str": "TRIANGLE_B" },
            "result": null,
            "test_case_category": "main"
        }
    ]

    For Problem 42:
    [
        {
            "euler_problem": 42,
            "kwargs": { "file_url": "https://projecteuler.net/resources/documents/0042_words.txt" },
            "result": null,
            "test_case_category": "main"
        }
    ]

    For Problem 81:
    [
        {
            "euler_problem": 81,
            "kwargs": { "file_url": "" },
            "result": 2427,
            "test_case_category": "preliminary"
        },
        {
            "euler_problem": 81,
            "kwargs": { "file_url": "https://projecteuler.net/resources/documents/0081_matrix.txt" },
            "result": null,
            "test_case_category": "main"
        }
    ]

### Key Requirements:
- Ensure exactly one test case is categorized as `"main"`.
- All test cases must accurately reflect the problem description and adhere to the outlined format.
"""
