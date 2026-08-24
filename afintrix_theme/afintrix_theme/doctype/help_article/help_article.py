# Copyright (c) 2026, Ariful Islam and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class HelpArticle(Document):
	"""A single Help Center entry.

	The Help Center pages are built from these rows so the client can edit the
	copy without a deploy — the kit's frames (131-135) are the layout, this is
	the content behind them.
	"""

	pass
