import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";
import vm from "node:vm";

function makeElement(id = "") {
  return {
    id,
    value: "",
    style: {},
    className: "",
    textContent: "",
    innerHTML: "",
    children: [],
    disabled: false,
    selected: false,
    appendChild(child) {
      this.children.push(child);
    },
    addEventListener(type, handler) {
      this[`on${type}`] = handler;
    },
    focus() {},
    select() {
      this.selected = true;
    },
  };
}

function makeRange(text, options = {}) {
  const range = {
    text,
    selected: false,
    highlights: [],
    GetText: options.getText === false ? undefined : function () {
      return text;
    },
    Select: options.select === false ? undefined : function () {
      this.selected = true;
    },
    SetHighlight: options.highlight === false ? undefined : function (...args) {
      this.highlights.push(args);
    },
  };
  return range;
}

function makeDocument(searchMap = {}) {
  return {
    searches: [],
    Search(text) {
      this.searches.push(text);
      return searchMap[text] || [];
    },
  };
}

function loadSpike(options = {}) {
  const elements = new Map();
  const executeCalls = [];
  const commandCalls = [];
  const controls = options.controls || [];
  const window = {
    setTimeout,
    clearTimeout,
    navigator: { clipboard: { writeText: async () => undefined } },
    Asc: {
      scope: {},
      plugin: {
        info: {},
        executeMethod(name, args, callback) {
          executeCalls.push({ name, args });
          let result = null;
          if (name === "GetAllContentControls") {
            result = controls;
          } else if (name === "AddContentControl") {
            if (options.addContentControl === false) {
              result = null;
            } else {
              const control = {
                InternalId: options.internalId || "cc_1",
                Tag: args[1].Tag,
                Alias: args[1].Alias,
              };
              controls.splice(0, controls.length, control);
              result = control;
            }
          } else if (name === "InsertAndReplaceContentControls") {
            if (options.insertReplace === false) {
              result = null;
            } else {
              if (typeof options.onInsertReplace === "function") {
                options.onInsertReplace(args);
              }
              result = { ok: true };
            }
          } else if (name === "RemoveContentControls") {
            controls.splice(0, controls.length);
            result = { ok: true };
          }
          if (callback) callback(result);
        },
        callCommand(command, close, calc, callback) {
          commandCalls.push({ close, calc });
          const result = command();
          if (callback) callback(result);
        },
      },
    },
  };
  window.window = window;

  const document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, makeElement(id));
      return elements.get(id);
    },
    createElement() {
      return makeElement();
    },
  };

  const context = vm.createContext({
    window,
    document,
    navigator: window.navigator,
    Promise,
    Error,
    JSON,
    Boolean,
    String,
    Array,
    Object,
    Api: options.document ? { GetDocument: () => options.document } : undefined,
    Asc: window.Asc,
  });
  const script = readFileSync(resolve("onlyoffice-plugin/biblioteca-spike/plugin.js"), "utf8");
  vm.runInContext(script, context);
  window.Asc.plugin.init();
  return {
    api: window.__EasyProBibliotecaSpike.test,
    constants: window.__EasyProBibliotecaSpike.constants,
    executeCalls,
    commandCalls,
    controls,
    elements,
  };
}

test("spike config and html use isolated plugin version", () => {
  const html = readFileSync(resolve("onlyoffice-plugin/biblioteca-spike/index.html"), "utf8");
  const config = JSON.parse(readFileSync(resolve("onlyoffice-plugin/biblioteca-spike/config.json"), "utf8"));
  const runtimeIndex = html.indexOf('<script type="text/javascript" src="../v1/plugins.js"></script>');
  const pluginIndex = html.indexOf('<script src="plugin.js?v=0.1.0"></script>');

  assert.equal(config.version, "0.1.0");
  assert.equal(config.variations[0].url, "index.html?v=0.1.0");
  assert.notEqual(config.guid, "asc.{biblioteca-easypro-2026-v1}");
  assert.notEqual(runtimeIndex, -1);
  assert.notEqual(pluginIndex, -1);
  assert.ok(runtimeIndex < pluginIndex);
});

