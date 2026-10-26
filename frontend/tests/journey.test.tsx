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
    expect(screen.getByText("उद्योजक प्रकरणे")).toBeInTheDocument();
    expect(screen.getByText("नवीन प्रकरण सुरू करा")).toBeInTheDocument();
  });

  it("navigates through DPDP consent notice into beneficiary profile", async () => {
    render(<App />);

    // Tap "+ नवीन प्रकरण सुरू करा"
    const newCaseBtn = screen.getByText("नवीन प्रकरण सुरू करा");
    fireEvent.click(newCaseBtn);

    // Verify statutory DPDP notice header is shown
    expect(
      screen.getByText(/वैयक्तिक डेटा संमती सूचना/i)
    ).toBeInTheDocument();

    // Tap voice consent button
    const consentBtn = screen.getByText(/आवाजी संमती/i);
    fireEvent.click(consentBtn);

    // Wait for recorded badge
    await waitFor(() => {
      expect(
        screen.getByText(/कायदेशीर संमती यशस्वीरीत्या नोंदवली गेली आहे/i)
      ).toBeInTheDocument();
    });

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
    expect(screen.getByText("Beneficiary Cases")).toBeInTheDocument();

    // Switch to Hindi
    const hiBtn = screen.getByRole("button", { name: "Switch to hi" });
    fireEvent.click(hiBtn);

    expect(screen.getByText("उद्यमी आवेदन")).toBeInTheDocument();
  });
});
