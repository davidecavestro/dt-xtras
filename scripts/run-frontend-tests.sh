#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="${SCRIPT_DIR}/../frontend"

cd "$FRONTEND_DIR"

echo "Running frontend tests from: $(pwd)"
echo "================================"

npm ci

if [[ "$1" == "--coverage" ]]; then
    echo "Running tests with coverage..."
    rm -rf coverage/
    npm run test:run -- --coverage
    echo ""
    echo "========================================"
    echo "Coverage Summary"
    echo "========================================"
    node -e "
const data = require('./coverage/coverage-final.json');
let totalStmts = 0, coveredStmts = 0;
let withCoverage = [], withoutCoverage = [];

Object.entries(data).forEach(([path, file]) => {
  if (file.s) {
    const stmts = Object.values(file.s);
    const total = stmts.length;
    const covered = stmts.filter(v => v > 0).length;
    totalStmts += total;
    coveredStmts += covered;
    const relPath = path.replace('/workspace/frontend/src/', '');
    if (covered > 0) withCoverage.push({path: relPath, pct: total > 0 ? Math.round((covered/total)*100) : 0, covered, total});
    else withoutCoverage.push(relPath);
  }
});

const overall = totalStmts > 0 ? Math.round((coveredStmts/totalStmts)*100) : 0;
console.log(\`Overall: \${overall}% (\${coveredStmts}/\${totalStmts} statements)\`);
console.log('');

if (withCoverage.length > 0) {
  console.log('Files WITH coverage:');
  withCoverage.forEach(f => console.log(\`  \${f.pct}% - \${f.path} (\${f.covered}/\${f.total})\`));
  console.log('');
}

console.log(\`Files WITHOUT coverage (\${withoutCoverage.length} total):\`);
withoutCoverage.slice(0, 10).forEach(f => console.log(\`  - \${f}\`));
if (withoutCoverage.length > 10) console.log(\`  ... and \${withoutCoverage.length - 10} more\`);
"
    echo ""
    echo "Full HTML report: frontend/coverage/index.html"
else
    npm run test:run
    echo ""
    echo "Tip: Use --coverage for detailed coverage report"
fi

echo "================================"
echo "Tests complete"
