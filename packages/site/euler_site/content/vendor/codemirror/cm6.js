/* Vendored CodeMirror 6 bundle entry. Re-exports the symbols code.js uses.
   The dependency graph (mirrored from esm.sh, target es2022) lives beside this
   file as flat ./*.js modules with rewritten relative imports — fully offline.
   NB: the `codemirror` meta-package is pinned to 6.0.2; the bare `@6` range
   resolves to the legacy CodeMirror 5 UMD (v6.65.x) which lacks EditorView. */
export {EditorView, basicSetup} from "./codemirror_6_0_2.js";
export {EditorState, Compartment} from "./_codemirror_state_6.js";
export {keymap, lineNumbers, placeholder} from "./_codemirror_view_6.js";
export {indentWithTab} from "./_codemirror_commands_6.js";
export {indentUnit} from "./_codemirror_language_6.js";
export {linter, lintGutter, forceLinting} from "./_codemirror_lint_6.js";
export {python} from "./_codemirror_lang_python_6.js";
export {cpp} from "./_codemirror_lang_cpp_6.js";
export {json} from "./_codemirror_lang_json_6.js";
export {oneDark} from "./_codemirror_theme_one_dark_6.js";
