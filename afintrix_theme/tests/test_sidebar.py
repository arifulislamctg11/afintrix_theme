# Copyright (c) 2026, Ariful Islam and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from afintrix_theme.events.sidebar import get_sidebar_html


class TestSidebarHtml(FrappeTestCase):
	def setUp(self):
		# Whitelisted calls (/api/method/...) run without a bootinfo on frappe.local,
		# unlike a desk page render. Drop it so the test reproduces that context.
		self._had_boot = hasattr(frappe.local, "boot")
		if self._had_boot:
			self._boot = frappe.local.boot
			del frappe.local.boot

		self.settings = frappe.get_single("Theme Settings")
		self._sidebar_logo = self.settings.sidebar_logo
		self.settings.db_set("sidebar_logo", None)

		self._app_logo = frappe.db.get_single_value("Website Settings", "app_logo")
		frappe.db.set_single_value("Website Settings", "app_logo", None)
		frappe.clear_cache()

	def tearDown(self):
		self.settings.db_set("sidebar_logo", self._sidebar_logo)
		frappe.db.set_single_value("Website Settings", "app_logo", self._app_logo)
		frappe.clear_cache()
		if self._had_boot:
			frappe.local.boot = self._boot

	def test_renders_without_bootinfo(self):
		"""Falls back to the app logo instead of blowing up on frappe.local.boot."""
		html = get_sidebar_html()

		self.assertIsInstance(html, str)
		self.assertNotEqual(html, "", "sidebar template rendered empty")
