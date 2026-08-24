/**
 * Employee list — Phase 2.
 *
 * Frame 19 of the kit shows each employee as an avatar with their name over
 * their email address. ERPNext's own employee_list.js already sets the fields,
 * filters and status colours; this file is loaded after it through the
 * doctype_list_js hook and extends that object in place, so the Import
 * Employees button and the status indicator survive.
 *
 * The email line is added to the rendered subject element rather than through
 * settings.formatters: the subject formatter's return value goes through a
 * text node, so markup would be shown as text.
 */
(function () {
	"use strict";

	const settings = (frappe.listview_settings["Employee"] =
		frappe.listview_settings["Employee"] || {});

	const wanted = ["employee_name", "personal_email", "company_email", "user_id"];
	const fields = settings.add_fields || [];
	settings.add_fields = fields.concat(wanted.filter((f) => !fields.includes(f)));

	function email_of(doc) {
		return doc.company_email || doc.personal_email || doc.user_id || "";
	}

	const previous_onload = settings.onload;

	settings.onload = function (list_view) {
		if (previous_onload) previous_onload.call(this, list_view);
		if (list_view.__afx_subject_patched) return;
		list_view.__afx_subject_patched = true;

		const original = list_view.get_subject_element.bind(list_view);

		list_view.get_subject_element = function (doc, title) {
			const element = original(doc, title);
			const email = email_of(doc || {});
			const link = element.querySelector("a");
			if (!email || !link) return element;

			const name_text = link.textContent;
			link.textContent = "";

			// employees rarely have a photo, and the kit still shows a disc, so
			// fall back to frappe's initials avatar
			if (!element.querySelector(".avatar")) {
				const avatar = document.createElement("span");
				avatar.innerHTML = frappe.get_avatar(
					"avatar avatar-medium",
					doc.employee_name || doc.name,
					doc.image || null
				);
				const disc = avatar.firstElementChild;
				if (disc) link.parentElement.insertBefore(disc, link);
			}

			const stack = document.createElement("span");
			stack.className = "afx-person";

			const name = document.createElement("span");
			name.className = "afx-person-name";
			name.textContent = name_text;

			const mail = document.createElement("span");
			mail.className = "afx-person-mail";
			mail.textContent = email;

			stack.appendChild(name);
			stack.appendChild(mail);
			link.appendChild(stack);
			return element;
		};
	};
})();
