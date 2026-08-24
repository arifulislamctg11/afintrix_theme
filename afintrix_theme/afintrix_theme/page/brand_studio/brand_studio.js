/**
 * Brand Studio — Phase 5.
 *
 * The product is sold to more than one company, so every instance needs to be
 * re-branded without a deploy. The values already live on Theme Settings; this
 * is the screen that makes changing them a five-minute job instead of a hunt
 * through a settings form: the fields that make up a tenant's identity, side by
 * side with a preview that repaints as you type, plus a way back to the house
 * brand.
 *
 * It writes through afintrix_theme.provision, which is the same code path the
 * command line provisioning uses, so a site dressed by hand and a site dressed
 * by script end up identical.
 */
frappe.pages["brand-studio"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Brand Studio"),
		single_column: true,
	});

	wrapper.afx_brand = new BrandStudio(page);
};

frappe.pages["brand-studio"].on_page_show = function (wrapper) {
	if (wrapper.afx_brand) wrapper.afx_brand.load();
};

const FIELDS = [
	{
		section: __("Identity"),
		fields: [
			{ name: "title", label: __("Brand name"), type: "Data" },
			{ name: "sidebar_text", label: __("Dashboard button label"), type: "Data" },
			{ name: "sidebar_logo", label: __("Logo"), type: "Attach" },
			{ name: "favicon_image", label: __("Favicon"), type: "Attach" },
		],
	},
	{
		section: __("Colour"),
		fields: [
			{ name: "primary_color", label: __("Primary"), type: "Color" },
			{ name: "secondary_color", label: __("Accent"), type: "Color" },
		],
	},
	{
		section: __("Sign-in page"),
		fields: [
			{ name: "login_tag", label: __("Headline"), type: "Data" },
			{ name: "login_description", label: __("Sub-heading"), type: "Small Text" },
		],
	},
	{
		section: __("Support"),
		fields: [
			{ name: "support_email", label: __("Support email"), type: "Data" },
			{ name: "support_phone", label: __("Support phone"), type: "Data" },
			{ name: "support_hours", label: __("Support hours"), type: "Data" },
		],
	},
];

class BrandStudio {
	constructor(page) {
		this.page = page;
		this.controls = {};
		this.body = $('<div class="afx-brand-studio"></div>').appendTo(this.page.main);

		this.page.set_primary_action(__("Save"), () => this.save(), "check");
		this.page.add_menu_item(__("Reset to Afintrix"), () => this.reset());
		this.page.add_menu_item(__("Export profile"), () => this.export_profile());

		this.render();
		this.load();
	}

	render() {
		this.body.empty();
		const layout = $(`<div class="afx-brand-layout">
			<div class="afx-brand-form"></div>
			<div class="afx-brand-preview"></div>
		</div>`).appendTo(this.body);

		const form = layout.find(".afx-brand-form");

		FIELDS.forEach((group) => {
			const section = $(`<section class="afx-brand-section">
				<h2>${frappe.utils.escape_html(group.section)}</h2>
			</section>`).appendTo(form);

			group.fields.forEach((field) => {
				const holder = $('<div class="afx-brand-field"></div>').appendTo(section);
				const control = frappe.ui.form.make_control({
					parent: holder,
					df: {
						fieldname: field.name,
						label: field.label,
						fieldtype: field.type,
						change: () => this.paint(),
					},
					render_input: true,
				});
				control.refresh();
				this.controls[field.name] = control;
			});
		});

		layout.find(".afx-brand-preview").append(this.preview());
	}

