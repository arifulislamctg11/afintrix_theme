const { test, expect } = require("@playwright/test");
const { login } = require("../../playwright/auth");

test.describe("HR screens", () => {
	test.beforeEach(async ({ page }) => {
		await login(page);
	});

	test("the employee list shows the name over the email", async ({ page }) => {
		await page.goto("/app/employee");
		await page.waitForSelector(".afx-person", { timeout: 20_000 });

		const first = page.locator(".afx-person").first();
		await expect(first.locator(".afx-person-name")).not.toBeEmpty();
		await expect(first.locator(".afx-person-mail")).toContainText("@");
	});

	test("the recruitment board counts its columns", async ({ page }) => {
		await page.goto("/app/job-applicant/view/kanban/Recruitment Pipeline");
		await page.waitForSelector(".kanban-column");

		const counted = page.locator(".kanban-title[data-afx-count]");
		expect(await counted.count()).toBeGreaterThan(0);
		await expect(counted.first()).toHaveAttribute("data-afx-count", /\d+/);
	});
});
