"""Tenant provisioning — Phase 5.

The product is sold to more than one company, so a tenant is a site, and a
tenant's identity is data on that site: Theme Settings, Website Settings, the
letter head. This module is the read and write side of that identity — a
**branding profile** — so a new site can be dressed in one command and an
existing site's look can be exported, reviewed and applied elsewhere.

    bench --site <site> execute afintrix_theme.provision.apply_defaults
    bench --site <site> execute afintrix_theme.provision.export_profile \\
        --kwargs "{'path': '/tmp/tenant.json'}"
    bench --site <site> execute afintrix_theme.provision.apply_profile \\
        --kwargs "{'path': '/tmp/tenant.json'}"

Afintrix is the default: a site that sets nothing looks like Afintrix, which is
the decision recorded in SPEC section 8.
"""

import json
import os

import frappe

#: The house brand. A tenant overrides what it cares about and inherits the rest.
AFINTRIX_DEFAULTS = {
	"title": "Afintrix",
	"sidebar_text": "Dashboard",
	# the logo that ships with the app, so a reset never leaves a site with no
	# mark at all — a tenant that uploaded its own gets that path instead
	"sidebar_logo": "/assets/afintrix_theme/images/logo.png",
	"favicon_image": "/assets/afintrix_theme/images/logo.png",
	"primary_color": "#1E39D6",
	"secondary_color": "#D5AA55",
	"login_tag": "Advisory and analytics, in one workspace.",
	"login_description": "Sign in to reach your reports, records and day-to-day operations.",
	"support_email": "support@afintrix.com",
	"support_phone": "",
	"support_hours": "Sunday to Thursday, 09:00 - 18:00",
}

#: What a branding profile carries. Everything else on Theme Settings is
#: per-site configuration (workspace order, quick links), not identity.
PROFILE_FIELDS = [
	"title",
	"sidebar_text",
	"sidebar_logo",
	"favicon_image",
	"primary_color",
	"secondary_color",
	"login_tag",
	"login_description",
	"short_notes",
	"support_email",
	"support_phone",
	"support_hours",
	"privacy_policy",
]


def _settings():
	return frappe.get_single("Theme Settings")


def get_profile():
	"""The current site's branding, as a plain dict."""
	settings = _settings()
	return {field: settings.get(field) or None for field in PROFILE_FIELDS}


def export_profile(path=None):
	"""Write the current site's branding to JSON (and return it)."""
	profile = get_profile()
	if path:
		with open(path, "w") as f:
			json.dump(profile, f, indent=2, sort_keys=True)
		print(f"wrote {path}")
	else:
		print(json.dumps(profile, indent=2, sort_keys=True))
	return profile


def _read(profile=None, path=None):
	if profile and path:
		frappe.throw("Pass a profile or a path, not both.")

	if path:
		if not os.path.isfile(path):
			frappe.throw(f"No branding profile at {path}")
		with open(path) as f:
			profile = json.load(f)

	if isinstance(profile, str):
		profile = json.loads(profile)

	if not isinstance(profile, dict):
		frappe.throw("A branding profile must be a JSON object.")

	unknown = sorted(set(profile) - set(PROFILE_FIELDS))
	if unknown:
		frappe.throw(f"Unknown branding fields: {', '.join(unknown)}")

	return profile


def apply_profile(profile=None, path=None, reset_missing=False):
	"""Write a branding profile onto this site.

	`reset_missing` puts any field the profile leaves out back to the Afintrix
	default, which is what "reset this tenant to the house brand" means; without
	it a profile is a patch and unlisted fields are left alone.
	"""
	frappe.set_user("Administrator")
	profile = _read(profile=profile, path=path)
	settings = _settings()

	for field in PROFILE_FIELDS:
		if field in profile:
			settings.set(field, profile[field])
		elif reset_missing:
			settings.set(field, AFINTRIX_DEFAULTS.get(field))

	settings.save(ignore_permissions=True)
	_sync_website_identity(settings)
	frappe.db.commit()
	frappe.clear_cache()

	applied = {f: settings.get(f) for f in PROFILE_FIELDS if settings.get(f)}
	print({"applied": sorted(applied)})
	return applied


def apply_defaults():
	"""Put this site back to the house brand."""
	return apply_profile(profile=dict(AFINTRIX_DEFAULTS), reset_missing=True)


def _sync_website_identity(settings):
	"""Identity that lives outside Theme Settings but has to agree with it.

	The desk reads Theme Settings, but the browser tab, the portal header and
	the login page read Website Settings, so a tenant that changed only Theme
	Settings would still show the previous brand in a browser tab.
	"""
	website = frappe.get_single("Website Settings")
	changed = False

	if settings.get("title") and website.app_name != settings.title:
		website.app_name = settings.title
		changed = True

	logo = settings.get("sidebar_logo")
	if logo and website.app_logo != logo:
		website.app_logo = logo
		changed = True

	favicon = settings.get("favicon_image") or logo
	if favicon and website.favicon != favicon:
		website.favicon = favicon
		changed = True

	if changed:
		website.save(ignore_permissions=True)

	return changed


# ---------------------------------------------------------------- desk API --

def _guard():
	"""Branding is tenant identity, so writing it is a System Manager job."""
	if "System Manager" not in frappe.get_roles():
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)


@frappe.whitelist()
def get_branding():
	"""Brand Studio's read: the profile plus the house defaults to compare against."""
	_guard()
	return {"profile": get_profile(), "defaults": dict(AFINTRIX_DEFAULTS)}


@frappe.whitelist()
def save_branding(profile):
	_guard()
	return apply_profile(profile=profile)


@frappe.whitelist()
def reset_branding():
	_guard()
	return apply_defaults()
