"""Phase 5: tenant branding profiles.

Every test here writes to Theme Settings, which is the live look of the site the
suite runs on, so each one snapshots the profile first and puts it back after.
"""

import json
import os
import tempfile

import frappe
from frappe.tests.utils import FrappeTestCase

import afintrix_theme
from afintrix_theme import provision


def app_path(*parts):
	return os.path.join(os.path.dirname(afintrix_theme.__file__), *parts)


class TestBrandingProfile(FrappeTestCase):
	def setUp(self):
		self.snapshot = provision.get_profile()

	def tearDown(self):
		provision.apply_profile(profile=self.snapshot, reset_missing=True)

	def test_profile_carries_identity_not_configuration(self):
		for field in ("title", "primary_color", "secondary_color", "sidebar_logo"):
			self.assertIn(field, provision.PROFILE_FIELDS)
		# workspace order and quick links are per-site setup, not brand identity
		for field in ("workspace_order", "quick_links"):
			self.assertNotIn(field, provision.PROFILE_FIELDS)

	def test_get_profile_answers_every_field(self):
		profile = provision.get_profile()
		self.assertEqual(sorted(profile), sorted(provision.PROFILE_FIELDS))

	def test_apply_profile_is_a_patch_by_default(self):
		provision.apply_profile(profile={"title": "_Test Tenant"})
		self.assertEqual(frappe.db.get_single_value("Theme Settings", "title"), "_Test Tenant")
		# a field the profile did not mention is left alone
		self.assertEqual(
			frappe.db.get_single_value("Theme Settings", "primary_color"),
			self.snapshot["primary_color"],
		)

	def test_reset_missing_puts_unlisted_fields_back_to_the_house_brand(self):
		provision.apply_profile(profile={"title": "_Test Tenant"}, reset_missing=True)
		self.assertEqual(
			frappe.db.get_single_value("Theme Settings", "primary_color"),
			provision.AFINTRIX_DEFAULTS["primary_color"],
		)

	def test_unknown_fields_are_refused(self):
		with self.assertRaises(frappe.ValidationError):
			provision.apply_profile(profile={"favourite_colour": "blue"})

	def test_apply_defaults_restores_the_house_brand(self):
		provision.apply_profile(profile={"title": "_Test Tenant", "primary_color": "#0B7A5C"})
		provision.apply_defaults()
		self.assertEqual(
			frappe.db.get_single_value("Theme Settings", "title"),
			provision.AFINTRIX_DEFAULTS["title"],
		)
		self.assertEqual(
			frappe.db.get_single_value("Theme Settings", "primary_color"),
			provision.AFINTRIX_DEFAULTS["primary_color"],
		)

	def test_export_and_apply_round_trip(self):
		with tempfile.TemporaryDirectory() as tmp:
			path = os.path.join(tmp, "tenant.json")
			provision.export_profile(path)

			with open(path) as f:
				written = json.load(f)
			self.assertEqual(written["title"], self.snapshot["title"])

			provision.apply_profile(profile={"title": "_Test Tenant"})
			provision.apply_profile(path=path, reset_missing=True)

		self.assertEqual(
			frappe.db.get_single_value("Theme Settings", "title"), self.snapshot["title"]
		)

	def test_website_identity_follows_the_brand(self):
		"""The desk reads Theme Settings; the browser tab reads Website Settings."""
		provision.apply_profile(profile={"title": "_Test Tenant"})
		self.assertEqual(frappe.db.get_single_value("Website Settings", "app_name"), "_Test Tenant")

	def test_a_profile_path_that_does_not_exist_is_an_error(self):
		with self.assertRaises(frappe.ValidationError):
			provision.apply_profile(path="/tmp/definitely-not-a-branding-profile.json")


class TestBrandStudioAssets(FrappeTestCase):
	def test_page_is_installed_and_restricted(self):
		self.assertTrue(frappe.db.exists("Page", "brand-studio"))
		roles = frappe.get_all("Has Role", filters={"parent": "brand-studio"}, pluck="role")
		self.assertIn("System Manager", roles)

	def test_the_sign_in_page_reads_the_tenant_headline(self):
		"""Brand Studio offers a headline; the login page has to use it."""
		with open(app_path("www", "login.html")) as f:
			template = f.read()
		self.assertIn('get_single_value("Theme Settings", "login_tag")', template)
		self.assertIn("theme_headline or", template)

	def test_the_letter_head_is_named_after_the_tenant(self):
		with open(app_path("demo", "brand_demo.py")) as f:
			source = f.read()
		self.assertIn("DEFAULT_LETTER_HEAD", source)
		self.assertIn('frappe.db.get_single_value("Theme Settings", "title")', source)

	def test_stylesheet_is_bundled(self):
		with open(app_path("public", "scss", "afintrix.bundle.scss")) as f:
			self.assertIn('@import "../css/afintrix_brand_studio";', f.read())

	def test_provisioning_script_ships_with_the_app(self):
		# app_path() is <repo>/afintrix_theme; the script sits at the repo root
		repo = os.path.dirname(os.path.dirname(afintrix_theme.__file__))
		script = os.path.join(repo, "scripts", "new_tenant.sh")
		self.assertTrue(os.path.isfile(script), script)
		with open(script) as f:
			body = f.read()
		self.assertIn("afintrix_theme.provision.apply_profile", body)
		self.assertIn("bench new-site", body.replace("bench \"${new_site_args[@]}\"", "bench new-site"))
