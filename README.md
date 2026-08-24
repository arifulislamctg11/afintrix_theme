# Afintrix Theme

White-labels ERPNext + HRMS as an **Afintrix** product: brand tokens, desk shell, HR and module
screens, a Help Center, print and email branding, and per-tenant branding so one codebase can
dress many client sites.

Built for **Frappe v16 / ERPNext v17-develop / HRMS v17-dev**. The design source is a licensed HR
dashboard UI kit (layout language only — colours and type are Afintrix's own).

---

## What is in here

| Path | What it is |
|---|---|
| `afintrix_theme/public/css/afintrix_brand.css` | brand tokens mapped onto Frappe's variables |
| `afintrix_theme/public/js/afintrix_brand.js` | applies a site's own colours over those tokens at boot |
| `afintrix_theme/public/js/afintrix_sidebar.js` + `templates/includes/afintrix/sidebar.html` | the desk sidebar (v16) |
| `afintrix_theme/public/js/afintrix_topbar.js` | the top bar: search, notifications, user menu |
| `afintrix_theme/public/css/afintrix_components.css` | buttons, inputs, dialogs, list view, states |
| `afintrix_theme/public/css/afintrix_hr.css` + `public/js/employee_list.js` | the HR screens |
| `afintrix_theme/public/css/afintrix_modules.css` | workspace widgets, reports, trees, calendar |
| `afintrix_theme/afintrix_theme/page/help_center/` | the Help Center (the one screen built, not skinned) |
| `afintrix_theme/afintrix_theme/page/brand_studio/` | the per-tenant branding screen |
| `afintrix_theme/provision.py` | branding profiles: export, apply, reset |
| `afintrix_theme/templates/print/afintrix_print.html` | the macros every print format is built from |
| `afintrix_theme/afintrix_theme/print_style/`, `print_format/` | the Afintrix print style and six document formats |
| `afintrix_theme/public/scss/afintrix_email.bundle.scss` | transactional email styling |
| `afintrix_theme/demo/` | seed scripts: HR data, Help Center copy, letter head and print defaults |
| `scripts/new_tenant.sh` | provision a client site end to end |

Two generations of code sit side by side: the v15-era `ocean_*`, `naidapa_*` and `ki_*` files came
from the theme this app was forked from and are **inert** on v16. Work in the `afintrix_*` files.

## Assets

Desk CSS and JS are bundled by esbuild into content-hashed files
(`public/scss/afintrix.bundle.scss`, `public/js/afintrix.bundle.js`), so a rebuild always reaches
the browser. Add a stylesheet by importing it in the bundle — a server test fails if any
`afintrix_*.css` is missing from it.

The bundle entry is `.scss`, not `.css`: Frappe's postcss plugin copies a `.css` entry to a temp
directory before resolving `@import`, which breaks relative paths.

```bash
export NVM_DIR=$HOME/.nvm; . $NVM_DIR/nvm.sh; nvm use default   # frappe needs node >= 24
bench build --app afintrix_theme
```

## Configuration lives in Theme Settings

Nothing about a site's identity is hardcoded. **Theme Settings** holds the brand name, logo,
favicon, colours, sign-in copy, sidebar workspace order and grouping, top-bar quick links, support
details and the privacy text. The desk reads it at boot; `provision.py` reads and writes it.

## Tests

```bash
scripts/test.sh                      # everything, from the bench directory
```

or by hand:

```bash
for m in test_sidebar test_hr_theme test_help_center test_modules test_provision test_print; do
  bench --site <site> run-tests --module afintrix_theme.tests.$m \
    --skip-before-tests --lightmode --test-category unit
done

cd apps/afintrix_theme
npx playwright install chromium                      # once
AFX_BASE_URL=http://<host>:8000 npx playwright test  # browser tests, against a live site
```

Playwright runs against a running bench rather than a fixture site, and signs in through
`/api/method/login` rather than the sign-in form (the branded form rehydrates after load, which
makes typing into it a race).

## Demo and starter data

```bash
bench --site <site> execute afintrix_theme.demo.hr_demo.run     # employees, attendance, leave, payroll, applicants
bench --site <site> execute afintrix_theme.demo.help_demo.run   # FAQ, Getting Started, privacy text
bench --site <site> execute afintrix_theme.demo.brand_demo.run  # letter head, print style, invoice default
```

All three only create what is missing, so they are safe to re-run.

## Tenants

A tenant is a site; its identity is a **branding profile** (JSON).

```bash
# a new client, dressed from a profile
MARIADB_ROOT_USER=benchadmin MARIADB_ROOT_PASSWORD='…' \
  scripts/new_tenant.sh acme.localhost 'admin-password' tenants/example.json

# move a look between sites
bench --site a execute afintrix_theme.provision.export_profile --kwargs "{'path': '/tmp/a.json'}"
bench --site b execute afintrix_theme.provision.apply_profile  --kwargs "{'path': '/tmp/a.json'}"

# back to the house brand
bench --site b execute afintrix_theme.provision.apply_defaults
```

In the desk, the same thing is **Brand Studio** (`/app/brand-studio`, System Manager only), with a
live preview.

## Project documents

`SPEC.md`, `PROGRESS.md` and the per-phase checklists live with the client's project files, not in
this repo.
