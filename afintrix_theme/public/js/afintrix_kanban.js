/**
 * Kanban column counts — Phase 2.
 *
 * Frame 61 puts the number of cards next to each column title. Frappe's board
 * renders a coloured dot there instead and never counts, so the count is
 * derived from the DOM and written to the column as an attribute; the chip
 * itself is drawn in CSS. An observer keeps it right after a drag, an inline
 * add or a filter change.
 */
(function () {
	"use strict";

	let scheduled = false;

	function count_columns() {
		scheduled = false;
		document.querySelectorAll(".kanban .kanban-column").forEach((column) => {
			const cards = column.querySelectorAll(".kanban-cards .kanban-card-wrapper").length;
			// attr() reads the element's own attribute, so it goes on the title
			const title = column.querySelector(".kanban-title");
			if (title) title.setAttribute("data-afx-count", cards);
		});
	}

	function schedule() {
		if (scheduled) return;
		scheduled = true;
		// the board rewrites whole columns while dragging; one pass per frame is enough
		requestAnimationFrame(count_columns);
	}

	function watch() {
		const board = document.querySelector(".kanban");
		if (!board || board.__afx_counted) return true;
		board.__afx_counted = true;
		new MutationObserver(schedule).observe(board, { childList: true, subtree: true });
		schedule();
		return true;
	}

	// A cold load renders the board well after page-change fires, so keep
	// looking for a few seconds instead of checking once.
	function watch_until_found(attempts) {
		if (watch() === true && document.querySelector(".kanban")) return;
		if (attempts <= 0) return;
		setTimeout(() => watch_until_found(attempts - 1), 250);
	}

	$(document).on("app_ready page-change", function () {
		watch_until_found(40);
	});

	$(document).ready(function () {
		watch_until_found(40);
	});
})();
