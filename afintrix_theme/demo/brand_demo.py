"""Site data that makes the Phase 3 branding actually apply.

The print style, print format and email styles ship in the app, but three
settings decide whether a site uses them, and settings are data, not code:

    bench --site <site> execute afintrix_theme.demo.brand_demo.run

It is safe to re-run; it only fills in what is unset.
"""

import frappe

LETTER_HEAD = "Afintrix"


def _logo():
	settings = frappe.get_cached_doc("Theme Settings")
	return (
		settings.get("sidebar_logo")
		or frappe.get_website_settings("app_logo")
		or "/assets/afintrix_theme/images/logo.png"
	)


def letter_head():
	"""Logo on the left, company name on the right, gold rule underneath."""
	brand = frappe.db.get_single_value("Theme Settings", "title") or "Afintrix"
	content = f"""<div style="display:flex;align-items:center;justify-content:space-between;
	border-bottom:3px solid #D5AA55;padding-bottom:10px;">
	<img src="{_logo()}" style="height:34px">
	<div style="font-family:Montserrat,Arial,sans-serif;font-weight:700;color:#1E39D6;font-size:15px">
		{frappe.utils.escape_html(brand)}
	</div>
</div>"""

	footer = """<div style="font-family:Montserrat,Arial,sans-serif;color:#8d96a8;font-size:10px;
	border-top:1px solid #e4e8ef;padding-top:6px;text-align:center">
	Afintrix Advisory Analytics
</div>"""

	if frappe.db.exists("Letter Head", LETTER_HEAD):
		doc = frappe.get_doc("Letter Head", LETTER_HEAD)
	else:
		doc = frappe.new_doc("Letter Head")
		doc.letter_head_name = LETTER_HEAD

	doc.source = "HTML"
	doc.content = content
	doc.footer_source = "HTML"
	doc.footer = footer
	doc.is_default = 1
	doc.disabled = 0
	doc.save(ignore_permissions=True)
	return doc.name


def print_settings():
	settings = frappe.get_single("Print Settings")
	changed = False
	if settings.print_style != "Afintrix":
		settings.print_style = "Afintrix"
		changed = True
	if changed:
		settings.save(ignore_permissions=True)
	return changed


def default_invoice_format():
	"""Make the branded format the one Sales Invoice offers first."""
	if not frappe.db.exists("Print Format", "Afintrix Invoice"):
		return False

	# ERPNext ships its own default here, so this replaces rather than skips —
	# but it leaves the setting alone once it already points at the brand format
	current = frappe.db.get_value(
		"Property Setter",
		{"doc_type": "Sales Invoice", "property": "default_print_format"},
		"value",
	)
	if current == "Afintrix Invoice":
		return False

	name = "Sales Invoice-main-default_print_format"
	if frappe.db.exists("Property Setter", name):
		frappe.db.set_value("Property Setter", name, "value", "Afintrix Invoice")
	else:
		frappe.make_property_setter(
			{
				"doctype": "Sales Invoice",
				"doctype_or_field": "DocType",
				"property": "default_print_format",
				"value": "Afintrix Invoice",
				"property_type": "Data",
			},
			ignore_validate=True,
		)
	frappe.clear_cache(doctype="Sales Invoice")
	return True


def run():
	frappe.set_user("Administrator")
	result = {
		"letter_head": letter_head(),
		"print_style_set": print_settings(),
		"invoice_format_default": default_invoice_format(),
	}
	frappe.db.commit()
	print(result)
	return result
