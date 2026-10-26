import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["pwa-icon.png"],
      manifest: {
        name: "ArthMitra - Rural Enterprise Advisory",
        short_name: "ArthMitra",
        description: "AI-assisted hyper-local business advisory & financial structuring for rural micro-entrepreneurs",
        theme_color: "#4f46e5",
        background_color: "#f8fafc",
        display: "standalone",
        start_url: "/",
        icons: [
          {
            src: "pwa-icon.png",
            sizes: "192x192",
            type: "image/png",
          },
        ],
      },
    }),
  ],
  server: {
    port: 5173,
    host: true,
  },
});
