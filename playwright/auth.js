/**
 * Shared sign-in helper.
 *
 * The session is created through /api/method/login rather than by driving the
 * sign-in form: the branded login page rehydrates its form after load, which
 * makes typing into it a race, and none of these specs are about the form —
 * brand.spec covers that screen on its own. page.request shares the browser
 * context's cookie jar, so the desk opens signed in.
 */
const USER = process.env.AFX_USER || "administrator";
const PASSWORD = process.env.AFX_PASSWORD || "admin";

async function login(page) {
	const response = await page.request.post("/api/method/login", {
		form: { usr: USER, pwd: PASSWORD },
	});
	if (!response.ok()) {
		throw new Error(`login failed: ${response.status()} ${await response.text()}`);
	}

	await page.goto("/app");
	await page.waitForSelector(".afx-topbar", { timeout: 30_000 });
}

module.exports = { login, USER, PASSWORD };
