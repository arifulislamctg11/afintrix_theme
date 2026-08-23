/**
 * Afintrix desk sidebar (Frappe v16).
 *
 * Renders the Jinja template afintrix_theme/templates/includes/afintrix/sidebar.html
 * next to the native desk sidebar, then takes the native one out of the layout.
 * The native sidebar stays in the DOM on purpose: its JS still owns search,
 * notifications and the user menu, which this sidebar triggers by proxy.
 */
(function () {
	"use strict";

	const COLLAPSE_KEY = "afintrix.sidebar.collapsed";
	const GROUP_KEY = "afintrix.sidebar.groups";
	const MOBILE_BREAKPOINT = 991;

	let injecting = false;

	function is_desk() {
		return !!(window.frappe && frappe.boot && document.querySelector(".main-section"));
	}

	function is_mobile() {
		return window.innerWidth <= MOBILE_BREAKPOINT;
	}

	function read_groups() {
		try {
			return JSON.parse(localStorage.getItem(GROUP_KEY) || "{}");
		} catch (e) {
			return {};
		}
	}

	function write_group(slug, expanded) {
		const state = read_groups();
		state[slug] = expanded;
		try {
			localStorage.setItem(GROUP_KEY, JSON.stringify(state));
		} catch (e) {
			/* storage disabled — collapse state just won't persist */
		}
	}

	function inject() {
		if (!is_desk() || injecting) return;
		if (document.getElementById("afx-sidebar")) return;

		injecting = true;
		frappe.call({
			method: "afintrix_theme.events.sidebar.get_sidebar_html",
			callback: function (r) {
				injecting = false;
				if (!r || !r.message) return;
				if (document.getElementById("afx-sidebar")) return;

				const holder = document.createElement("div");
				holder.innerHTML = r.message.trim();
				const nav = holder.firstElementChild;
				if (!nav) return;

				const main = document.querySelector(".main-section");
				document.body.insertBefore(nav, main);

				if (!document.querySelector(".afx-scrim")) {
					const scrim = document.createElement("div");
					scrim.className = "afx-scrim";
					scrim.addEventListener("click", () =>
						document.body.classList.remove("afx-sidebar-open")
					);
					document.body.insertBefore(scrim, main);
				}

				add_mobile_toggle();
				document.body.classList.add("afx-sidebar-on");
				if (localStorage.getItem(COLLAPSE_KEY) === "true" && !is_mobile()) {
					document.body.classList.add("afx-collapsed");
				}

				drop_legacy_navbar_buttons();
				set_kbd_hint(nav);
				restore_groups(nav);
				bind(nav);
				highlight();
				sync_theme_buttons();
				watch_notification_count();
			},
			error: function () {
				injecting = false;
			},
		});
	}

	// Off-canvas opener for narrow screens; the desk header has no room for one.
	function add_mobile_toggle() {
		if (document.querySelector(".afx-mobile-toggle")) return;
		const btn = document.createElement("button");
		btn.type = "button";
		btn.className = "afx-mobile-toggle";
		btn.setAttribute("aria-label", "Open navigation");
		btn.innerHTML = "<span></span><span></span><span></span>";
		btn.addEventListener("click", () => document.body.classList.add("afx-sidebar-open"));
		document.body.appendChild(btn);
	}

	// v15-era buttons injected by afintrix_theme.js; the v16 desk does not need them.
	function drop_legacy_navbar_buttons() {
		document
			.querySelectorAll(".header-toggle, .naidapa-sidebar-mode-btn")
			.forEach((el) => el.remove());
	}

	function set_kbd_hint(nav) {
		const kbd = nav.querySelector("[data-afx-kbd]");
		if (!kbd) return;
		const is_mac = (navigator.userAgentData?.platform || navigator.platform || "")
			.toLowerCase()
			.includes("mac");
		kbd.textContent = is_mac ? "\u2318K" : "Ctrl+K";
	}

	function restore_groups(nav) {
		const state = read_groups();
		nav.querySelectorAll(".afx-group").forEach((group) => {
			const slug = group.getAttribute("data-afx-group");
			const toggle = group.querySelector(".afx-group-toggle");
			if (!toggle || !(slug in state)) return;
			toggle.setAttribute("aria-expanded", state[slug] ? "true" : "false");
		});
	}

	function bind(nav) {
		nav.addEventListener("click", function (e) {
			const toggle = e.target.closest(".afx-group-toggle");
			if (toggle) {
				// A collapsed rail has no room for children: open the rail instead.
				if (document.body.classList.contains("afx-collapsed")) {
					toggle_sidebar();
					return;
				}
				const expanded = toggle.getAttribute("aria-expanded") === "true";
				toggle.setAttribute("aria-expanded", expanded ? "false" : "true");
				const group = toggle.closest(".afx-group");
				if (group) write_group(group.getAttribute("data-afx-group"), !expanded);
				return;
			}

			if (e.target.closest("[data-afx-collapse]")) {
				toggle_sidebar();
				return;
			}

			const action = e.target.closest("[data-afx-action]");
			if (action) {
				// Frappe closes its notification dropdown on any document click that
				// lands outside the native item, so keep this click to ourselves and
				// proxy it once the current event has finished.
				e.preventDefault();
				e.stopPropagation();
				const name = action.getAttribute("data-afx-action");
				setTimeout(() => run_action(name), 0);
				return;
			}

			const theme_btn = e.target.closest("[data-afx-theme]");
			if (theme_btn) {
				set_theme(theme_btn.getAttribute("data-afx-theme"));
				return;
			}

			if (e.target.closest("[data-afx-route]") && is_mobile()) {
				document.body.classList.remove("afx-sidebar-open");
			}
		});

		// The desk's own sidebar button drives this sidebar instead.
		document.addEventListener(
			"click",
			function (e) {
				const btn = e.target.closest(".sidebar-toggle-btn:not(.collapse-sidebar-link)");
				if (!btn) return;
				e.preventDefault();
				e.stopPropagation();
				toggle_sidebar();
			},
			true
		);

		window.addEventListener("resize", function () {
			if (!is_mobile()) document.body.classList.remove("afx-sidebar-open");
		});
	}

	function toggle_sidebar() {
		if (is_mobile()) {
			document.body.classList.toggle("afx-sidebar-open");
			return;
		}
		const collapsed = document.body.classList.toggle("afx-collapsed");
		try {
			localStorage.setItem(COLLAPSE_KEY, collapsed ? "true" : "false");
		} catch (e) {
			/* ignore */
		}
	}

	function run_action(action) {
		if (action === "search") {
			const el = document.querySelector("#navbar-modal-search .item-anchor, #navbar-modal-search");
			if (el) el.click();
			return;
		}
		if (action === "notifications") {
			const el = document.querySelector(
				".sidebar-notification .item-anchor, [data-id='Notification'] .item-anchor"
			);
			if (el) el.click();
			return;
		}
		if (action === "user-menu") {
			if (frappe.ui.toolbar && frappe.ui.toolbar.route_to_user) {
				frappe.ui.toolbar.route_to_user();
			} else {
				frappe.set_route("user-profile");
			}
		}
	}

	function set_theme(theme) {
		const root = document.documentElement;
		root.setAttribute("data-theme-mode", theme);
		root.setAttribute("data-theme", theme);
		sync_theme_buttons();
		frappe.xcall("frappe.core.doctype.user.user.switch_theme", {
			theme: theme.charAt(0).toUpperCase() + theme.slice(1),
		});
	}

	function sync_theme_buttons() {
		const current = document.documentElement.getAttribute("data-theme") || "light";
		document.querySelectorAll("[data-afx-theme]").forEach((btn) => {
			btn.classList.toggle("afx-active", btn.getAttribute("data-afx-theme") === current);
		});
	}

	function current_route() {
		let path = (window.location.pathname || "").replace(/\/+$/, "");
		// /desk/home and /app/home address the same workspace
		path = path.replace(/^\/desk/, "/app");
		return path.toLowerCase();
	}

	function highlight() {
		const nav = document.getElementById("afx-sidebar");
		if (!nav) return;

		const path = current_route();
		let best = null;

		nav.querySelectorAll("[data-afx-route]").forEach((el) => {
			el.classList.remove("afx-active");
			const route = (el.getAttribute("data-afx-route") || "")
				.replace(/\/+$/, "")
				.replace(/^\/desk/, "/app")
				.toLowerCase();
			if (!route) return;
			if (path === route || path.startsWith(route + "/")) {
				if (!best || route.length > best.route.length) best = { el: el, route: route };
			}
		});

		if (!best) return;
		best.el.classList.add("afx-active");

		const subnav = best.el.closest(".afx-subnav");
		if (subnav) {
			const toggle = subnav.previousElementSibling;
			if (toggle && toggle.classList.contains("afx-group-toggle")) {
				toggle.setAttribute("aria-expanded", "true");
			}
		}
	}

	function watch_notification_count() {
		const source = document.querySelector(".sidebar-notification .sidebar-notification-count");
		const target = document.querySelector("[data-afx-notification-count]");
		if (!source || !target) return;

		const sync = () => {
			const hidden = source.classList.contains("hidden");
			target.textContent = source.textContent.trim() || "0";
			target.classList.toggle("hidden", hidden);
		};

		new MutationObserver(sync).observe(source, {
			attributes: true,
			childList: true,
			characterData: true,
			subtree: true,
		});
		sync();
	}

	function boot() {
		drop_legacy_navbar_buttons();
		inject();
		highlight();
		sync_theme_buttons();
	}

	$(document).ready(boot);
	$(document).on("app_ready page-change", boot);
	window.addEventListener("hashchange", highlight);
	window.addEventListener("popstate", highlight);
})();
