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


# ------------------------------------------------------------ chart colour --
#
# Chart colour is data, not code: every Dashboard Chart record carries its own
# `color`, and a multi-series chart carries one per series in `y_axis`. Frappe
# falls back to its own palette when they are blank, which is why an otherwise
# Afintrix desk still drew charts in frappe blue-and-grey.
#
#     bench --site <site> execute afintrix_theme.provision.apply_chart_palette
#     bench --site <site> execute afintrix_theme.provision.apply_chart_palette \\
#         --kwargs "{'reset': True}"
#
# `reset` clears them instead, handing the charts back to frappe. Colours are
# assigned in a stable order, so re-running is a no-op rather than a reshuffle.

#: Brand first, then hues that stay distinguishable side by side and in print.
#: Status colours stay semantic elsewhere; a chart series is not a status.
CHART_PALETTE = [
	"#1E39D6",  # Afintrix primary
	"#D5AA55",  # Afintrix gold
	"#0B7A5C",  # green
	"#5B2EA6",  # purple
	"#B7280C",  # rust
	"#127C9C",  # teal
	"#8A5A10",  # amber
	"#4B5563",  # slate
]


def _palette():
	"""The site's own primary first, so a re-branded tenant leads with its colour."""
	import frappe

	primary = frappe.db.get_single_value("Theme Settings", "primary_color")
	accent = frappe.db.get_single_value("Theme Settings", "secondary_color")

	palette = list(CHART_PALETTE)
	if primary:
		palette = [primary] + [c for c in palette if c.lower() != primary.lower()]
	if accent:
		rest = [c for c in palette[1:] if c.lower() != accent.lower()]
		palette = [palette[0], accent] + rest
	return palette


def _set_custom_colours(chart, palette, index, reset):
	"""Merge (or drop) a colour list in the chart's custom_options JSON."""
	import json

	import frappe

	try:
		options = json.loads(chart.get("custom_options") or "{}")
	except ValueError:
		options = {}

	if reset:
		if "colors" not in options:
			return False
		options.pop("colors")
	else:
		colours = [palette[(index + offset) % len(palette)] for offset in range(4)]
		if options.get("colors") == colours:
			return False
		options["colors"] = colours

	chart.custom_options = json.dumps(options) if options else ""
	return True


def apply_chart_palette(reset=False, include_series=False):
	"""Paint the dashboard charts from the brand palette.

	By default this sets each chart's single `color` only. Multi-series charts
	are left alone: their series are often statuses — present, absent, on leave —
	and SPEC section 4 keeps status colour semantic rather than brand-coloured.
	Pass `include_series=True` to paint those too, for charts where the series
	are categories rather than states.
	"""
	import frappe

	frappe.set_user("Administrator")
	palette = _palette()
	touched = 0

	for index, name in enumerate(frappe.get_all("Dashboard Chart", pluck="name")):
		chart = frappe.get_doc("Dashboard Chart", name)
		colour = None if reset else palette[index % len(palette)]

		changed = False
		if (chart.color or None) != colour:
			chart.color = colour
			changed = True

		series = chart.get("y_axis") or []
		for series_index, row in enumerate(series if include_series or reset else []):
			series_colour = None if reset else palette[(index + series_index) % len(palette)]
			if (row.color or None) != series_colour:
				row.color = series_colour
				changed = True

		# A chart without y_axis rows — a report or group-by chart — draws its
		# series from frappe's own palette unless custom_options says otherwise.
		if (include_series or reset) and not series:
			if _set_custom_colours(chart, palette, index, reset):
				changed = True

		if changed:
			chart.flags.ignore_permissions = True
			chart.flags.ignore_validate = True
			chart.save(ignore_permissions=True)
			touched += 1

	frappe.db.commit()
	frappe.clear_cache()
	print({"charts": touched, "reset": bool(reset), "series": bool(include_series)})
	return touched
