/**
 * Real SMS OTP via Firebase phone auth (Google delivers the SMS, no DLT needed).
 * Enabled only when VITE_FIREBASE_* variables are set at build time; otherwise the
 * app uses the server's own OTP endpoints. Firebase is loaded lazily on first use.
 */
import type { ConfirmationResult, RecaptchaVerifier } from "firebase/auth";

const cfg = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY as string | undefined,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN as string | undefined,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID as string | undefined,
  appId: import.meta.env.VITE_FIREBASE_APP_ID as string | undefined,
};

export const firebaseEnabled = (): boolean => Boolean(cfg.apiKey && cfg.projectId && cfg.appId);

let confirmation: ConfirmationResult | null = null;
let verifier: RecaptchaVerifier | null = null;

async function auth() {
  const [{ initializeApp, getApps }, fa] = await Promise.all([import("firebase/app"), import("firebase/auth")]);
  const app = getApps()[0] ?? initializeApp(cfg);
  const a = fa.getAuth(app);
  a.languageCode = "mr";
  return { a, fa };
}

/** Sends the SMS. `buttonId` is the element the invisible reCAPTCHA attaches to. */
export async function firebaseSendOtp(phone10: string, buttonId: string): Promise<void> {
  const { a, fa } = await auth();
  if (!verifier) verifier = new fa.RecaptchaVerifier(a, buttonId, { size: "invisible" });
  try {
    confirmation = await fa.signInWithPhoneNumber(a, `+91${phone10}`, verifier);
  } catch (e) {
    verifier.clear();
    verifier = null;
    throw new Error(friendly(e));
  }
}

/** Confirms the code and returns a Firebase ID token for the backend to verify. */
export async function firebaseConfirmOtp(code: string): Promise<string> {
  if (!confirmation) throw new Error("Please request the OTP again.");
  try {
    const cred = await confirmation.confirm(code);
    const token = await cred.user.getIdToken();
    const { a, fa } = await auth();
    await fa.signOut(a); // our own session (PIN + JWT) takes over from here
    return token;
  } catch (e) {
    throw new Error(friendly(e));
  }
}

function friendly(e: unknown): string {
  const code = (e as { code?: string })?.code || "";
  if (code.includes("invalid-verification-code")) return "Wrong OTP";
  if (code.includes("code-expired")) return "OTP expired. Please request a new one.";
  if (code.includes("too-many-requests")) return "Too many attempts. Please try again later.";
  if (code.includes("invalid-phone-number")) return "Invalid mobile number";
  if (code.includes("quota-exceeded")) return "SMS limit reached for today. Please try again tomorrow.";
  return (e as Error)?.message || "Could not send OTP";
}
