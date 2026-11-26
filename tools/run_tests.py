#!/usr/bin/env python3
"""Run the unittest suite of every service.

Each service keeps its tests in services/<service>/tests/ and its package next
to them, so the tests are discovered with the service folder as the working
directory. Standard library only.

Usage:
  python tools/run_tests.py              # all services
  python tools/run_tests.py billing auth # only the named services
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    wanted = set(sys.argv[1:])
    services = sorted(p.parent for p in (ROOT / "services").glob("*/tests") if p.is_dir())
    if wanted:
        unknown = wanted - {s.name for s in services}
        if unknown:
            print(f"unknown service(s): {', '.join(sorted(unknown))}")
            return 2
        services = [s for s in services if s.name in wanted]

    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    failed: list[str] = []
    total = 0
    for service in services:
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            cwd=service, env=env, capture_output=True, text=True,
        )
        match = re.search(r"Ran (\d+) tests?", result.stderr)
        count = int(match.group(1)) if match else 0
        total += count
        ok = result.returncode == 0 and count > 0
        print(f"{'ok  ' if ok else 'FAIL'} {service.name:<14} {count:>3} tests")
        if not ok:
            failed.append(service.name)
            print(result.stderr)

    print(f"\n{total} tests in {len(services)} services, {len(failed)} service(s) failing")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
