/**
 * Afintrix desk top bar — Phase 1.
 *
 * The reference kit puts search, quick links, notifications and the user menu
 * along the top, and keeps the sidebar for navigation only. Frappe v16 keeps
 * all of those inside its sidebar, so this lifts them into the desk's page
 * head and lets afintrix_sidebar.js drop its own copies.
 *
 * Nothing here reimplements desk behaviour: each control proxies to the native
 * element that already owns it.
 */
(function () {
	"use strict";

	let building = false;

	function is_desk() {
		// .page-head is not present on every desk route and appears late on a
		// cold load; the content column is the only thing the bar needs.
		return !!(window.frappe && frappe.boot && document.querySelector(".main-section"));
	}

	function settings() {
		return (frappe.boot && frappe.boot.theme_settings) || {};
	}

	function el(tag, className, html) {
		const node = document.createElement(tag);
		if (className) node.className = className;
		if (html !== undefined) node.innerHTML = html;
		return node;
	}

	function build() {
		if (building || !is_desk()) return;
		const main = document.querySelector(".main-section");
		if (!main || document.querySelector(".afx-topbar")) return;

		building = true;
		try {
			const bar = el("div", "afx-topbar");
			bar.appendChild(search_box());

			const links = quick_links();
			if (links) bar.appendChild(links);

			bar.appendChild(el("div", "afx-topbar-spacer"));
			bar.appendChild(notification_button());
			bar.appendChild(user_button());

			// its own row at the top of the content column, so breadcrumbs and
			// page actions keep the full width of the row below. .page-head is
			// nested deeper than .main-section, so prepend rather than
			// insertBefore against a non-child node.
			main.prepend(bar);

			document.body.classList.add("afx-topbar-on");
		} catch (e) {
			console.warn("afintrix top bar failed to build", e);
		} finally {
			building = false;
		}
	}

	function search_box() {
		const mac = (navigator.userAgentData?.platform || navigator.platform || "")
			.toLowerCase()
			.includes("mac");
		const box = el(
			"button",
			"afx-topbar-search",
			`<span class="afx-topbar-search-icon"><iconify-icon icon="line-md:search"></iconify-icon></span>
			 <span class="afx-topbar-search-label">${frappe.utils.escape_html(__("Search anything..."))}</span>
			 <span class="afx-kbd">${mac ? "⌘K" : "Ctrl+K"}</span>`
		);
		box.type = "button";
		box.addEventListener("click", () => {
			const native = document.querySelector("#navbar-modal-search .item-anchor, #navbar-modal-search");
			if (native) native.click();
		});
		return box;
	}

	function quick_links() {
		const links = settings().quick_links || [];
		if (!links.length) return null;

		const wrap = el("nav", "afx-topbar-links");
		links.forEach((row) => {
			if (!row.label || !row.route) return;
			const a = el("a", "afx-topbar-link");
			a.textContent = row.label;
			a.href = row.route;
			if (row.open_in_new_tab) {
				a.target = "_blank";
				a.rel = "noopener";
			}
			wrap.appendChild(a);
		});
		return wrap.children.length ? wrap : null;
	}

	function notification_button() {
		const btn = el(
			"button",
			"afx-topbar-icon-btn",
			`<iconify-icon icon="line-md:bell"></iconify-icon>
			 <span class="afx-topbar-dot hidden" data-afx-topbar-count></span>`
		);
		btn.type = "button";
		btn.title = __("Notifications");
		btn.addEventListener("click", function (e) {
			// frappe closes the dropdown on any document click outside its own item
			e.preventDefault();
			e.stopPropagation();
			setTimeout(() => {
				const native = document.querySelector(
					".sidebar-notification .item-anchor, [data-id='Notification'] .item-anchor"
				);
				if (native) native.click();
			}, 0);
		});
		mirror_notification_count(btn);
		return btn;
	}

	function mirror_notification_count(btn) {
		const source = document.querySelector(".sidebar-notification .sidebar-notification-count");
		const dot = btn.querySelector("[data-afx-topbar-count]");
		if (!source || !dot) return;

		const sync = () => {
			const count = (source.textContent || "").trim();
			const hidden = source.classList.contains("hidden") || !count || count === "0";
			dot.textContent = hidden ? "" : count;
			dot.classList.toggle("hidden", hidden);
		};
		new MutationObserver(sync).observe(source, {
			attributes: true,
			childList: true,
			characterData: true,
			subtree: true,
		});
		sync();
	}

	function user_button() {
		const user = (frappe.session && frappe.session.user) || "";
		// frappe.user.full_name() answers "You" for the current session, which is
		// no use for initials — read the directory entry instead.
		const info = (frappe.boot && frappe.boot.user_info && frappe.boot.user_info[user]) || {};
		const full_name = info.fullname || frappe.session.user_fullname || user;
		const email = (frappe.session && frappe.session.user_email) || user;
		const avatar = info && info.image
			? `<img src="${frappe.utils.escape_html(info.image)}" alt="">`
			: frappe.utils.escape_html(initials(full_name || user));

		const wrap = el("div", "afx-topbar-usermenu");
		const btn = el(
			"button",
			"afx-topbar-user",
			`<span class="afx-topbar-avatar">${avatar}</span>
			 <iconify-icon icon="line-md:chevron-down"></iconify-icon>`
		);
		btn.type = "button";
		btn.title = full_name || user;
		btn.setAttribute("aria-haspopup", "menu");
		btn.setAttribute("aria-expanded", "false");

		// The /desk navbar that used to carry Edit Profile and Logout is hidden
		// (it duplicated this bar), so those two live here. Frappe Support and
		// About are deliberately left out.
		const menu = el(
			"div",
			"afx-topbar-menu hidden",
			`<div class="afx-topbar-menu-head">
				<span class="afx-topbar-menu-name">${frappe.utils.escape_html(full_name || user)}</span>
				<span class="afx-topbar-menu-mail">${frappe.utils.escape_html(email)}</span>
			 </div>
			 <a class="afx-topbar-menu-item" href="/app/user/${encodeURIComponent(user)}">
				<iconify-icon icon="line-md:person"></iconify-icon>${frappe.utils.escape_html(__("My Profile"))}
			 </a>
			 <a class="afx-topbar-menu-item" href="/app/settings">
				<iconify-icon icon="line-md:cog"></iconify-icon>${frappe.utils.escape_html(__("Settings"))}
			 </a>
			 <button type="button" class="afx-topbar-menu-item" data-afx-logout>
				<iconify-icon icon="line-md:logout"></iconify-icon>${frappe.utils.escape_html(__("Logout"))}
			 </button>`
		);
		menu.setAttribute("role", "menu");

		const close = () => {
			menu.classList.add("hidden");
			btn.setAttribute("aria-expanded", "false");
		};

		btn.addEventListener("click", function (e) {
			e.stopPropagation();
			const open = menu.classList.toggle("hidden") === false;
			btn.setAttribute("aria-expanded", open ? "true" : "false");
		});

		menu.addEventListener("click", function (e) {
			if (e.target.closest("[data-afx-logout]")) {
				e.preventDefault();
				frappe.app.logout();
			}
			close();
		});

		document.addEventListener("click", function (e) {
			if (!wrap.contains(e.target)) close();
		});
		document.addEventListener("keydown", function (e) {
			if (e.key === "Escape") close();
		});

		wrap.appendChild(btn);
		wrap.appendChild(menu);
		return wrap;
	}

	function initials(name) {
		const parts = String(name || "")
			.replace(/[@.]/g, " ")
			.split(" ")
			.filter(Boolean);
		if (!parts.length) return "?";
		if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
		return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
	}

	// The desk renders its shell asynchronously, so a single pass at ready time
	// can run before .main-section exists. Watch until the bar is in place.
	function watch_for_shell() {
		if (document.querySelector(".afx-topbar")) return;
		const observer = new MutationObserver(() => {
			build();
			if (document.querySelector(".afx-topbar")) observer.disconnect();
		});
		observer.observe(document.body, { childList: true, subtree: true });
		setTimeout(() => observer.disconnect(), 15000);
	}

	$(document).ready(function () {
		build();
		watch_for_shell();
	});
	$(document).on("app_ready page-change", build);

	window.afintrix_topbar = { build: build };
})();
