"""Starter Help Center content — Phase 3.

The Help Center is built from Help Article rows and Theme Settings, so an empty
site shows empty pages. This writes a first pass of copy for the client to edit
in place; like the HR seed, it only creates what is missing.

    bench --site <site> execute afintrix_theme.demo.help_demo.run
"""

import frappe

FAQ = [
	(
		"What is Afintrix?",
		"Afintrix is an advisory and analytics workspace: your reports, records and "
		"day-to-day operations in one place, built on ERPNext.",
	),
	(
		"How do I reset my password?",
		"Open the sign-in page and choose <b>Forgot Password</b>. A reset link is sent "
		"to the email address registered with your organisation.",
	),
	(
		"Who can see my data?",
		"Access follows the roles your administrator assigns. A colleague only sees a "
		"record if their role grants it, and every change is recorded against the user "
		"who made it.",
	),
	(
		"How do I export a report?",
		"Open any report and use the <b>Menu</b> in the top right, then <b>Export</b>. "
		"Excel and CSV are both available.",
	),
	(
		"Can I use Afintrix on a phone?",
		"Yes. The workspace is responsive: the navigation collapses to a drawer and the "
		"tables scroll sideways rather than shrinking to nothing.",
	),
]

GETTING_STARTED = [
	(
		"Find your way around",
		"The left sidebar groups the workspaces you have access to. The bar along the "
		"top carries search, notifications and your account menu. Press "
		"<kbd>Ctrl/⌘ + K</kbd> anywhere to jump to a record.",
	),
	(
		"Create your first record",
		"Open a list — Sales Invoice, Employee, anything — and use the blue "
		"<b>Add</b> button. Required fields carry a red asterisk; the record saves with "
		"<kbd>Ctrl/⌘ + S</kbd>.",
	),
	(
		"Set up your profile",
		"Choose your avatar in the top right, then <b>My Profile</b>, to set your photo, "
		"time zone and notification preferences.",
	),
]

PRIVACY = """<p>Afintrix Advisory Analytics processes the data you enter into this workspace on
behalf of your organisation. This page is a placeholder that your administrator should replace
with your own policy text, in <b>Theme Settings › Help Center › Privacy Policy</b>.</p>
<h3>What is stored</h3>
<p>Records you create, the files you attach, and an audit trail of who changed what and when.</p>
<h3>Who can see it</h3>
<p>Access is governed by the roles your administrator assigns. Support staff access the system
only when you ask them to.</p>
<h3>Retention</h3>
<p>Data is kept for as long as your organisation's agreement requires, and removed on request
subject to statutory retention periods.</p>"""


def _article(title, body, category, order, icon=None):
	if frappe.db.exists("Help Article", title):
		return False

	frappe.get_doc(
		{
			"doctype": "Help Article",
			"title": title,
			"category": category,
			"published": 1,
			"sort_order": order,
			"icon": icon,
			"body": body,
		}
	).insert(ignore_permissions=True)
	return True


def run():
	frappe.set_user("Administrator")
	made = 0

	for index, (title, body) in enumerate(FAQ):
		made += bool(_article(title, body, "FAQ", index))

	for index, (title, body) in enumerate(GETTING_STARTED):
		made += bool(_article(title, body, "Getting Started", index))

	settings = frappe.get_doc("Theme Settings")
	changed = False
	if not settings.get("privacy_policy"):
		settings.privacy_policy = PRIVACY
		changed = True
	if not settings.get("support_email"):
		settings.support_email = "support@afintrix.com"
		changed = True
	if not settings.get("support_phone"):
		settings.support_phone = "+880 1700 000000"
		changed = True
	if not settings.get("support_hours"):
		settings.support_hours = "Sunday to Thursday, 09:00 - 18:00"
		changed = True
	if changed:
		settings.save(ignore_permissions=True)

	frappe.db.commit()
	print({"articles": made, "settings_updated": changed})
	return {"articles": made, "settings_updated": changed}
