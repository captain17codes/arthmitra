import { test, expect } from "@playwright/test";

test.describe("ArthMitra Agent Journey (360x640 Mobile Viewport)", () => {
  test("completes full end-to-end case from consent to DPR on 360x640 viewport", async ({
    page,
  }) => {
    // 1. Visit app
    await page.goto("/");

    // 2. Baseline checks
    await expect(page.locator("text=अर्थमित्र")).toBeVisible();
    await expect(page.locator("text=उद्योजक प्रकरणे")).toBeVisible();

    // 3. Start New Case
    const newCaseBtn = page.locator("button:has-text('नवीन प्रकरण सुरू करा')").first();
    await newCaseBtn.click();

    // 4. Statutory DPDP Consent Step
    await expect(page.locator("text=डीपीडीपी वैधानिक संमती")).toBeVisible();
    await expect(page.locator("text=वैयक्तिक डेटा संमती सूचना")).toBeVisible();

    // Tap voice consent button
    const voiceBtn = page.locator("button:has-text('आवाजी संमती')");
    await voiceBtn.click();

    // Wait for recorded confirmation
    await expect(
      page.locator("text=कायदेशीर संमती यशस्वीरीत्या नोंदवली गेली आहे")
    ).toBeVisible({ timeout: 5000 });

    // Tap proceed to profile
    const toProfileBtn = page.locator("button:has-text('उद्योजक माहिती भरा')");
    await toProfileBtn.click();

    // 5. Beneficiary Profile Step
    await expect(page.locator("text=उद्योजकाची प्राथमिक माहिती")).toBeVisible();
    const nameInput = page.locator("input[placeholder='उदा. अनिता कांबळे']");
    await expect(nameInput).toBeVisible();

    // Tap next to village
    const toVillageBtn = page.locator("button:has-text('पुढे →')");
    await toVillageBtn.click();

    // 6. Village Picker Step
    await expect(page.locator("text=उद्योगाचे कार्यक्षेत्र / गाव निवडा")).toBeVisible();
    await expect(page.locator("text=शिरवळ")).toBeVisible();

    // Select Shirwal
    const selectVillageBtn = page.locator("button:has-text('हे गाव निवडा →')");
    await selectVillageBtn.click();

    // 7. Business Catalog Step
    await expect(page.locator("text=सूक्ष्म व्यवसायाचा प्रकार निवडा")).toBeVisible();
    await expect(page.locator("text=किराणा दुकान")).toBeVisible();

    // Proceed to calibration
    const toCalibBtn = page.locator("button:has-text('स्थानिक तपासणी करा →')");
    await toCalibBtn.click();

    // 8. Calibration Step
    await expect(page.locator("text=स्थानिक बाजार व क्षमता तपासणी")).toBeVisible();

    // Click evaluate
    const evalBtn = page.locator("button:has-text('व्यवहार्यता व कर्ज योजना तपासा →')");
    await evalBtn.click();

    // 9. Results Screen
    await expect(page.locator("text=व्यवसाय व्यवहार्यता व कर्ज रचना अहवाल")).toBeVisible();
    await expect(page.locator("text=सर्वोत्तम EMI")).toBeVisible();

    // Check Financing top scheme
    await expect(page.locator("text=# 1 पर्याय")).toBeVisible();

    // Switch to Market tab
    const marketTab = page.locator("button:has-text('बाजारपेठ')");
    await marketTab.click();
    await expect(page.locator("text=स्थानिक बाजार मागणी व स्पर्धा विश्लेषण")).toBeVisible();

    // Switch to Viability tab
    const viabilityTab = page.locator("button:has-text('व्यवहार्यता')");
    await viabilityTab.click();
    await expect(page.locator("text=कर्ज परतफेड क्षमता (DSCR)")).toBeVisible();

    // 10. Proceed to DPR Screen
    const toDprBtn = page.locator("button:has-text('बँकेसाठी अधिकृत डीपीआर (PDF) तयार करा →')");
    await toDprBtn.click();

    await expect(page.locator("text=बँकेसाठी प्रकल्प अहवाल")).toBeVisible();
    await expect(page.locator("text=मराठी डीपीआर डाऊनलोड करा")).toBeVisible();
    await expect(page.locator("text=डिजिटल सुरक्षितता कोड (SHA-256)")).toBeVisible();
  });
});
