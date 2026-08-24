"""Phase 4 wiring tests: the module stylesheet is present and reachable."""

import os

import frappe
from frappe.tests.utils import FrappeTestCase

import afintrix_theme


def app_path(*parts):
	return os.path.join(os.path.dirname(afintrix_theme.__file__), *parts)


class TestPhase4Assets(FrappeTestCase):
	def test_module_stylesheet_exists_and_is_bundled(self):
		self.assertTrue(os.path.isfile(app_path("public", "css", "afintrix_modules.css")))
		with open(app_path("public", "scss", "afintrix.bundle.scss")) as f:
			self.assertIn('@import "../css/afintrix_modules";', f.read())

	def test_page_head_controls_are_kept_on_one_row(self):
		"""The calendar, gantt, kanban and report views pack their controls into
		the page head; a wrap there lands on the breadcrumbs."""
		with open(app_path("public", "css", "afintrix_components.css")) as f:
			css = f.read()
		self.assertIn(".sort-selector .btn-group", css)
		self.assertIn(".page-head .custom-actions", css)

	def test_number_card_order_is_pinned(self):
		"""The inherited template sets display:contents on the card's wrappers,
		which is why the value used to sit above its own label."""
		with open(app_path("public", "css", "afintrix_modules.css")) as f:
			css = f.read()
		self.assertIn(".widget.number-widget-box .widget-head", css)
		self.assertIn("order: 1", css)

	def test_kanban_counter_keeps_looking_for_a_cold_loaded_board(self):
		with open(app_path("public", "js", "afintrix_kanban.js")) as f:
			source = f.read()
		self.assertIn("watch_until_found", source)

	def test_every_theme_stylesheet_is_in_the_bundle(self):
		"""A stylesheet that is never imported is the failure that looks fine in
		the editor and does nothing on the site."""
		with open(app_path("public", "scss", "afintrix.bundle.scss")) as f:
			bundle = f.read()

		css_dir = app_path("public", "css")
		ours = [
			f
			for f in os.listdir(css_dir)
			if f.startswith("afintrix_") and f.endswith(".css") and f != "afintrix_portal.css"
		]
		missing = [f for f in ours if f'@import "../css/{f[:-4]}"' not in bundle]
		self.assertEqual(missing, [], f"stylesheets not imported by the bundle: {missing}")


class TestLegacyShellIsGone(FrappeTestCase):
	"""The v15 shell this app was forked from.

	`www/app.html` replaced frappe's desk page and wrapped it in an "ocean"
	sidebar and navbar that the theme then hid with CSS. On v16 `/app` redirects
	to `/desk`, so that page was already dead — it just left a hidden second
	shell in every DOM. It and its assets are removed; these tests keep them
	from coming back with a stray include.
	"""

	def test_the_desk_page_override_is_gone(self):
		for name in ("app.html", "app.py"):
			self.assertFalse(
				os.path.exists(app_path("www", name)),
				f"www/{name} is back; the desk shell belongs to frappe",
			)

	def test_the_ocean_templates_are_gone(self):
		self.assertFalse(os.path.isdir(app_path("templates", "includes", "ocean")))

	def test_no_dead_stylesheet_is_still_included(self):
		hooks_css = frappe.get_hooks("app_include_css") + frappe.get_hooks("web_include_css")
		hooks_js = frappe.get_hooks("app_include_js") + frappe.get_hooks("web_include_js")
		for asset in hooks_css + hooks_js:
			if not asset.startswith("/assets/afintrix_theme/"):
				continue
			relative = asset.replace("/assets/afintrix_theme/", "")
			self.assertTrue(
				os.path.exists(app_path("public", *relative.split("/"))),
				f"hooks include a file that does not exist: {asset}",
			)
