#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../backend"

cd "$BACKEND_DIR"

echo "Running tests from: $(pwd)"
echo "================================"

pip install -r requirements.txt

if [[ "$1" == "--coverage" ]]; then
    echo "Running tests with coverage..."
    rm -rf htmlcov/ .coverage
    python -m pytest -v --cov=. --cov-report=term-missing --cov-report=html:htmlcov --cov-report=json:coverage.json
    echo ""
    echo "========================================"
    echo "Coverage Summary"
    echo "========================================"
    python -c "
import json
with open('coverage.json') as f:
    data = json.load(f)

total = data['totals']
overall = round(total['percent_covered'])
covered = total['covered_lines']
stmts = total['num_statements']

print(f'Overall: {overall}% ({covered}/{stmts} statements)')
print('')

with_cov = []
without_cov = []

for path, file_data in data['files'].items():
    if not path.startswith('tests/'):
        summary = file_data['summary']
        pct = round(summary['percent_covered'])
        stmts = summary['num_statements']
        cov = summary['covered_lines']
        if cov > 0:
            with_cov.append((path, pct, cov, stmts))
        else:
            without_cov.append(path)

if with_cov:
    print('Files WITH coverage:')
    for path, pct, cov, stmts in sorted(with_cov, key=lambda x: -x[1]):
        print(f'  {pct}% - {path} ({cov}/{stmts})')
    print('')

print(f'Files WITHOUT coverage ({len(without_cov)} total):')
for path in without_cov[:10]:
    print(f'  - {path}')
if len(without_cov) > 10:
    print(f'  ... and {len(without_cov) - 10} more')
"
    echo ""
    echo "Full HTML report: backend/htmlcov/index.html"
else
    python -m pytest -v --tb=short
fi

echo "================================"
echo "Tests complete"
