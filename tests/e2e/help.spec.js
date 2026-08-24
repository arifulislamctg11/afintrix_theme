const { test, expect } = require("@playwright/test");
const { login } = require("../../playwright/auth");

test.describe("Help Center", () => {
	test.beforeEach(async ({ page }) => {
		await login(page);
	});

	test("the index lists the five sections once", async ({ page }) => {
		await page.goto("/app/help-center");
		await page.waitForSelector(".afx-help-card");

		await expect(page.locator(".afx-help-head")).toHaveCount(1);
		await expect(page.locator(".afx-help-card")).toHaveCount(5);
		await expect(page.locator(".afx-help-card", { hasText: "FAQ" })).toBeVisible();
	});

	test("FAQ renders published articles and the search filters them", async ({ page }) => {
		await page.goto("/app/help-center/faq");
		await page.waitForSelector(".afx-help-article");

		const all = await page.locator(".afx-help-article").count();
		expect(all).toBeGreaterThan(0);

		await page.fill(".afx-help-search input", "password");
		const visible = await page
			.locator(".afx-help-article:not(.hidden)")
			.count();
		expect(visible).toBeLessThan(all);
	});

	test("contact support shows the details from Theme Settings", async ({ page }) => {
		await page.goto("/app/help-center/contact");
		await page.waitForSelector(".afx-help-contact");
		await expect(page.locator(".afx-help-contact")).toContainText("@");
		await expect(page.locator(".afx-help-form .btn-primary")).toBeVisible();
	});
});
