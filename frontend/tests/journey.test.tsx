import React from "react";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { App } from "../src/App";

type Route = (url: string, init?: RequestInit) => unknown;

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

function stubApi(route: Route) {
  const fn = vi.fn(async (url: string, init?: RequestInit) => {
    const out = route(String(url), init);
    return out instanceof Response ? out : json(out ?? []);
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

function signIn(role = "citizen") {
  localStorage.setItem("arthmitra_auth_token", "test-token");
  localStorage.setItem(
    "arthmitra_auth_user",
    JSON.stringify({ id: "7", full_name: "Asha Kamble", role, organization_id: "9", organization_name: "" })
  );
}

describe("Self-service PWA journey", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("signed out: shows login with sign-up / forgot PIN, and no demo PIN", () => {
    stubApi(() => []);
    render(<App />);
    expect(screen.getByText("पहिल्यांदाच? नवीन खाते बनवा")).toBeInTheDocument();
    expect(screen.getByText("पिन विसरलात?")).toBeInTheDocument();
    expect(screen.queryByText(/1234/)).not.toBeInTheDocument();
    expect(screen.queryByText(/बँक सखी/)).not.toBeInTheDocument();
  });

  it("sign-up: phone → OTP (demo shown) → name + PIN → my plans", async () => {
    const calls: string[] = [];
    stubApi((url, init) => {
      calls.push(`${init?.method || "GET"} ${url}`);
      if (url.endsWith("/auth/otp/request")) return { sent: true, dev_otp: "482913" };
      if (url.endsWith("/auth/otp/verify")) return { setup_token: "st", is_new_user: true, name: null };
      if (url.endsWith("/auth/pin")) {
        expect(JSON.parse(String(init?.body))).toMatchObject({ setup_token: "st", pin: "2580", name: "Asha" });
        return { access_token: "tok", user: { id: 7, name: "Asha", role: "citizen", org_id: 9, lang: "mr" } };
      }
      return [];
    });
    render(<App />);

    fireEvent.click(screen.getByText("पहिल्यांदाच? नवीन खाते बनवा"));
    fireEvent.change(screen.getByLabelText("मोबाईल क्रमांक"), { target: { value: "98220 11111" } });
    fireEvent.click(screen.getByText("OTP पाठवा"));

    await waitFor(() => expect(screen.getByText("482913")).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText("OTP टाका"), { target: { value: "482913" } });
    fireEvent.click(screen.getByText("पडताळा"));

    await waitFor(() => expect(screen.getByText("नवीन खाते")).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText("तुमचे नाव"), { target: { value: "Asha" } });
    fireEvent.change(screen.getByLabelText("४ अंकी पिन"), { target: { value: "2580" } });
    fireEvent.change(screen.getByLabelText("पिन पुन्हा टाका"), { target: { value: "2580" } });
    fireEvent.click(screen.getByText("खाते बनवा"));

    await waitFor(() => expect(screen.getAllByText("माझे व्यवसाय प्लॅन").length).toBeGreaterThan(0));
    expect(calls.some((c) => c.includes("/auth/otp/request"))).toBe(true);
  });

  it("PINs must match before an account is created", async () => {
    stubApi((url) => {
      if (url.endsWith("/auth/otp/request")) return { sent: true, dev_otp: "111222" };
      if (url.endsWith("/auth/otp/verify")) return { setup_token: "st", is_new_user: true, name: null };
      return [];
    });
    render(<App />);
    fireEvent.click(screen.getByText("पहिल्यांदाच? नवीन खाते बनवा"));
    fireEvent.change(screen.getByLabelText("मोबाईल क्रमांक"), { target: { value: "9822011111" } });
    fireEvent.click(screen.getByText("OTP पाठवा"));
    await waitFor(() => screen.getByLabelText("OTP टाका"));
    fireEvent.change(screen.getByLabelText("OTP टाका"), { target: { value: "111222" } });
    fireEvent.click(screen.getByText("पडताळा"));
    await waitFor(() => screen.getByLabelText("तुमचे नाव"));
    fireEvent.change(screen.getByLabelText("तुमचे नाव"), { target: { value: "Asha" } });
    fireEvent.change(screen.getByLabelText("४ अंकी पिन"), { target: { value: "2580" } });
    fireEvent.change(screen.getByLabelText("पिन पुन्हा टाका"), { target: { value: "2581" } });
    fireEvent.click(screen.getByText("खाते बनवा"));
    expect(screen.getByRole("alert")).toHaveTextContent("दोन्ही पिन सारखे नाहीत");
  });

  it("first plan: consent tick is required, then an empty profile (no invented values)", async () => {
    signIn();
    stubApi(() => []); // no cases, no saved profile
    render(<App />);
    fireEvent.click(screen.getAllByText("नवीन व्यवसाय प्लॅन")[0]);

    await waitFor(() => expect(screen.getByRole("checkbox")).toBeInTheDocument());
    const next = screen.getByText("पुढे: माझी माहिती →");
    expect(next).toBeDisabled();
    fireEvent.click(screen.getByRole("checkbox"));
    expect(next).not.toBeDisabled();
    fireEvent.click(next);

    expect(screen.getByText("तुमची माहिती")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Asha Kamble")).toBeInTheDocument(); // own name prefilled
    expect(screen.queryByDisplayValue("32")).not.toBeInTheDocument(); // no made-up age
  });

  it("later plans skip consent and reuse the saved profile", async () => {
    signIn();
    stubApi((url) => {
      if (url.endsWith("/beneficiaries"))
        return [{
          id: 5, first_name: "Asha Kamble", gender: "female", age: 34, category: "SC", disability_40: false,
          occupation_flags: [], annual_family_income: 90000, education_band: "secondary_10th", shg_member: true,
          prior_subsidy: "no", credit_default: "no", existing_emi_monthly: "0",
        }];
      return [];
    });
    render(<App />);
    fireEvent.click(screen.getAllByText("नवीन व्यवसाय प्लॅन")[0]);
    await waitFor(() => expect(screen.getByText("तुमची माहिती")).toBeInTheDocument());
    expect(screen.getByDisplayValue("34")).toBeInTheDocument();
    expect(screen.getByDisplayValue("90000")).toBeInTheDocument();
  });

  it("language switching uses personal wording", () => {
    signIn();
    stubApi(() => []);
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Switch to en" }));
    expect(screen.getAllByText("My Business Plans").length).toBeGreaterThan(0);
    fireEvent.click(screen.getByRole("button", { name: "Switch to hi" }));
    expect(screen.getAllByText("मेरे व्यवसाय प्लान").length).toBeGreaterThan(0);
  });

  it("no agent/supervisor console for a person; admin still gets it", () => {
    signIn("citizen");
    stubApi(() => []);
    const { unmount } = render(<App />);
    expect(screen.queryByText("Admin")).not.toBeInTheDocument();
    unmount();
    localStorage.clear();
    signIn("admin");
    render(<App />);
    expect(screen.getByText("Admin")).toBeInTheDocument();
  });

  it("account screen: delete needs a second confirmation", async () => {
    signIn();
    const fn = stubApi(() => []);
    render(<App />);
    fireEvent.click(screen.getAllByText("माझे खाते")[0]);
    fireEvent.click(screen.getByText("माझे खाते व सर्व माहिती कायमची हटवा"));
    expect(fn.mock.calls.some(([, init]) => (init as RequestInit | undefined)?.method === "DELETE")).toBe(false);
    fireEvent.click(screen.getByText("होय, कायमचे हटवा"));
    await waitFor(() =>
      expect(fn.mock.calls.some(([u, init]) => String(u).endsWith("/auth/me") && (init as RequestInit)?.method === "DELETE")).toBe(true)
    );
    await waitFor(() => expect(screen.getByText("पहिल्यांदाच? नवीन खाते बनवा")).toBeInTheDocument());
  });
});
