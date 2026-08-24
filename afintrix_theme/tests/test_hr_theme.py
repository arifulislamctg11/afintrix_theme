"""Phase 2 wiring tests.

The HR work is CSS and a list-view patch, so what is worth asserting is that the
assets exist and are actually reachable from hooks — a stylesheet that is never
imported is the failure mode that looks fine in the editor and does nothing on
the site. The demo seed's pure helpers are covered here too; the parts that
write records are exercised by running the seed, not by the test suite.
"""

import os

import frappe
from frappe.tests.utils import FrappeTestCase

import afintrix_theme
from afintrix_theme.demo import hr_demo


def app_path(*parts):
	return os.path.join(os.path.dirname(afintrix_theme.__file__), *parts)


class TestPhase2Assets(FrappeTestCase):
	def test_hr_stylesheet_exists(self):
		self.assertTrue(os.path.isfile(app_path("public", "css", "afintrix_hr.css")))

	def test_hr_stylesheet_is_in_the_bundle(self):
		with open(app_path("public", "scss", "afintrix.bundle.scss")) as f:
			bundle = f.read()
		self.assertIn('@import "../css/afintrix_hr";', bundle)

	def test_kanban_script_is_in_the_bundle(self):
		with open(app_path("public", "js", "afintrix.bundle.js")) as f:
			bundle = f.read()
		self.assertIn('import "./afintrix_kanban.js";', bundle)

	def test_employee_list_script_is_wired_through_hooks(self):
		hooks = frappe.get_hooks("doctype_list_js")
		self.assertIn("Employee", hooks)
		paths = hooks["Employee"]
		self.assertTrue(
			any("employee_list.js" in path for path in paths),
			f"Employee list js missing from doctype_list_js: {paths}",
		)
		self.assertTrue(os.path.isfile(app_path("public", "js", "employee_list.js")))

	def test_employee_list_script_extends_rather_than_replaces(self):
		"""ERPNext's own settings must survive — the file is loaded after theirs."""
		with open(app_path("public", "js", "employee_list.js")) as f:
			source = f.read()
		self.assertIn('frappe.listview_settings["Employee"] =', source)
		self.assertIn('frappe.listview_settings["Employee"] || {}', source)


class TestHRDemoHelpers(FrappeTestCase):
	def test_people_carry_the_statuses_the_screens_need(self):
		statuses = {row[5] for row in hr_demo.PEOPLE}
		self.assertIn("Active", statuses)
		self.assertIn("Left", statuses)
		self.assertIn("Suspended", statuses)

	def test_people_rows_are_complete(self):
		for row in hr_demo.PEOPLE:
			self.assertEqual(len(row), 6, f"malformed demo row: {row}")
			self.assertTrue(all(str(value).strip() for value in row))

	def test_department_lookup_returns_none_when_missing(self):
		self.assertIsNone(hr_demo._department("No Such Department"))

	def test_demo_targets_the_demo_company(self):
		self.assertEqual(hr_demo.COMPANY, "Afintrix (Demo)")
