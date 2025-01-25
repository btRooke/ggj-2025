import sys
from pathlib import Path

from mypy import api

PACKAGE_ROOT = Path(__file__).parent.resolve()

def _run_mypy():
    out, err, code = api.run([str(PACKAGE_ROOT)])
    print(out, file=sys.stdout, end="")
    print(err, file=sys.stderr, end="")
    if code != 0:
        exit(code)

if __name__ == "__main__":
    _run_mypy()