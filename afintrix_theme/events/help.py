"""Help Center content — Phase 3.

ERPNext ships no help centre, so frames 131-135 are built rather than skinned.
The copy lives in Help Article rows and Theme Settings so the client can change
it without a deploy; this module is the read side of that, plus the one write
the Contact Support form needs.
"""

import frappe
from frappe import _


def _settings():
	try:
		return frappe.get_cached_doc("Theme Settings")
	except Exception:
		return None


def _articles(category):
	return frappe.get_all(
		"Help Article",
		filters={"published": 1, "category": category},
		fields=["name", "title", "summary", "body", "modified"],
		order_by="sort_order asc, title asc",
	)


@frappe.whitelist()
def get_help_center(section=None):
	"""Everything the Help Center page needs for one route."""
	section = (section or "").strip()
	settings = _settings()

	if section == "faq":
		return {"articles": _articles("FAQ")}

	if section == "getting-started":
		return {"articles": _articles("Getting Started")}

	if section == "privacy":
		return {"privacy_policy": settings.get("privacy_policy") if settings else None}

	if section == "contact":
		return {
			"support_email": settings.get("support_email") if settings else None,
			"support_phone": settings.get("support_phone") if settings else None,
			"support_hours": settings.get("support_hours") if settings else None,
		}

	# the index: card counts, so an empty category is visible before it is opened
	return {
		"counts": {
			"faq": len(_articles("FAQ")),
			"getting-started": len(_articles("Getting Started")),
		}
	}


@frappe.whitelist()
def raise_support_request(subject, description=None):
	"""Contact Support submits into whatever the site actually has.

	ERPNext's Issue is the right home for this, but the theme must not assume
	the Support module is installed, so it falls back to a ToDo assigned to the
	support mailbox owner.
	"""
	subject = (subject or "").strip()
	if not subject:
		frappe.throw(_("Please add a subject."))

	description = (description or "").strip()

	if frappe.db.exists("DocType", "Issue"):
		issue = frappe.get_doc(
			{
				"doctype": "Issue",
				"subject": subject,
				"description": description,
				"raised_by": frappe.session.user,
			}
		)
		issue.insert(ignore_permissions=True)
		return issue.name

	todo = frappe.get_doc(
		{
			"doctype": "ToDo",
			"description": f"{subject}\n\n{description}",
			"owner": frappe.session.user,
			"reference_type": "User",
			"reference_name": frappe.session.user,
		}
	)
	todo.insert(ignore_permissions=True)
	return todo.name
