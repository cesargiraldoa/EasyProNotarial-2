import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Fija la raíz de tracing a esta carpeta para evitar que Next infiera mal el
  // workspace cuando hay un package-lock.json en la carpeta contenedora.
  outputFileTracingRoot: __dirname,
  generateBuildId: async () => {
    return 'build-' + Date.now()
  }
};

export default nextConfig;
