"""The dashboard chart palette."""

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from afintrix_theme import provision


class TestChartPalette(FrappeTestCase):
	def setUp(self):
		self.chart = frappe.get_all("Dashboard Chart", limit=1, pluck="name")
		if not self.chart:
			self.skipTest("no dashboard charts on this site")
		self.chart = self.chart[0]
		doc = frappe.get_doc("Dashboard Chart", self.chart)
		self.original = (doc.color, doc.get("custom_options"))

	def tearDown(self):
		doc = frappe.get_doc("Dashboard Chart", self.chart)
		doc.color, doc.custom_options = self.original
		doc.flags.ignore_validate = True
		doc.save(ignore_permissions=True)
		frappe.db.commit()

	def test_the_palette_leads_with_the_site_colour(self):
		palette = provision._palette()
		primary = frappe.db.get_single_value("Theme Settings", "primary_color")
		if primary:
			self.assertEqual(palette[0].lower(), primary.lower())
		self.assertGreaterEqual(len(palette), 6)

	def test_the_palette_has_no_duplicates(self):
		palette = [c.lower() for c in provision._palette()]
		self.assertEqual(len(palette), len(set(palette)))

	def test_applying_gives_every_chart_a_colour(self):
		provision.apply_chart_palette()
		blank = frappe.get_all("Dashboard Chart", filters={"color": ["in", ["", None]]}, limit=1)
		self.assertFalse(blank, "a chart was left without a colour")

	def test_series_are_left_semantic_by_default(self):
		"""Present, absent and on leave are statuses, not brand categories."""
		provision.apply_chart_palette(reset=True)
		provision.apply_chart_palette()

		doc = frappe.get_doc("Dashboard Chart", self.chart)
		options = json.loads(doc.get("custom_options") or "{}")
		self.assertNotIn("colors", options)

	def test_series_can_be_painted_on_request(self):
		provision.apply_chart_palette(include_series=True)
		painted = 0
		for name in frappe.get_all("Dashboard Chart", limit=20, pluck="name"):
			options = json.loads(
				frappe.db.get_value("Dashboard Chart", name, "custom_options") or "{}"
			)
			painted += "colors" in options
		self.assertGreater(painted, 0)

		provision.apply_chart_palette(reset=True)
		provision.apply_chart_palette()

	def test_reset_hands_the_charts_back_to_frappe(self):
		provision.apply_chart_palette(reset=True)
		doc = frappe.get_doc("Dashboard Chart", self.chart)
		self.assertFalse(doc.color)
		provision.apply_chart_palette()
