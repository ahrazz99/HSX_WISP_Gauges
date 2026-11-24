"""
src/util/process.py
Generic process isolation utilities to execute crash-prone or hang-prone
C/Fortran functions in a safe, disposable worker process.
"""

from typing import Callable, Any, Tuple, Optional
import multiprocessing as mp


def _worker_wrapper(func: Callable, args: tuple, kwargs: dict, queue: mp.Queue):
    """Executes target function and puts (success, result, error_str) on queue."""
    try:
        result = func(*args, **kwargs)
        queue.put((True, result, None))
    except Exception as e:
        queue.put((False, None, str(e)))


def run_isolated(
    func: Callable,
    *args,
    timeout: Optional[float] = 15.0,
    **kwargs,
) -> Tuple[bool, Any, Optional[str]]:
    """
    Executes func(*args, **kwargs) in a separate operating system process.
    Guards against Fortran 'ERROR STOP', C-extension segfaults, and infinite loops.

    Args:
        func: The function to execute.
        *args: Positional arguments to pass to func.
        timeout: Maximum seconds to wait before terminating the process (default: 15s).
        **kwargs: Keyword arguments to pass to func.

    Returns:
        (success: bool, result: Any, error_message: Optional[str])
    """
    queue = mp.Queue()
    proc = mp.Process(
        target=_worker_wrapper,
        args=(func, args, kwargs, queue),
    )
    proc.start()
    proc.join(timeout=timeout)

    # 1. Check if the function hung/timed out
    if proc.is_alive():
        proc.terminate()
        proc.join()
        return False, None, f"Execution timed out after {timeout} seconds."

    # 2. Check if Fortran called ERROR STOP or C segfaulted (exit code != 0)
    if proc.exitcode != 0:
        return False, None, f"Worker process crashed with exit code {proc.exitcode} (e.g. Fortran ERROR STOP)."

    # 3. Retrieve normal return value or Python exception
    if not queue.empty():
        success, result, err_msg = queue.get()
        return success, result, err_msg

    return False, None, "Worker exited without returning data."