	preview() {
		// A miniature of the shell: enough surface for a colour decision — the
		// sidebar, the dashboard pill, a primary button, a status chip, a link.
		return $(`<div class="afx-preview-card">
			<div class="afx-preview-label">${__("Preview")}</div>
			<div class="afx-preview-shell">
				<div class="afx-preview-side">
					<div class="afx-preview-brand">
						<span class="afx-preview-logo"></span>
						<span class="afx-preview-name" data-afx-preview-name>Afintrix</span>
					</div>
					<div class="afx-preview-pill" data-afx-preview-pill>Dashboard</div>
					<div class="afx-preview-row"></div>
					<div class="afx-preview-row"></div>
					<div class="afx-preview-row"></div>
				</div>
				<div class="afx-preview-main">
					<div class="afx-preview-topbar"></div>
					<div class="afx-preview-body">
						<button class="afx-preview-btn" data-afx-preview-btn>${__("Save")}</button>
						<span class="afx-preview-chip" data-afx-preview-chip>${__("Active")}</span>
						<a class="afx-preview-link" data-afx-preview-link href="#">${__("A link")}</a>
						<div class="afx-preview-rule" data-afx-preview-rule></div>
					</div>
				</div>
			</div>
		</div>`);
	}

	load() {
		frappe.xcall("afintrix_theme.provision.get_branding").then((data) => {
			this.defaults = data.defaults || {};
			const profile = data.profile || {};
			Object.keys(this.controls).forEach((name) => {
				this.controls[name].set_value(profile[name] || "");
			});
			this.paint();
		});
	}

	values() {
		const out = {};
		Object.keys(this.controls).forEach((name) => {
			out[name] = this.controls[name].get_value() || null;
		});
		return out;
	}

	paint() {
		const values = this.values();
		const primary = values.primary_color || this.defaults?.primary_color || "#1E39D6";
		const accent = values.secondary_color || this.defaults?.secondary_color || "#D5AA55";
		const preview = this.body.find(".afx-preview-shell");

		// jQuery.css() cannot write custom properties — it goes through the
		// camel-cased style object, which drops --foo on the floor
		const shell = preview.get(0);
		if (shell) {
			shell.style.setProperty("--afx-preview-primary", primary);
			shell.style.setProperty("--afx-preview-accent", accent);
		}
		preview.find("[data-afx-preview-name]").text(values.title || this.defaults?.title || "Afintrix");
		preview
			.find("[data-afx-preview-pill]")
			.text(values.sidebar_text || this.defaults?.sidebar_text || "Dashboard");

		const logo = values.sidebar_logo;
		const mark = preview.find(".afx-preview-logo");
		mark.css("background-image", logo ? `url("${encodeURI(logo)}")` : "");
		mark.toggleClass("afx-preview-logo-image", !!logo);
	}

	save() {
		frappe
			.xcall("afintrix_theme.provision.save_branding", { profile: JSON.stringify(this.values()) })
			.then(() => {
				frappe.show_alert({ message: __("Branding saved"), indicator: "green" });
				// the shell reads these at boot, so the desk needs a reload to
				// pick up the logo and the name it already drew
				frappe.msgprint({
					title: __("Reload to see it everywhere"),
					message: __(
						"Colours apply immediately. The logo, brand name and favicon are drawn at load, so reload the page to see them in the sidebar and the browser tab."
					),
					primary_action: {
						label: __("Reload now"),
						action: () => window.location.reload(),
					},
				});
				this.apply_live(this.values());
			});
	}

	apply_live(values) {
		if (window.afintrix_brand && window.afintrix_brand.apply) {
			window.afintrix_brand.apply(values);
		}
		if (frappe.boot && frappe.boot.theme_settings) {
			Object.assign(frappe.boot.theme_settings, values);
		}
	}

	reset() {
		frappe.confirm(
			__("Put this site back to the Afintrix brand? Any tenant colours, logo and copy are replaced."),
			() => {
				frappe.xcall("afintrix_theme.provision.reset_branding").then(() => {
					frappe.show_alert({ message: __("Reset to Afintrix"), indicator: "blue" });
					this.load();
				});
			}
		);
	}

	export_profile() {
		const blob = new Blob([JSON.stringify(this.values(), null, 2)], {
			type: "application/json",
		});
		const link = document.createElement("a");
		link.href = URL.createObjectURL(blob);
		link.download = "afintrix-branding-profile.json";
		link.click();
		URL.revokeObjectURL(link.href);
	}
}
