/**
 * Help Center — Phase 3, frames 131 to 135.
 *
 * ERPNext has no help centre of its own, so this is one of the two screens the
 * spec allows to be built rather than skinned. One page serves all five frames
 * through the route: /app/help-center, then /faq, /privacy, /shortcuts and
 * /contact. Content comes from Help Article rows and Theme Settings, so the
 * client edits the copy without a deploy.
 */
frappe.pages["help-center"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Help Center"),
		single_column: true,
	});

	wrapper.afx_help = new HelpCenter(page);
};

frappe.pages["help-center"].on_page_show = function (wrapper) {
	if (wrapper.afx_help) wrapper.afx_help.render();
};

const SECTIONS = {
	faq: { title: __("Frequently Asked Questions"), category: "FAQ" },
	"getting-started": { title: __("Getting Started"), category: "Getting Started" },
	privacy: { title: __("Privacy Policy") },
	shortcuts: { title: __("Keyboard Shortcuts") },
	contact: { title: __("Contact Support") },
};

class HelpCenter {
	constructor(page) {
		this.page = page;
		this.body = $('<div class="afx-help"></div>').appendTo(this.page.main);
		this.render();
	}

	get section() {
		const route = frappe.get_route();
		return route[1] || "";
	}

	render() {
		const section = this.section;
		// on_page_load and on_page_show both fire on a cold open; without this the
		// two async renders both append and the page draws its header twice
		if (this.rendering === section) return;
		this.rendering = section;

		frappe.call({
			method: "afintrix_theme.events.help.get_help_center",
			args: { section: section },
			callback: (r) => {
				const data = (r && r.message) || {};
				this.page.set_title(SECTIONS[section] ? SECTIONS[section].title : __("Help Center"));
				this.body.empty();
				this.body.append(this.header(section, data));

				if (!section) this.body.append(this.index(data));
				else if (section === "shortcuts") this.body.append(this.shortcuts());
				else if (section === "contact") this.body.append(this.contact(data));
				else if (section === "privacy") this.body.append(this.document(data.privacy_policy));
				else this.body.append(this.articles(data.articles || []));
			},
			always: () => {
				this.rendering = null;
			},
		});
	}

	header(section, data) {
		const crumb = section
			? `<a href="/app/help-center">${__("Help Center")}</a>
			   <span class="afx-help-sep">/</span><span>${SECTIONS[section].title}</span>`
			: `<span>${__("What can we help you with?")}</span>`;

		const head = $(`<div class="afx-help-head">
			<div>
				<h1 class="afx-help-title">${__("Help Center")}</h1>
				<div class="afx-help-crumb">${crumb}</div>
			</div>
			<div class="afx-help-search">
				<input type="search" class="form-control" placeholder="${__("Search what you need")}">
			</div>
		</div>`);

		const search = head.find("input");
		search.on("input", () => {
			const term = (search.val() || "").toLowerCase().trim();
			this.body.find("[data-afx-searchable]").each(function () {
				const hit = !term || $(this).text().toLowerCase().includes(term);
				$(this).toggleClass("hidden", !hit);
			});
		});

		return head;
	}

	index(data) {
		const cards = [
			{
				route: "/app/help-center/getting-started",
				icon: "line-md:person",
				title: __("Getting Started"),
				text: __("Find your way around Afintrix"),
			},
			{
				route: "/app/help-center/faq",
				icon: "line-md:question",
				title: __("FAQ"),
				text: __("Frequently asked questions"),
			},
			{
				route: "/app/help-center/shortcuts",
				icon: "line-md:computer",
				title: __("Keyboard Shortcuts"),
				text: __("Move faster with the keyboard"),
			},
			{
				route: "/app/help-center/privacy",
				icon: "line-md:document-list",
				title: __("Privacy Policy"),
				text: __("How your data is handled"),
			},
			{
				route: "/app/help-center/contact",
				icon: "line-md:phone",
				title: __("Contact Support"),
				text: __("Get help from the Afintrix team"),
			},
		];

		const grid = $('<div class="afx-help-grid"></div>');
		cards.forEach((card) => {
			const count = (data.counts || {})[card.route.split("/").pop()];
			grid.append(`<a class="afx-help-card" href="${card.route}" data-afx-searchable>
				<span class="afx-help-icon"><iconify-icon icon="${card.icon}"></iconify-icon></span>
				<span class="afx-help-card-title">${frappe.utils.escape_html(card.title)}</span>
				<span class="afx-help-card-text">${frappe.utils.escape_html(card.text)}</span>
				${count ? `<span class="afx-help-count">${count}</span>` : ""}
			</a>`);
		});
		return grid;
	}

