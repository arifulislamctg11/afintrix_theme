const { test, expect } = require("@playwright/test");
const { login } = require("../../playwright/auth");

/**
 * Brand Studio drives the live look of the site it runs on, so this spec never
 * saves: it changes the controls, checks the preview follows, and leaves.
 */
test.describe("Brand Studio", () => {
	test.beforeEach(async ({ page }) => {
		await login(page);
		await page.goto("/app/brand-studio");
		await page.waitForSelector(".afx-preview-shell");
	});

	test("loads the site's current branding into the form", async ({ page }) => {
		// the form fills from an xcall, so the control exists before its value does
		await page.waitForFunction(() => {
			const input = document.querySelector('[data-fieldname="title"] input');
			return input && input.value.length > 0;
		});

		const title = await page.inputValue('[data-fieldname="title"] input');
		expect(title.length).toBeGreaterThan(0);
		await expect(page.locator(".afx-preview-name")).toHaveText(title);
	});

	test("the preview repaints as the colour changes", async ({ page }) => {
		const before = await page
			.locator(".afx-preview-btn")
			.evaluate((el) => getComputedStyle(el).backgroundColor);

		await page.evaluate(() => {
			const studio = document.querySelector("[data-page-route=brand-studio]").afx_brand;
			studio.controls.primary_color.set_value("#0B7A5C");
			studio.paint();
		});

		const after = await page
			.locator(".afx-preview-btn")
			.evaluate((el) => getComputedStyle(el).backgroundColor);

		expect(after).not.toBe(before);
		expect(after).toBe("rgb(11, 122, 92)");
	});

	test("the accent colour drives the rule under the preview", async ({ page }) => {
		await page.evaluate(() => {
			const studio = document.querySelector("[data-page-route=brand-studio]").afx_brand;
			studio.controls.secondary_color.set_value("#C89B3C");
			studio.paint();
		});

		const rule = await page
			.locator(".afx-preview-rule")
			.evaluate((el) => getComputedStyle(el).backgroundColor);
		expect(rule).toBe("rgb(200, 155, 60)");
	});
});
