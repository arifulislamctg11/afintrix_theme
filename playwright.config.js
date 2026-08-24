/**
 * Playwright — starts at Phase 3, per SPEC section 6: before this the screens
 * moved too often for browser tests to repay their maintenance.
 *
 * The suite runs against a live bench, not a fixture site, so the base URL and
 * the credentials come from the environment:
 *
 *   AFX_BASE_URL=http://192.168.64.4:8000 AFX_USER=administrator AFX_PASSWORD=admin \
 *     npx playwright test
 */
const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
	testDir: "./tests/e2e",
	timeout: 60_000,
	expect: { timeout: 10_000 },
	fullyParallel: false,
	retries: process.env.CI ? 1 : 0,
	workers: 1,
	reporter: [["list"]],
	use: {
		baseURL: process.env.AFX_BASE_URL || "http://afintrix.localhost:8000",
		trace: "retain-on-failure",
		screenshot: "only-on-failure",
		viewport: { width: 1440, height: 900 },
	},
	projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
