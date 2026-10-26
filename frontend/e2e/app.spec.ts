import { test, expect } from "@playwright/test";

test("mobile screen 360x640 baseline loads app title", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("h1")).toContainText("ArthMitra");
});
