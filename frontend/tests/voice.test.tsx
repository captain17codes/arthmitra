import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import {
  parseIndianSpokenNumber,
  formatInrCurrency,
} from "../src/services/voiceParser";
import { VoiceFieldInput } from "../src/components/VoiceFieldInput";

describe("Voice Engine & Indian Number Parser (Frontend)", () => {
  it("correctly parses Indian spoken idioms into exact numbers", () => {
    expect(parseIndianSpokenNumber("दीड लाख")).toBe(150000);
    expect(parseIndianSpokenNumber("अडीच लाख")).toBe(250000);
    expect(parseIndianSpokenNumber("सव्वा लाख")).toBe(125000);
    expect(parseIndianSpokenNumber("साडे तीन हजार")).toBe(3500);
    expect(parseIndianSpokenNumber("पावणे दोन लाख")).toBe(175000);
    expect(parseIndianSpokenNumber("दोन लाख पन्नास हजार")).toBe(250000);
    expect(parseIndianSpokenNumber("एक लाख वीस हजार")).toBe(120000);
    expect(parseIndianSpokenNumber("पन्नास हजार")).toBe(50000);
    expect(parseIndianSpokenNumber("एक कोटी")).toBe(10000000);
  });

  it("handles Hindi, English and Hinglish phrases", () => {
    expect(parseIndianSpokenNumber("डेढ़ लाख")).toBe(150000);
    expect(parseIndianSpokenNumber("ढाई लाख")).toBe(250000);
    expect(parseIndianSpokenNumber("सवा लाख")).toBe(125000);
    expect(parseIndianSpokenNumber("साढ़े तीन हजार")).toBe(3500);
    expect(parseIndianSpokenNumber("पौने दो लाख")).toBe(175000);
    expect(parseIndianSpokenNumber("dedh lakh")).toBe(150000);
    expect(parseIndianSpokenNumber("dhai lakh")).toBe(250000);
    expect(parseIndianSpokenNumber("sade teen hazar")).toBe(3500);
    expect(parseIndianSpokenNumber("1.5 lakh")).toBe(150000);
    expect(parseIndianSpokenNumber("50k")).toBe(50000);
    expect(parseIndianSpokenNumber("₹ 1,50,000")).toBe(150000);
  });

  it("formats numbers into Indian currency string", () => {
    expect(formatInrCurrency(150000)).toBe("₹1,50,000");
    expect(formatInrCurrency(3500)).toBe("₹3,500");
    expect(formatInrCurrency(25000000)).toBe("₹2,50,00,000");
  });

  it("renders VoiceFieldInput and requires explicit confirmation before applying values", () => {
    const handleChange = vi.fn();
    render(
      <VoiceFieldInput
        label="मासिक दुकान भाडे"
        value={2000}
        onChange={handleChange}
        type="number"
        language="mr"
      />
    );

    // Initial value is shown
    expect(screen.getByDisplayValue("2000")).toBeInTheDocument();

    // Click mic trigger
    const micBtn = screen.getByLabelText("Speak into microphone");
    fireEvent.click(micBtn);

    // Modal opens
    expect(screen.getByText(/आवाजी इनपुट \(Voice Input\)/i)).toBeInTheDocument();

    // Type or pick a spoken phrase: "साडे तीन हजार"
    const transcriptInput = screen.getByPlaceholderText(/उदा\. दीड लाख/i);
    fireEvent.change(transcriptInput, { target: { value: "साडे तीन हजार" } });

    // Live preview updates to ₹3,500
    expect(screen.getByText("₹3,500")).toBeInTheDocument();

    // handleChange should NOT have been called yet (acceptance check: nothing is used without confirmation)
    expect(handleChange).not.toHaveBeenCalled();

    // Click "वापरा (Apply Value)"
    const applyBtn = screen.getByText(/वापरा \(Apply Value\)/i);
    fireEvent.click(applyBtn);

    // Now handleChange is called with 3500
    expect(handleChange).toHaveBeenCalledWith(3500);
  });
});
