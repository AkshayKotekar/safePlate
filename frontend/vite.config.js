import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // bind 0.0.0.0 so the phone on the same Wi-Fi can reach this dev server
    port: 5173,
    proxy: {
      "/api": { target: "http://localhost:8000", ws: true },
      "/media": "http://localhost:8000",
    },
  },
});
