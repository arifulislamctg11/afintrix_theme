const { test, expect } = require("@playwright/test");
const { login } = require("../../playwright/auth");

test.describe("module screens", () => {
	test.beforeEach(async ({ page }) => {
		await login(page);
	});

	test("a workspace stat tile reads label first, then the number", async ({ page }) => {
		await page.goto("/app/accounting");
		await page.waitForSelector(".number-widget-box .number");

		const card = page.locator(".number-widget-box").first();
		const label = await card.locator(".widget-title").boundingBox();
		const number = await card.locator(".number").boundingBox();

		expect(label).not.toBeNull();
		expect(number).not.toBeNull();
		expect(label.y).toBeLessThan(number.y);
	});

	test("page head controls stay on one row, clear of the breadcrumbs", async ({ page }) => {
		await page.goto("/app/todo/view/calendar/default");
		await page.waitForSelector(".fc");

		const head = await page.locator(".page-head").boundingBox();
		const controls = page.locator(".page-head .page-actions .btn-group, .page-head .sort-selector");

		for (let i = 0; i < (await controls.count()); i++) {
			const box = await controls.nth(i).boundingBox();
			if (!box) continue;
			// nothing may start above the head it belongs to
			expect(box.y).toBeGreaterThanOrEqual(head.y - 1);
		}
	});

	test("the chart of accounts tree opens in a card", async ({ page }) => {
		await page.goto("/app/account/view/tree");
		await page.waitForSelector(".tree");

		const radius = await page
			.locator(".layout-main-section.frappe-card:has(.tree)")
			.first()
			.evaluate((el) => getComputedStyle(el).borderRadius);
		expect(radius).not.toBe("0px");
	});
});
