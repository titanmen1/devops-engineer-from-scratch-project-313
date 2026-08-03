import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  base: "/",
  server: {
    host: true,
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8080",
      },
      "/r": {
        target: "http://localhost:8080",
      },
    },
  },
});
