"""Phase 3 server tests: Help Center, print and email branding."""

import os

import frappe
from frappe.tests.utils import FrappeTestCase

import afintrix_theme
from afintrix_theme.events import help as help_api


def app_path(*parts):
	return os.path.join(os.path.dirname(afintrix_theme.__file__), *parts)


class TestHelpCenterApi(FrappeTestCase):
	def setUp(self):
		self.article = frappe.get_doc(
			{
				"doctype": "Help Article",
				"title": "_Test question for the theme suite",
				"category": "FAQ",
				"published": 1,
				"sort_order": 99,
				"body": "<p>_Test answer</p>",
			}
		).insert(ignore_permissions=True)

	def tearDown(self):
		frappe.delete_doc("Help Article", self.article.name, force=True, ignore_permissions=True)

	def test_faq_returns_published_articles(self):
		titles = [a.title for a in help_api.get_help_center("faq")["articles"]]
		self.assertIn(self.article.title, titles)

	def test_unpublished_articles_stay_hidden(self):
		self.article.published = 0
		self.article.save(ignore_permissions=True)
		titles = [a.title for a in help_api.get_help_center("faq")["articles"]]
		self.assertNotIn(self.article.title, titles)

	def test_index_counts_each_category(self):
		counts = help_api.get_help_center()["counts"]
		self.assertIn("faq", counts)
		self.assertGreaterEqual(counts["faq"], 1)

	def test_contact_section_reads_theme_settings(self):
		contact = help_api.get_help_center("contact")
		for key in ("support_email", "support_phone", "support_hours"):
			self.assertIn(key, contact)

	def test_support_request_needs_a_subject(self):
		with self.assertRaises(frappe.ValidationError):
			help_api.raise_support_request("   ")

	def test_support_request_creates_a_record(self):
		name = help_api.raise_support_request(
			"_Test support request", "Raised by the theme test suite."
		)
		doctype = "Issue" if frappe.db.exists("DocType", "Issue") else "ToDo"
		self.assertTrue(frappe.db.exists(doctype, name))
		frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)


class TestPhase3Assets(FrappeTestCase):
	def test_help_center_page_is_installed(self):
		self.assertTrue(frappe.db.exists("Page", "help-center"))

	def test_help_stylesheet_is_bundled(self):
		with open(app_path("public", "scss", "afintrix.bundle.scss")) as f:
			self.assertIn('@import "../css/afintrix_help";', f.read())

	def test_print_style_and_format_ship_with_the_app(self):
		self.assertTrue(frappe.db.exists("Print Style", "Afintrix"))
		self.assertTrue(frappe.db.exists("Print Format", "Afintrix Invoice"))

	def test_invoice_format_renders(self):
		invoice = frappe.get_all("Sales Invoice", filters={"docstatus": 1}, limit=1)
		if not invoice:
			self.skipTest("no submitted Sales Invoice on this site")

		html = frappe.get_print("Sales Invoice", invoice[0].name, "Afintrix Invoice")
		self.assertIn("afx-print", html)
		self.assertIn("Grand total", html)

	def test_email_css_hook_points_at_the_brand_bundle(self):
		self.assertIn("afintrix_email.bundle.css", frappe.get_hooks("email_css"))

	def test_portal_stylesheet_dropped_the_cdn_font(self):
		with open(app_path("public", "css", "afintrix_portal.css")) as f:
			css = f.read()
		self.assertNotIn("fonts.googleapis", css)
		self.assertIn("Montserrat", css)
