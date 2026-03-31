import asyncio
import base64
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import websockets

ROOT = Path(r"C:\EasyProNotarial-2\easypro2")
FRONTEND_URL = "http://127.0.0.1:5179"
BACKEND_URL = "http://127.0.0.1:8000"
BACKEND_DIR = ROOT / "backend"
BACKEND_PYTHON = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
FRONTEND_DIR = ROOT / "frontend"
SCREENSHOT_DIR = ROOT / "artifacts" / "e2e"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
if not CHROME.exists():
    CHROME = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def http_json(url, method="GET", data=None, headers=None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        return resp.status, json.loads(raw) if raw else None


def wait_http(url, timeout=30):
    start = time.time()
    last = None
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                return resp.status
        except Exception as exc:
            last = exc
            time.sleep(0.5)
    raise RuntimeError(f"timeout waiting for {url}: {last}")




class BrowserCDP:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.ws = None
        self._id = 0
        self.pending = {}
        self._listener_task = None

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50_000_000)
        self._listener_task = asyncio.create_task(self._listener())

    async def close(self):
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except BaseException:
                pass
        if self.ws:
            await self.ws.close()

    async def _listener(self):
        async for raw in self.ws:
            message = json.loads(raw)
            if "id" in message:
                fut = self.pending.pop(message["id"], None)
                if fut and not fut.done():
                    if "error" in message:
                        fut.set_exception(RuntimeError(str(message["error"])))
                    else:
                        fut.set_result(message.get("result", {}))

    async def send(self, method, params=None):
        self._id += 1
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        self.pending[self._id] = fut
        await self.ws.send(json.dumps({"id": self._id, "method": method, "params": params or {}}))
        return await fut

class CDP:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.ws = None
        self._id = 0
        self.pending = {}
        self.console = []
        self.exceptions = []
        self.network_failures = []
        self.http_errors = []
        self.page_errors = []
        self._listener_task = None

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50_000_000)
        self._listener_task = asyncio.create_task(self._listener())
        await self.send("Page.enable")
        await self.send("Runtime.enable")
        await self.send("Network.enable")
        await self.send("Log.enable")

    async def close(self):
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except BaseException:
                pass
        if self.ws:
            await self.ws.close()

    async def _listener(self):
        async for raw in self.ws:
            message = json.loads(raw)
            if "id" in message:
                fut = self.pending.pop(message["id"], None)
                if fut and not fut.done():
                    if "error" in message:
                        fut.set_exception(RuntimeError(str(message["error"])))
                    else:
                        fut.set_result(message.get("result", {}))
                continue
            method = message.get("method")
            params = message.get("params", {})
            if method == "Runtime.consoleAPICalled":
                args = []
                for arg in params.get("args", []):
                    args.append(arg.get("value") or arg.get("description") or "")
                self.console.append({"type": params.get("type"), "text": " ".join(map(str, args))})
            elif method == "Runtime.exceptionThrown":
                details = params.get("exceptionDetails", {})
                self.exceptions.append(details.get("text") or str(details))
            elif method == "Log.entryAdded":
                entry = params.get("entry", {})
                text = entry.get("text") or ""
                level = entry.get("level") or "info"
                self.console.append({"type": level, "text": text})
                if level == "error":
                    self.page_errors.append(text)
            elif method == "Network.loadingFailed":
                self.network_failures.append(params)
            elif method == "Network.responseReceived":
                response = params.get("response", {})
                status = int(response.get("status", 0))
                if status >= 400:
                    self.http_errors.append({"url": response.get("url"), "status": status})

    async def send(self, method, params=None):
        self._id += 1
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        self.pending[self._id] = fut
        await self.ws.send(json.dumps({"id": self._id, "method": method, "params": params or {}}))
        return await fut

    async def eval(self, expression, await_promise=True):
        result = await self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": await_promise,
        })
        if result.get("exceptionDetails"):
            raise RuntimeError(str(result["exceptionDetails"]))
        return result.get("result", {}).get("value")

    async def navigate(self, url):
        await self.send("Page.navigate", {"url": url})
        await self.wait_for_ready()

    async def wait_for_ready(self, timeout=30):
        start = time.time()
        while time.time() - start < timeout:
            state = await self.eval("document.readyState")
            if state == "complete":
                return
            await asyncio.sleep(0.25)
        raise RuntimeError("document did not reach readyState=complete")

    async def wait_for(self, js_condition, timeout=30):
        start = time.time()
        while time.time() - start < timeout:
            try:
                ok = await self.eval(f"Boolean({js_condition})")
            except Exception:
                ok = False
            if ok:
                return
            await asyncio.sleep(0.25)
        raise RuntimeError(f"condition timeout: {js_condition}")

    async def screenshot(self, filename):
        result = await self.send("Page.captureScreenshot", {"format": "png", "fromSurface": True})
        path = SCREENSHOT_DIR / filename
        path.write_bytes(base64.b64decode(result["data"]))
        return str(path)


