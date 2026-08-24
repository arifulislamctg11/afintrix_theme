#!/usr/bin/env bash
#
# Provision a tenant — Phase 5.
#
# A tenant is a site: its own database, its own users, its own branding. This
# creates one, installs the product on it, and dresses it from a branding
# profile (the same JSON afintrix_theme.provision exports), so a new client is
# one command rather than a checklist.
#
#   scripts/new_tenant.sh northwind.localhost 'admin-password' tenants/northwind.json
#
# The profile argument is optional; without it the site comes up in the house
# brand, which is the documented default.
#
# Run it from the bench directory. MariaDB credentials come from the
# environment so nothing secret lives in the repo:
#
#   MARIADB_ROOT_USER=benchadmin MARIADB_ROOT_PASSWORD=... scripts/new_tenant.sh ...
#
set -euo pipefail

SITE="${1:-}"
ADMIN_PASSWORD="${2:-}"
PROFILE="${3:-}"

if [[ -z "$SITE" || -z "$ADMIN_PASSWORD" ]]; then
	echo "usage: $0 <site> <admin-password> [branding-profile.json]" >&2
	exit 2
fi

if [[ ! -d "sites" ]]; then
	echo "run this from the bench directory (no ./sites here)" >&2
	exit 2
fi

MARIADB_ROOT_USER="${MARIADB_ROOT_USER:-benchadmin}"
APPS="${APPS:-erpnext hrms afintrix_theme}"

# frappe needs node >= 24 and a non-interactive shell can resolve an older one
if [[ -s "$HOME/.nvm/nvm.sh" ]]; then
	# shellcheck disable=SC1091
	. "$HOME/.nvm/nvm.sh"
	nvm use default >/dev/null 2>&1 || true
fi

echo "==> creating $SITE"
new_site_args=(new-site "$SITE" --admin-password "$ADMIN_PASSWORD" --mariadb-root-username "$MARIADB_ROOT_USER")
if [[ -n "${MARIADB_ROOT_PASSWORD:-}" ]]; then
	new_site_args+=(--mariadb-root-password "$MARIADB_ROOT_PASSWORD")
fi
bench "${new_site_args[@]}"

for app in $APPS; do
	echo "==> installing $app"
	bench --site "$SITE" install-app "$app"
done

echo "==> migrating"
bench --site "$SITE" migrate

if [[ -n "$PROFILE" ]]; then
	if [[ ! -f "$PROFILE" ]]; then
		echo "no branding profile at $PROFILE" >&2
		exit 1
	fi
	echo "==> applying branding from $PROFILE"
	bench --site "$SITE" execute afintrix_theme.provision.apply_profile \
		--kwargs "{'path': '$(readlink -f "$PROFILE")', 'reset_missing': True}"
else
	echo "==> applying the Afintrix defaults"
	bench --site "$SITE" execute afintrix_theme.provision.apply_defaults
fi

echo "==> letter head, print style and print defaults"
bench --site "$SITE" execute afintrix_theme.demo.brand_demo.run

echo "==> building assets"
bench build --app afintrix_theme

cat <<INFO

$SITE is ready.

  Sign in     administrator / (the password you passed)
  Re-brand    Desk › Brand Studio, or
              bench --site $SITE execute afintrix_theme.provision.apply_profile --kwargs "{'path': '...'}"
  Export      bench --site $SITE execute afintrix_theme.provision.export_profile --kwargs "{'path': '...'}"
  Remove      bench drop-site $SITE --mariadb-root-username $MARIADB_ROOT_USER

INFO
