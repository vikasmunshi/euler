#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from importlib import import_module
from pathlib import Path
from types import ModuleType

from Cython.Build import cythonize
from setuptools import Extension, setup


def build() -> None:
    c_libs_path: Path = Path(__file__).parent
    functions: list[Path] = sorted(c_libs_path.glob('sources/*.pyx'))
    sources: dict[str, Path] = {fun.stem: fun for fun in functions}
    setup(ext_modules=cythonize([Extension(f'euler_solver.c_libs._{k}', sources=[s.as_posix()])
                                 for k, s in sources.items()],
                                compiler_directives={'boundscheck': False, 'wraparound': False, 'cdivision': True}),
          script_args=['build_ext', '--inplace'])
    init_file: Path = c_libs_path / '__init__.py'
    init_code: str = '#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n'
    for func, pyx_file in sources.items():
        pyx_file.with_suffix('.c').unlink(missing_ok=True)
        module: ModuleType = import_module(f'euler_solver.c_libs._{func}')
        stub_code: str = getattr(module, '__signature__', '')
        pyi_file_path: Path = c_libs_path / ('_' + pyx_file.with_suffix('.pyi').name)
        with open(pyi_file_path, 'w') as f:
            f.write(stub_code)
        init_code += f'from euler_solver.c_libs._{func} import {func}\n'
    with open(init_file, 'w') as f:
        f.write(init_code)


if __name__ == '__main__':
    build()
