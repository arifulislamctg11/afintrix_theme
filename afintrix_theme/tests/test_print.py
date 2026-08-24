"""Print formats and the branded web message pages.

Every Afintrix format is a thin wrapper around the macros in
templates/print/afintrix_print.html, so the thing worth testing is that each one
still compiles against a real document of its doctype and produces the shared
markup — a Jinja typo in a format is invisible until someone tries to print.
"""

import os

import frappe
from frappe.tests.utils import FrappeTestCase

import afintrix_theme

FORMATS = {
	"Afintrix Invoice": "Sales Invoice",
	"Afintrix Sales Order": "Sales Order",
	"Afintrix Purchase Order": "Purchase Order",
	"Afintrix Delivery Note": "Delivery Note",
	"Afintrix Payment Receipt": "Payment Entry",
	"Afintrix Payslip": "Salary Slip",
}


def app_path(*parts):
	return os.path.join(os.path.dirname(afintrix_theme.__file__), *parts)


class TestPrintFormats(FrappeTestCase):
	def test_every_format_is_installed_against_its_doctype(self):
		for name, doctype in FORMATS.items():
			self.assertEqual(
				frappe.db.get_value("Print Format", name, "doc_type"),
				doctype,
				f"{name} is missing or points at the wrong doctype",
			)

	def test_every_format_compiles(self):
		"""Render each one against an empty document of its doctype."""
		for name, doctype in FORMATS.items():
			html = frappe.db.get_value("Print Format", name, "html")
			doc = frappe.new_doc(doctype)
			doc.name = "PREVIEW"
			try:
				rendered = frappe.render_template(
					html, {"doc": doc, "frappe": frappe, "_": frappe._}
				)
			except Exception as exc:  # a template error names the format
				self.fail(f"{name} failed to render: {exc}")

			self.assertIn("afx-print", rendered, f"{name} did not use the shared layout")

	def test_formats_carry_no_css_of_their_own(self):
		"""The styling belongs to the print style, which applies to every format."""
		for name in FORMATS:
			self.assertFalse(
				(frappe.db.get_value("Print Format", name, "css") or "").strip(),
				f"{name} carries its own CSS; it belongs in the Afintrix print style",
			)

	def test_the_print_style_holds_the_shared_layout(self):
		css = frappe.db.get_value("Print Style", "Afintrix", "css") or ""
		for rule in (".afx-print-head", ".afx-print-total", ".afx-print-signatures"):
			self.assertIn(rule, css)

	def test_a_real_document_prints(self):
		invoice = frappe.get_all("Sales Invoice", filters={"docstatus": 1}, limit=1)
		if not invoice:
			self.skipTest("no submitted Sales Invoice on this site")

		html = frappe.get_print("Sales Invoice", invoice[0].name, "Afintrix Invoice")
		self.assertIn("afx-print-total", html)
		self.assertIn("Grand total", html)


class TestWebMessagePages(FrappeTestCase):
	def test_the_message_page_is_ours_not_the_forked_template(self):
		with open(app_path("www", "message.html")) as f:
			template = f.read()
		self.assertIn("afx-message", template)
		self.assertIn('get_single_value("Theme Settings", "sidebar_logo")', template)
		# the teal template's badge and wave background
		self.assertNotIn("auth-logo-float", template)
		self.assertNotIn("bg-waves", template)

	def test_the_404_page_uses_the_same_card(self):
		with open(app_path("www", "404.html")) as f:
			template = f.read()
		self.assertIn('extends "afintrix_theme/www/message.html"', template)
