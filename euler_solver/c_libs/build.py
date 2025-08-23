#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Callable, List

from Cython.Build import cythonize
from setuptools import Extension, setup


def build() -> None:
    c_libs_path = Path(__file__).parent
    sources = sorted(c_libs_path.glob('sources/*.pyx'))

    # Validate that there are source files to compile
    if not sources:
        raise FileNotFoundError('No .pyx files were found in the sources directory.')

    # Setup extensions
    ext_modules: List[Extension] = []
    for pyx_file in sources:
        module_name = f'euler_solver.c_libs.{pyx_file.stem}'  # Fully-qualified module name
        ext_modules.append(Extension(module_name, sources=[pyx_file.as_posix()]))

    # Cythonize and compile
    setup(ext_modules=cythonize(ext_modules, compiler_directives={'language_level': '3'}, ),
          script_args=['build_ext', '--inplace'], )

    # Generate __init__.py dynamically
    init_file: Path = c_libs_path / '__init__.py'
    init_code: str = '#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n\n'
    init_code += '\n'.join([f'from euler_solver.c_libs.{pyx_file.stem} import {pyx_file.stem}' for pyx_file in sources])
    init_code += '\n\n__all__ = [\n'
    init_code += ',\n'.join([f"    '{pyx_file.stem}'" for pyx_file in sources])
    init_code += '\n]\n'
    with open(init_file, 'w') as f:
        f.write(init_code)
    print(f'Generated {init_file} with the following content:\n{init_code}')

    # Dynamic imports to verify integrity of compiled modules
    for pyx_file in sources:
        pyx_file.with_suffix('.c').unlink(missing_ok=True)
        pyi_file: Path = c_libs_path / f'{pyx_file.stem}.pyi'
        module_name = f"euler_solver.c_libs.{pyx_file.stem}"
        try:
            module: ModuleType = import_module(module_name)
            func_defs: str = getattr(module, '__pyi__')
            with open(pyi_file, 'w') as f:
                f.write(f'from typing import *\n\n{func_defs}')
            print(f'Successfully imported {module_name} with definitions: {func_defs}')
            func_name: str = pyx_file.stem
            func: Callable = getattr(module, func_name)
            assert callable(func), f'Expected {func_name} to be callable, got {func}'
        except ImportError as e:
            print(f'Failed to import module {module_name}: {e}')
            raise


if __name__ == '__main__':
    build()
