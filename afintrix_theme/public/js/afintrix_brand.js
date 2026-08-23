/**
 * Afintrix brand runtime — Phase 1.
 *
 * afintrix_brand.css ships the default Afintrix tokens. This applies a site's
 * own overrides from Theme Settings on top of them, so re-branding an instance
 * is a settings change rather than a code change.
 *
 * Tints are derived from the two configured colours, so a site that sets only
 * a primary colour still gets a coherent set of hover, soft-fill and ring
 * values instead of Afintrix blue leaking through.
 */
(function () {
	"use strict";

	function parse_hex(value) {
		if (!value) return null;
		const hex = String(value).trim().replace("#", "");
		const full =
			hex.length === 3
				? hex
						.split("")
						.map((c) => c + c)
						.join("")
				: hex;
		if (!/^[0-9a-f]{6}$/i.test(full)) return null;
		return {
			r: parseInt(full.slice(0, 2), 16),
			g: parseInt(full.slice(2, 4), 16),
			b: parseInt(full.slice(4, 6), 16),
		};
	}

	function to_hex(rgb) {
		const clamp = (n) => Math.max(0, Math.min(255, Math.round(n)));
		return (
			"#" +
			[rgb.r, rgb.g, rgb.b]
				.map((c) => clamp(c).toString(16).padStart(2, "0"))
				.join("")
		);
	}

	function mix(rgb, target, amount) {
		return to_hex({
			r: rgb.r + (target - rgb.r) * amount,
			g: rgb.g + (target - rgb.g) * amount,
			b: rgb.b + (target - rgb.b) * amount,
		});
	}

	function apply(theme_settings) {
		const root = document.documentElement;
		const primary = parse_hex(theme_settings.primary_color);
		const secondary = parse_hex(theme_settings.secondary_color);

		if (primary) {
			const is_dark = document.documentElement.getAttribute("data-theme") === "dark";
			root.style.setProperty("--afx-primary", to_hex(primary));
			root.style.setProperty("--afx-primary-deep", mix(primary, 0, 0.22));
			root.style.setProperty("--afx-primary-600", mix(primary, 0, 0.12));
			root.style.setProperty("--afx-primary-050", mix(primary, is_dark ? 0 : 255, 0.94));
			root.style.setProperty("--afx-primary-100", mix(primary, is_dark ? 0 : 255, 0.86));
			root.style.setProperty("--afx-primary-200", mix(primary, is_dark ? 0 : 255, 0.68));
			root.style.setProperty(
				"--afx-primary-ring",
				`rgba(${primary.r}, ${primary.g}, ${primary.b}, 0.25)`
			);
		}

		if (secondary) {
			const is_dark = document.documentElement.getAttribute("data-theme") === "dark";
			root.style.setProperty("--afx-gold", to_hex(secondary));
			root.style.setProperty("--afx-gold-light", mix(secondary, 255, 0.35));
			root.style.setProperty("--afx-gold-050", mix(secondary, is_dark ? 0 : 255, 0.92));
			root.style.setProperty("--afx-gold-100", mix(secondary, is_dark ? 0 : 255, 0.82));
		}
	}

	function boot() {
		const settings = (window.frappe && frappe.boot && frappe.boot.theme_settings) || {};
		if (settings.primary_color || settings.secondary_color) apply(settings);
	}

	// Theme switches change how tints should sit against the ground, so recompute.
	function watch_theme() {
		new MutationObserver(boot).observe(document.documentElement, {
			attributes: true,
			attributeFilter: ["data-theme"],
		});
	}

	boot();
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", () => {
			boot();
			watch_theme();
		});
	} else {
		watch_theme();
	}

	window.afintrix_brand = { apply: apply, refresh: boot };
})();
