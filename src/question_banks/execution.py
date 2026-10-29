from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def execute_python_test_cases(
    reference_solution: str,
    test_cases: list[str],
    *,
    test_imports: list[str] | None = None,
    timeout: float = 10.0,
) -> dict:
    """Execute a Python reference solution against its test cases in a subprocess.

    The code is written to a temporary file and run with ``python -I`` so that
    user site-packages and environment customisations do not affect execution.
    The function never evaluates code in the current process.
    """
    imports = "\n".join(test_imports or [])
    tests = "\n".join(test_cases or [])
    script = f"{imports}\n{reference_solution}\n{tests}\nprint('__GENASSESS_TESTS_PASSED__')\n"
    with tempfile.NamedTemporaryFile(
        "w", suffix=".py", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(script)
        script_path = Path(handle.name)
    try:
        completed = subprocess.run(
            [sys.executable, "-I", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir(),
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "passed": False,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": f"Execution timed out after {timeout} seconds.",
        }
    finally:
        script_path.unlink(missing_ok=True)
    passed = (
        completed.returncode == 0
        and "__GENASSESS_TESTS_PASSED__" in completed.stdout
    )
    return {
        "passed": passed,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


# Backwards/alternative friendly aliases.
run_python_test_cases = execute_python_test_cases
execute_test_cases = execute_python_test_cases
run_coding_tests = execute_python_test_cases