test("zero matches fail safely", async () => {
  const document = makeDocument({});
  const { api } = loadSpike({ document });

  const result = await api.locateRange();

  assert.equal(result.ok, false);
  assert.equal(result.error, "token_not_found");
  assert.equal(api.getReport().test_token_matches, 0);
});

test("one match resolves and reads exact range text", async () => {
  const range = makeRange("EASYPRO_SPIKE_RANGE_2026");
  const document = makeDocument({ EASYPRO_SPIKE_RANGE_2026: [range] });
  const { api } = loadSpike({ document });

  const result = await api.locateRange();

  assert.equal(result.ok, true);
  assert.equal(api.getReport().range.resolved, true);
  assert.equal(api.getReport().range.text_matches, true);
});

test("multiple matches fail and do not select an arbitrary range", async () => {
  const first = makeRange("EASYPRO_SPIKE_RANGE_2026");
  const second = makeRange("EASYPRO_SPIKE_RANGE_2026");
  const document = makeDocument({ EASYPRO_SPIKE_RANGE_2026: [first, second] });
  const { api } = loadSpike({ document });

  const result = await api.selectRange();

  assert.equal(result.ok, false);
  assert.equal(result.error, "token_not_unique");
  assert.equal(first.selected, false);
  assert.equal(second.selected, false);
});

test("missing Search is reported as unsupported failure", async () => {
  const { api } = loadSpike({ document: {} });

  const result = await api.locateRange();

  assert.equal(result.ok, false);
  assert.equal(result.error, "search_unavailable");
  assert.equal(api.getReport().capabilities.search_supported, false);
});

test("missing Select is reported without mutation", async () => {
  const range = makeRange("EASYPRO_SPIKE_RANGE_2026", { select: false });
  const document = makeDocument({ EASYPRO_SPIKE_RANGE_2026: [range] });
  const { api } = loadSpike({ document });

  const result = await api.selectRange();

  assert.equal(result.ok, false);
  assert.equal(result.error, "select_unavailable");
  assert.equal(api.getReport().range.select, "UNSUPPORTED");
});

test("missing SetHighlight is unsupported and SetColor is never used", async () => {
  const range = makeRange("EASYPRO_SPIKE_RANGE_2026", { highlight: false });
  range.SetColor = () => {
    throw new Error("SetColor must not be called");
  };
  const document = makeDocument({ EASYPRO_SPIKE_RANGE_2026: [range] });
  const { api } = loadSpike({ document });

  const result = await api.applyHighlight(false);

  assert.equal(result.ok, false);
  assert.equal(result.error, "highlight_unavailable");
  assert.equal(api.getReport().range.highlight_apply, "UNSUPPORTED");
});

test("highlight can be applied and cleared with SetHighlight only", async () => {
  const range = makeRange("EASYPRO_SPIKE_RANGE_2026");
  const document = makeDocument({ EASYPRO_SPIKE_RANGE_2026: [range] });
  const { api } = loadSpike({ document });

  await api.applyHighlight(false);
  await api.applyHighlight(true);

  assert.deepEqual(range.highlights[0], [255, 242, 102]);
  assert.deepEqual(range.highlights[1], [null]);
  assert.equal(api.getReport().range.highlight_apply, "PASS");
  assert.equal(api.getReport().range.highlight_clear, "PASS");
});

test("content control creation absence is reported", async () => {
  const range = makeRange("EASYPRO_SPIKE_RANGE_2026");
  const document = makeDocument({ EASYPRO_SPIKE_RANGE_2026: [range] });
  const { api, executeCalls } = loadSpike({ document, addContentControl: false });

  await api.createContentControl();

  assert.equal(executeCalls.some((call) => call.name === "AddContentControl"), true);
  assert.equal(api.getReport().capabilities.content_control_create_supported, false);
  assert.equal(api.getReport().content_control.created, false);
});

