# Copyright (c) 2026, Ariful Islam and contributors
# For license information, please see license.txt

"""Server-side tests for the Afintrix desk shell.

Covers the pieces the desk sidebar and top bar depend on: icon resolution,
workspace grouping, the sidebar context payload and the rendered template.
"""

import frappe
from frappe.tests.utils import FrappeTestCase

from afintrix_theme.events.sidebar import (
	_menu_from_desktop_pages,
	_pop_primary_action,
	_slugify,
	_user_initials,
	get_desktop_pages,
	get_sidebar_context,
	get_sidebar_html,
	resolve_icon,
)


class TestSidebarHelpers(FrappeTestCase):
	def test_slugify_lowercases_and_replaces_separators(self):
		self.assertEqual(_slugify("Shift & Attendance"), "shift-and-attendance")
		self.assertEqual(_slugify("  HR Setup "), "hr-setup")
		self.assertEqual(_slugify(None), "")

	def test_resolve_icon_prefers_a_valid_custom_icon(self):
		self.assertEqual(resolve_icon("Anything", "briefcase"), "briefcase")

	def test_resolve_icon_strips_the_line_md_prefix(self):
		self.assertEqual(resolve_icon("Anything", "line-md:person"), "person")

	def test_resolve_icon_ignores_placeholder_icons(self):
		# "archive" is the stock icon the picker leaves behind; the title should win
		self.assertEqual(resolve_icon("Recruitment", "archive"), "grid-3")
		self.assertEqual(resolve_icon("Employees", "line-md:archive"), "person")

	def test_resolve_icon_falls_back_to_the_keyword_map(self):
		self.assertEqual(resolve_icon("Accounting"), "document-list")
		self.assertEqual(resolve_icon("Administration"), "cog")
		self.assertEqual(resolve_icon("Supply Chain"), "clipboard")

	def test_resolve_icon_defaults_to_grid(self):
		self.assertEqual(resolve_icon("Zzzz Unknown"), "grid-3")

	def test_user_initials(self):
		self.assertEqual(_user_initials("Ariful Islam", "a@b.com"), "AI")
		self.assertEqual(_user_initials("Cher", "cher@b.com"), "CH")
		self.assertEqual(_user_initials("", "jane@example.com"), "JA")
		self.assertEqual(_user_initials("", ""), "?")


class TestSidebarMenu(FrappeTestCase):
	def test_menu_entries_carry_a_route_and_an_icon(self):
		menu = _menu_from_desktop_pages()
		self.assertTrue(menu, "expected at least one workspace in the sidebar menu")

		for item in menu:
			self.assertTrue(item.get("title"))
			self.assertTrue(item.get("slug"))
			if item.get("is_group"):
				self.assertTrue(item["children"], f"group {item['title']} has no children")
				for child in item["children"]:
					self.assertTrue(child["route"].startswith("/app/"))
			else:
				self.assertTrue(item["route"].startswith("/app/"))

	def test_primary_action_prefers_home_and_removes_it_from_the_menu(self):
		menu = [
			{"is_group": False, "slug": "projects", "title": "Projects", "route": "/app/projects"},
			{"is_group": False, "slug": "home", "title": "Home", "route": "/app/home"},
		]
		primary = _pop_primary_action(menu)
		self.assertEqual(primary["route"], "/app/home")
		self.assertEqual([i["slug"] for i in menu], ["projects"])

	def test_primary_action_label_can_be_overridden(self):
		menu = [{"is_group": False, "slug": "home", "title": "Home", "route": "/app/home"}]
		self.assertEqual(_pop_primary_action(menu, "Dashboard")["title"], "Dashboard")

	def test_primary_action_falls_back_to_the_first_leaf(self):
		menu = [
			{"is_group": True, "slug": "finance", "title": "Finance", "children": []},
			{"is_group": False, "slug": "projects", "title": "Projects", "route": "/app/projects"},
		]
		primary = _pop_primary_action(menu)
		self.assertEqual(primary["route"], "/app/projects")

	def test_primary_action_is_none_without_any_leaf(self):
		self.assertIsNone(_pop_primary_action([{"is_group": True, "slug": "g", "title": "G", "children": []}]))

	def test_get_desktop_pages_reports_which_branch_it_used(self):
		data = get_desktop_pages()
		self.assertIn("custom_menu", data)
		if data["custom_menu"]:
			self.assertIn("items_list", data)
		else:
			self.assertIn("pages", data)


class TestSidebarContext(FrappeTestCase):
	def test_context_has_everything_the_template_reads(self):
		context = get_sidebar_context()
		for key in (
			"menu",
			"primary_action",
			"app_logo",
			"brand_title",
			"user_fullname",
			"user_email",
			"user_abbr",
		):
			self.assertIn(key, context)

		self.assertTrue(context["brand_title"])
		self.assertTrue(context["app_logo"])

	def test_sidebar_has_no_external_help_link(self):
		# The ERPNext docs backlink was dropped; the real Help Center is Phase 3.
		self.assertNotIn("help_url", get_sidebar_context())
		self.assertNotIn("Help Center", get_sidebar_html())

	def test_rendered_sidebar_carries_the_shell_markup(self):
		html = get_sidebar_html()
		self.assertIn('id="afx-sidebar"', html)
		self.assertIn("afx-nav", html)
		self.assertIn("data-afx-collapse", html)
		self.assertIn('data-afx-theme="dark"', html)
		# search / notifications / user moved to the top bar in Phase 1
		self.assertNotIn("afx-quick", html)


class TestThemeSettings(FrappeTestCase):
	def test_brand_colours_are_stored_on_theme_settings(self):
		settings = frappe.get_cached_doc("Theme Settings")
		self.assertTrue(settings.meta.has_field("primary_color"))
		self.assertTrue(settings.meta.has_field("secondary_color"))

	def test_quick_links_table_exists_for_the_top_bar(self):
		settings = frappe.get_cached_doc("Theme Settings")
		field = settings.meta.get_field("quick_links")
		self.assertIsNotNone(field, "Theme Settings is missing the quick_links table")
		self.assertEqual(field.options, "Theme Quick Link")

	def test_quick_link_rows_expose_label_route_and_target(self):
		meta = frappe.get_meta("Theme Quick Link")
		for fieldname in ("label", "route", "open_in_new_tab"):
			self.assertIsNotNone(meta.get_field(fieldname))

	def test_boot_session_publishes_theme_settings(self):
		from afintrix_theme.events.sidebar import boot_session

		bootinfo = frappe._dict()
		boot_session(bootinfo)
		self.assertTrue(bootinfo.get("sidebar_logo"))
		self.assertIn("theme_settings", bootinfo)
