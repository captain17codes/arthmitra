import React from "react";
import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { App } from "../src/App";

describe("Agent PWA Frontend Journey", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders mobile baseline, header and case list", async () => {
    render(<App />);

    // Brand and logo visible
    expect(screen.getByText("अर्थमित्र")).toBeInTheDocument();

    // Cases title or New Case CTA visible
    expect(screen.getAllByText("उद्योजक प्रकरणे").length).toBeGreaterThan(0);
    expect(screen.getAllByText("नवीन प्रकरण सुरू करा").length).toBeGreaterThan(0);
  });

  it("navigates through DPDP consent notice into beneficiary profile", async () => {
    render(<App />);

    // Tap "+ नवीन प्रकरण सुरू करा"
    const newCaseBtn = screen.getAllByText("नवीन प्रकरण सुरू करा")[0];
    fireEvent.click(newCaseBtn);

    // Verify statutory DPDP notice header is shown
    expect(
      screen.getByText(/वैयक्तिक डेटा संमती सूचना/i)
    ).toBeInTheDocument();

    // Tap voice consent button
    const consentBtn = screen.getByText(/होय, मी सहमत आहे/i);
    fireEvent.click(consentBtn);

    // Wait for recorded badge
    await waitFor(
      () => {
        expect(
          screen.getByText(/कायदेशीर संमती यशस्वीरीत्या नोंदवली गेली आहे/i)
        ).toBeInTheDocument();
      },
      { timeout: 3000 }
    );

    // Advance to Profile
    const nextBtn = screen.getByText(/उद्योजक माहिती भरा/i);
    fireEvent.click(nextBtn);

    // Profile screen visible
    expect(
      screen.getByText("उद्योजकाची प्राथमिक माहिती")
    ).toBeInTheDocument();
    expect(screen.getByText("सामाजिक प्रवर्ग *")).toBeInTheDocument();
  });

  it("supports language switching between Marathi, Hindi and English", () => {
    render(<App />);

    // Switch to English
    const enBtn = screen.getByRole("button", { name: "Switch to en" });
    fireEvent.click(enBtn);

    expect(screen.getByText("ArthMitra")).toBeInTheDocument();
    expect(screen.getAllByText("Beneficiary Cases").length).toBeGreaterThan(0);

    // Switch to Hindi
    const hiBtn = screen.getByRole("button", { name: "Switch to hi" });
    fireEvent.click(hiBtn);

    expect(screen.getAllByText("उद्यमी आवेदन").length).toBeGreaterThan(0);
  });

  it("navigates to supervisor dashboard console and opens scheme editor", () => {
    render(<App />);

    // Tap supervisor bottom nav tab
    const supervisorTab = screen.getByText("पर्यवेक्षक");
    fireEvent.click(supervisorTab);

    // Verify supervisor dashboard header
    expect(
      screen.getByText("जिल्हा व गट स्तरावरील सूक्ष्म-उद्योग स्थिती")
    ).toBeInTheDocument();
    expect(
      screen.getByText("बाजार संतृप्तता व स्पर्धा धोके (Saturation Flags)")
    ).toBeInTheDocument();

    // Click Scheme Rules Editor tool
    const schemeBtn = screen.getByText(/शासकीय योजना नियम व आवृत्ती/i);
    fireEvent.click(schemeBtn);

    // Verify scheme editor screen
    expect(
      screen.getByText(/शासकीय योजना नियम व आवृत्ती व्यवस्थापन/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/नियम तपासा व चाचणी चालवा/i)
    ).toBeInTheDocument();
  });
});