test("tag is written and read from Content Controls", async () => {
  const range = makeRange("EASYPRO_SPIKE_RANGE_2026");
  const document = makeDocument({ EASYPRO_SPIKE_RANGE_2026: [range] });
  const { api, constants, controls } = loadSpike({ document });

  await api.createContentControl();
  await api.readSpikeControls(true);

  assert.equal(controls[0].Tag, constants.SPIKE_TAG);
  assert.equal(api.getReport().content_control.created, true);
  assert.equal(api.getReport().content_control.tag_read, true);
});

test("content update and restore use InsertAndReplaceContentControls", async () => {
  const searchMap = {
    EASYPRO_SPIKE_RANGE_2026: [makeRange("EASYPRO_SPIKE_RANGE_2026")],
    EASYPRO_SPIKE_UPDATED_2026: [],
  };
  const { api, executeCalls, constants } = loadSpike({
    document: makeDocument(searchMap),
    controls: [{ InternalId: "cc_1", Tag: "easypro:spike:v1:EASYPRO_SPIKE_RANGE_2026" }],
    onInsertReplace(args) {
      const serialized = JSON.stringify(args);
      if (serialized.includes("EASYPRO_SPIKE_UPDATED_2026")) {
        searchMap.EASYPRO_SPIKE_RANGE_2026 = [];
        searchMap.EASYPRO_SPIKE_UPDATED_2026 = [makeRange("EASYPRO_SPIKE_UPDATED_2026")];
      } else {
        searchMap.EASYPRO_SPIKE_RANGE_2026 = [makeRange("EASYPRO_SPIKE_RANGE_2026")];
        searchMap.EASYPRO_SPIKE_UPDATED_2026 = [];
      }
    },
  });

  await api.setContent(constants.UPDATED_TOKEN);
  await api.setContent(constants.TEST_TOKEN);

  const calls = executeCalls.filter((call) => call.name === "InsertAndReplaceContentControls");
  assert.equal(calls.length, 2);
  assert.match(JSON.stringify(calls[0].args), /EASYPRO_SPIKE_UPDATED_2026/);
  assert.match(JSON.stringify(calls[1].args), /EASYPRO_SPIKE_RANGE_2026/);
  assert.equal(api.getReport().content_control.content_updated, true);
  assert.equal(api.getReport().content_control.content_restored, true);
});

test("persistence verification requires one tagged control and one restored token", async () => {
  const document = makeDocument({ EASYPRO_SPIKE_RANGE_2026: [makeRange("EASYPRO_SPIKE_RANGE_2026")] });
  const { api } = loadSpike({
    document,
    controls: [{ InternalId: "cc_1", Tag: "easypro:spike:v1:EASYPRO_SPIKE_RANGE_2026" }],
  });

  const result = await api.verifyPersistence();

  assert.equal(result.ok, true);
  assert.equal(api.getReport().content_control.persisted_after_reopen, true);
});

test("report JSON is safe and contains required structure", async () => {
  const document = makeDocument({ EASYPRO_SPIKE_RANGE_2026: [makeRange("EASYPRO_SPIKE_RANGE_2026")] });
  const { api } = loadSpike({ document });

  await api.detectCapabilities();
  const text = JSON.stringify(api.getReport());

  assert.match(text, /"spike_version":"0.1.0"/);
  assert.match(text, /"capabilities":/);
  assert.doesNotMatch(text, /jwt|storage_path|cookie|cedula|api_key/i);
});

test("plugin source has no destructive APIs or arbitrary ranges[0]", () => {
  const source = readFileSync(resolve("onlyoffice-plugin/biblioteca-spike/plugin.js"), "utf8");

  assert.doesNotMatch(source, /SetColor/);
  assert.doesNotMatch(source, /ReplaceAllText/);
  assert.doesNotMatch(source, /ranges\[0\]/);
});