	articles(articles) {
		if (!articles.length) {
			return $(`<div class="afx-help-empty">${__(
				"Nothing published yet. Add rows in Help Article and they appear here."
			)}</div>`);
		}

		const list = $('<div class="afx-help-articles"></div>');
		articles.forEach((article) => {
			list.append(`<article class="afx-help-article" data-afx-searchable>
				<h2>${frappe.utils.escape_html(article.title)}</h2>
				<div class="afx-help-article-body">${article.body || ""}</div>
				<div class="afx-help-article-meta">
					<iconify-icon icon="line-md:calendar"></iconify-icon>
					${__("Updated")} ${frappe.datetime.comment_when(article.modified)}
				</div>
			</article>`);
		});
		return list;
	}

	document(html) {
		if (!html) {
			return $(`<div class="afx-help-empty">${__(
				"No policy text yet. Add it in Theme Settings under Help Center."
			)}</div>`);
		}
		return $(`<div class="afx-help-doc" data-afx-searchable>${html}</div>`);
	}

	shortcuts() {
		const groups = [
			{
				title: __("Everywhere"),
				rows: [
					[__("Search anything"), "Ctrl/⌘ + K"],
					[__("New document"), "Ctrl/⌘ + B"],
					[__("Save"), "Ctrl/⌘ + S"],
					[__("Keyboard shortcut help"), "Ctrl/⌘ + /"],
				],
			},
			{
				title: __("Lists"),
				rows: [
					[__("Refresh"), "Ctrl/⌘ + R"],
					[__("Select all rows"), "Ctrl/⌘ + A"],
					[__("Next page"), "→"],
					[__("Previous page"), "←"],
				],
			},
			{
				title: __("Forms"),
				rows: [
					[__("Submit"), "Ctrl/⌘ + Enter"],
					[__("Previous record"), "Ctrl/⌘ + ↑"],
					[__("Next record"), "Ctrl/⌘ + ↓"],
					[__("Close dialog"), "Esc"],
				],
			},
		];

		const wrap = $('<div class="afx-help-shortcuts"></div>');
		groups.forEach((group) => {
			const rows = group.rows
				.map(
					(row) =>
						`<div class="afx-help-shortcut" data-afx-searchable>
							<span>${frappe.utils.escape_html(row[0])}</span>
							<kbd>${frappe.utils.escape_html(row[1])}</kbd>
						</div>`
				)
				.join("");
			wrap.append(`<section class="afx-help-shortcut-group">
				<h2>${frappe.utils.escape_html(group.title)}</h2>${rows}
			</section>`);
		});
		return wrap;
	}

	contact(data) {
		const wrap = $(`<div class="afx-help-contact">
			<section class="afx-help-contact-card" data-afx-searchable>
				<h2>${__("Talk to us")}</h2>
				<p class="afx-help-contact-line">
					<iconify-icon icon="line-md:email"></iconify-icon>
					<a href="mailto:${frappe.utils.escape_html(data.support_email || "")}">${frappe.utils.escape_html(
			data.support_email || __("Set a support email in Theme Settings")
		)}</a>
				</p>
				<p class="afx-help-contact-line">
					<iconify-icon icon="line-md:phone"></iconify-icon>
					<span>${frappe.utils.escape_html(data.support_phone || __("Set a support phone in Theme Settings"))}</span>
				</p>
				<p class="afx-help-contact-line">
					<iconify-icon icon="line-md:clock"></iconify-icon>
					<span>${frappe.utils.escape_html(data.support_hours || __("Mon to Fri, 9:00 - 18:00"))}</span>
				</p>
			</section>
			<section class="afx-help-contact-card" data-afx-searchable>
				<h2>${__("Send a request")}</h2>
				<div class="afx-help-form"></div>
			</section>
		</div>`);

		const form = wrap.find(".afx-help-form");
		const subject = $(
			`<div class="form-group"><label>${__("Subject")}</label>
			 <input type="text" class="form-control" data-afx-subject></div>`
		).appendTo(form);
		const description = $(
			`<div class="form-group"><label>${__("How can we help?")}</label>
			 <textarea class="form-control" rows="5" data-afx-description></textarea></div>`
		).appendTo(form);
		const button = $(
			`<button class="btn btn-primary">${__("Submit request")}</button>`
		).appendTo(form);

		button.on("click", () => {
			const payload = {
				subject: subject.find("input").val(),
				description: description.find("textarea").val(),
			};
			if (!payload.subject) {
				frappe.msgprint(__("Please add a subject."));
				return;
			}
			button.prop("disabled", true);
			frappe
				.xcall("afintrix_theme.events.help.raise_support_request", payload)
				.then((name) => {
					frappe.show_alert({
						message: __("Request {0} created", [name]),
						indicator: "green",
					});
					subject.find("input").val("");
					description.find("textarea").val("");
				})
				.finally(() => button.prop("disabled", false));
		});

		return wrap;
	}
}
