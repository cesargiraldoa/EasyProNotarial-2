import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
  cacheDir: ".next/vitest-cache",
  esbuild: {
    jsx: "automatic",
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
  test: {
    cache: false,
    environment: "node",
    include: ["lib/**/*.test.ts", "components/**/*.test.ts"],
  },
});