async def main():
    if not CHROME.exists():
        raise RuntimeError("No browser executable found")

    backend = subprocess.Popen(
        [str(BACKEND_PYTHON), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(BACKEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    frontend = subprocess.Popen(
        ["C:\Windows\System32\cmd.exe", "/c", "npm.cmd run start -- --hostname 127.0.0.1 --port 5179"],
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    user_data_dir = Path(tempfile.mkdtemp(prefix="easypro2-chrome-"))
    browser = subprocess.Popen([
        str(CHROME),
        "--headless=new",
        "--disable-gpu",
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}",
        "--window-size=1600,1200",
        "about:blank",
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    cdp = None
    browser_cdp = None
    try:
        wait_http(BACKEND_URL + "/health")
        wait_http(FRONTEND_URL + "/login")
        status, _ = http_json(BACKEND_URL + "/api/v1/auth/login", method="POST", data={"email": "superadmin@easypro.co", "password": "ChangeMe123!"}, headers={"Content-Type": "application/json"})
        if status != 200:
            raise RuntimeError("login api failed before browser test")

        # get browser ws endpoint
        version = None
        for _ in range(40):
            try:
                with urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=2) as resp:
                    version = json.loads(resp.read().decode("utf-8"))
                    break
            except Exception:
                time.sleep(0.25)
        if not version:
            raise RuntimeError("chrome devtools endpoint not available")

        browser_cdp = BrowserCDP(version["webSocketDebuggerUrl"])
        await browser_cdp.connect()
        created_target = await browser_cdp.send("Target.createTarget", {"url": "about:blank"})
        target_id = created_target.get("targetId")
        target = None
        for _ in range(40):
            try:
                with urllib.request.urlopen("http://127.0.0.1:9222/json/list", timeout=5) as resp:
                    targets = json.loads(resp.read().decode("utf-8"))
                    target = next((item for item in targets if item.get("id") == target_id and item.get("webSocketDebuggerUrl")), None)
                    if target:
                        break
            except Exception:
                time.sleep(0.25)
        if not target:
            raise RuntimeError("could not find browser page target")

        cdp = CDP(target["webSocketDebuggerUrl"])
        await cdp.connect()

        evidence = {}

        await cdp.navigate(FRONTEND_URL + "/login")
        await cdp.wait_for("document.querySelector('input[name=email]') && document.querySelector('input[name=password]')")
        evidence["login_before"] = await cdp.screenshot("01-login.png")
        await cdp.eval("""
        (() => {
          const setValue = (selector, value) => {
            const input = document.querySelector(selector);
            if (!input) return false;
            const proto = Object.getPrototypeOf(input);
            const descriptor = Object.getOwnPropertyDescriptor(proto, 'value');
            if (descriptor && descriptor.set) descriptor.set.call(input, value);
            else input.value = value;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
          };
          const emailOk = setValue('input[name=email]', 'superadmin@easypro.co');
          const passwordOk = setValue('input[name=password]', 'ChangeMe123!');
          if (!emailOk || !passwordOk) return false;
          const button = Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Ingresar'));
          if (!button) return false;
          button.click();
          return true;
        })()
        """)
        try:
            await cdp.wait_for("location.pathname === '/dashboard'", timeout=20)
        except Exception:
            print(json.dumps({
                'login_debug_url': await cdp.eval('location.href'),
                'login_debug_text': await cdp.eval('document.body.innerText.slice(0, 1500)'),
                'login_console': cdp.console[-20:],
                'login_http_errors': cdp.http_errors[-20:],
                'login_network_failures': cdp.network_failures[-20:],
                'login_exceptions': cdp.exceptions[-20:],
            }, ensure_ascii=False, indent=2))
            raise
        evidence["dashboard_after_login"] = await cdp.screenshot("02-dashboard-after-login.png")

        await cdp.navigate(FRONTEND_URL + "/dashboard/actos-plantillas")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('poder general')")
        evidence["templates"] = await cdp.screenshot("03-templates.png")

        await cdp.navigate(FRONTEND_URL + "/dashboard/casos")
        try:
            await cdp.wait_for("document.body.innerText.toLowerCase().includes('casos documentales')", timeout=20)
        except Exception:
            print(json.dumps({
                'cases_debug_url': await cdp.eval('location.href'),
                'cases_debug_text': await cdp.eval('document.body.innerText.slice(0, 2000)'),
                'cases_console': cdp.console[-30:],
                'cases_http_errors': cdp.http_errors[-30:],
                'cases_network_failures': cdp.network_failures[-30:],
                'cases_exceptions': cdp.exceptions[-30:],
            }, ensure_ascii=False, indent=2))
            raise
        evidence["cases"] = await cdp.screenshot("04-cases.png")

        await cdp.navigate(FRONTEND_URL + "/dashboard/casos/crear")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('wizard documental inicial para poder general')")
        evidence["wizard_step1"] = await cdp.screenshot("05-wizard-step1.png")

        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Poder General'))?.click(); true")
        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Continuar'))?.click(); true")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('datos generales del caso')")
        evidence["wizard_step2"] = await cdp.screenshot("06-wizard-step2.png")

        async def select_option(label, match):
            expr = f"""
            (() => {{
              const norm = (value) => (value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
              const blocks = Array.from(document.querySelectorAll('div.grid.gap-2.text-sm.font-medium.text-primary'));
              const block = blocks.find(node => norm(node.innerText).includes(norm({json.dumps(label)})));
              if (!block) return false;
              const search = block.querySelector('input');
              if (!search) return false;
              search.value = {json.dumps(match)};
              search.dispatchEvent(new Event('input', {{ bubbles: true }}));
              const buttons = Array.from(block.querySelectorAll('button'));
              const target = buttons.find(btn => norm(btn.textContent).includes(norm({json.dumps(match)})));
              if (!target) return false;
              target.click();
              return true;
            }})()
            """
            return await cdp.eval(expr)

        async def set_text_input(js_expr, value):
            focused = await cdp.eval(f"""
            (() => {{
              const input = {js_expr};
              if (!input) return false;
              const descriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
              if (descriptor && descriptor.set) descriptor.set.call(input, '');
              else input.value = '';
              input.dispatchEvent(new Event('input', {{ bubbles: true }}));
              input.focus();
              if (input.select) input.select();
              return true;
            }})()
            """)
            if not focused:
                raise RuntimeError(f'Input not found for expression: {js_expr}')
            await cdp.send('Input.insertText', {'text': value})
            await asyncio.sleep(0.1)

        async def click_button_in_block(js_expr, text):
            expr = f"""
            (() => {{
              const block = {js_expr};
              if (!block) return false;
              const target = Array.from(block.querySelectorAll('button')).find(btn => (btn.textContent || '').includes({json.dumps(text)}));
              if (!target) return false;
              target.click();
              return true;
            }})()
            """
            ok = await cdp.eval(expr)
            if not ok:
                raise RuntimeError(f'Button {text} not found in block {js_expr}')
            await asyncio.sleep(0.1)

        await select_option('Notaría', 'Caldas')
        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Continuar'))?.click(); true")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('intervinientes')")
        evidence["wizard_step3"] = await cdp.screenshot("07-wizard-step3.png")

        participant_values = [
            {"doc": "10010001", "name": "Carlos Poderdante UI", "profession": "Comerciante", "municipality": "Caldas", "phone": "3001000001", "email": "carlos.poderdante@easypro.co", "address": "Calle 10 # 20-30", "civil": "Soltero(a)"},
            {"doc": "10010002", "name": "Laura Apoderada UI", "profession": "Abogada", "municipality": "Medellin", "phone": "3001000002", "email": "laura.apoderada@easypro.co", "address": "Carrera 40 # 50-60", "civil": "Casado(a)"},
        ]
        for card_index, item in enumerate(participant_values):
            card_expr = f"Array.from(document.querySelectorAll('div.ep-card-soft')).filter(card => (card.innerText || '').toLowerCase().includes('bloque obligatorio'))[{card_index}]"
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[0]", item['doc'])
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[1]", item['name'])
            await set_text_input(f"{card_expr}.querySelector('input[list]')", item['profession'])
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[3]", item['municipality'])
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[4]", item['phone'])
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[5]", item['email'])
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[6]", item['address'])
            await click_button_in_block(f"{card_expr}.querySelectorAll('div.grid.gap-2.text-sm.font-medium.text-primary')[3]", item['civil'])
        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Continuar'))?.click(); true")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('datos del acto')")
        evidence["wizard_step4"] = await cdp.screenshot("08-wizard-step4.png")

        act_values = ['23', 'marzo', '2026', '185000', '35150', '6500', '5200', 'PG-UI-01', '4 hojas', 'Sin cuantía']
        for index, value in enumerate(act_values):
            await set_text_input(f"Array.from(document.querySelectorAll('label input'))[{index}]", value)
        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Continuar'))?.click(); true")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('generar borrador')")
        evidence["wizard_step5"] = await cdp.screenshot("09-wizard-step5.png")

        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Generar borrador Word v1'))?.click(); true")
        try:
            await cdp.wait_for("document.body.innerText.toLowerCase().includes('borrador word v1 generado correctamente')", timeout=25)
        except Exception:
            print(json.dumps({
                'draft_debug_url': await cdp.eval('location.href'),
                'draft_debug_text': await cdp.eval('document.body.innerText.slice(0, 2500)'),
                'draft_console': cdp.console[-40:],
                'draft_http_errors': cdp.http_errors[-40:],
                'draft_network_failures': cdp.network_failures[-40:],
                'draft_exceptions': cdp.exceptions[-40:],
            }, ensure_ascii=False, indent=2))
            raise
        evidence["wizard_done"] = await cdp.screenshot("10-wizard-done.png")

        case_href = await cdp.eval("(() => { const link = Array.from(document.querySelectorAll('a')).find(a => a.textContent.includes('Abrir detalle del caso')); return link ? link.href : ''; })()")
        if not case_href:
            raise RuntimeError('No detail link found after draft generation')
        await cdp.navigate(case_href)
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('detalle del caso') && document.body.innerText.toLowerCase().includes('documentos')")
        evidence["case_detail"] = await cdp.screenshot("11-case-detail.png")
        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Documentos'))?.click(); true")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('exportar word') && document.body.innerText.toLowerCase().includes('documento definitivo')")
        evidence["case_documents"] = await cdp.screenshot("12-case-documents.png")

        body_text = await cdp.eval("document.body.innerText")
        current_url = await cdp.eval("location.href")
        meaningful_network_failures = [item for item in cdp.network_failures if not item.get('canceled')]
        has_draft = ('borrador documental' in body_text.lower()) or ('v1' in body_text.lower())
        has_documents_tab = 'Documentos' in body_text
        has_traceability = 'Trazabilidad' in body_text
        has_runtime_error = 'Application error: a client-side exception has occurred' in body_text

        result = {
            'current_url': current_url,
            'has_draft': has_draft,
            'has_documents_tab': has_documents_tab,
            'has_traceability': has_traceability,
            'has_runtime_error': has_runtime_error,
            'console': cdp.console[-20:],
            'exceptions': cdp.exceptions,
            'network_failures': cdp.network_failures,
            'meaningful_network_failures': meaningful_network_failures,
            'http_errors': cdp.http_errors,
            'page_errors': cdp.page_errors,
            'screenshots': evidence,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))

        if has_runtime_error or cdp.exceptions or meaningful_network_failures or any(item.get('status', 0) >= 500 for item in cdp.http_errors) or not has_draft:
            raise SystemExit(2)
    finally:
        try:
            await cdp.close()
        except Exception:
            pass
        try:
            await browser_cdp.close()
        except Exception:
            pass
        try:
            browser.terminate()
            browser.wait(timeout=5)
        except Exception:
            try:
                browser.kill()
            except BaseException:
                pass
        try:
            backend.terminate()
            backend.wait(timeout=5)
        except Exception:
            try:
                backend.kill()
            except BaseException:
                pass
        shutil.rmtree(user_data_dir, ignore_errors=True)

if __name__ == '__main__':
    asyncio.run(main())

