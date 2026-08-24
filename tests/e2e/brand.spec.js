const { test, expect } = require("@playwright/test");
const { login } = require("../../playwright/auth");

test.describe("brand shell", () => {
	test("the sign-in page is the Afintrix split screen", async ({ page }) => {
		await page.goto("/login");
		await expect(page.locator(".for-login")).toBeVisible();
		await expect(page.locator(".btn-login")).toBeVisible();

		// the login button carries the brand blue, not frappe's default
		const background = await page
			.locator(".btn-login")
			.evaluate((el) => getComputedStyle(el).backgroundColor);
		expect(background).toBe("rgb(30, 57, 214)");
	});

	test("the desk draws exactly one top bar and one sidebar", async ({ page }) => {
		await login(page);
		await page.goto("/app/employee");
		await page.waitForSelector(".afx-topbar");

		await expect(page.locator(".afx-topbar")).toHaveCount(1);
		await expect(page.locator("#afx-sidebar")).toHaveCount(1);

		// the /desk page ships its own navbar; it must stay out of the layout
		const stray = await page
			.locator("header.desktop-navbar")
			.evaluateAll((nodes) => nodes.filter((n) => getComputedStyle(n).display !== "none").length);
		expect(stray).toBe(0);
	});

	test("the user menu offers Logout and never About", async ({ page }) => {
		await login(page);
		await page.click(".afx-topbar-user");
		const menu = page.locator(".afx-topbar-menu");
		await expect(menu).toBeVisible();
		await expect(menu).toContainText("Logout");
		await expect(menu).not.toContainText("About");
	});
});
