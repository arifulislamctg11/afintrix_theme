#!/usr/bin/env bash
#
# Run everything: the server suite on a site, then the browser suite against it.
#
#   scripts/test.sh                       # afintrix.localhost, http://localhost:8000
#   SITE=acme.localhost scripts/test.sh
#   AFX_BASE_URL=http://192.168.64.4:8000 scripts/test.sh
#
# Run it from the bench directory.
set -euo pipefail

SITE="${SITE:-afintrix.localhost}"
BASE_URL="${AFX_BASE_URL:-http://localhost:8000}"
MODULES=(test_sidebar test_hr_theme test_help_center test_modules test_provision)

if [[ ! -d "sites" ]]; then
	echo "run this from the bench directory (no ./sites here)" >&2
	exit 2
fi

if [[ -s "$HOME/.nvm/nvm.sh" ]]; then
	# shellcheck disable=SC1091
	. "$HOME/.nvm/nvm.sh"
	nvm use default >/dev/null 2>&1 || true
fi

failed=0

for module in "${MODULES[@]}"; do
	echo "==> $module"
	if ! bench --site "$SITE" run-tests --module "afintrix_theme.tests.$module" \
		--skip-before-tests --lightmode --test-category unit; then
		failed=1
	fi
done

if [[ "${SKIP_BROWSER:-}" == "1" ]]; then
	echo "==> browser tests skipped (SKIP_BROWSER=1)"
else
	echo "==> browser tests against $BASE_URL"
	if ! (cd apps/afintrix_theme && AFX_BASE_URL="$BASE_URL" npx playwright test); then
		failed=1
	fi
fi

if [[ "$failed" -ne 0 ]]; then
	echo "FAILED" >&2
	exit 1
fi

echo "all suites passed"
