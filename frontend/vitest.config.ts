import { defineConfig } from "vitest/config";

export default defineConfig({
  cacheDir: ".next/vitest-cache",
  test: {
    cache: false,
    environment: "node",
    include: ["lib/motor-escritura/**/*.test.ts"],
  },
});
