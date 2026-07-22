// Arranca `next dev` liberando antes el puerto por si quedó un servidor viejo
// escuchando (causa típica del error EADDRINUSE en Windows, que dejaba el
// navegador viendo código antiguo). Cross-platform (Windows / macOS / Linux).

import { execSync, spawn } from "node:child_process";

const PORT = Number(process.env.PORT || 5179);
const HOST = "127.0.0.1";

function freePort(port) {
  try {
    if (process.platform === "win32") {
      const out = execSync("netstat -ano -p tcp", { stdio: ["ignore", "pipe", "ignore"] }).toString();
      const pids = new Set();
      for (const line of out.split(/\r?\n/)) {
        const parts = line.trim().split(/\s+/);
        // Proto | Local Address | Foreign Address | State | PID
        if (parts.length >= 5 && /LISTEN/i.test(parts[3]) && parts[1].endsWith(`:${port}`)) {
          pids.add(parts[4]);
        }
      }
      for (const pid of pids) {
        try {
          execSync(`taskkill /PID ${pid} /F`, { stdio: "ignore" });
          console.log(`[dev] Puerto ${port}: proceso ${pid} liberado.`);
        } catch {
          /* el proceso ya no existe */
        }
      }
    } else {
      execSync(`lsof -ti tcp:${port} | xargs -r kill -9`, { stdio: "ignore", shell: "/bin/sh" });
    }
  } catch {
    /* nada escuchando en el puerto → seguir */
  }
}

freePort(PORT);

const child = spawn("next", ["dev", "-H", HOST, "-p", String(PORT)], {
  stdio: "inherit",
  shell: true,
});
child.on("exit", (code) => process.exit(code ?? 0));
