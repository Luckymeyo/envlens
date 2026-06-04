const SECRET_WORDS = ["SECRET", "TOKEN", "PASSWORD", "PASS", "PRIVATE", "API_KEY", "ACCESS_KEY"];
const PUBLIC_PREFIXES = ["PUBLIC_", "NEXT_PUBLIC_", "VITE_", "REACT_APP_", "NUXT_PUBLIC_"];
const PLACEHOLDER_VALUES = new Set([
  "",
  "changeme",
  "change_me",
  "change-me",
  "example",
  "example-value",
  "replace-me",
  "replace_me",
  "todo",
  "none",
  "null",
  "password",
  "password123",
  "secret",
  "token",
  "your-api-key",
  "your_api_key",
]);

const PRESETS = {
  nextjs: {
    NODE_ENV: { type: "enum", required: false, default: "development", values: ["development", "test", "production"], description: "Node.js runtime environment." },
    NEXT_TELEMETRY_DISABLED: { type: "boolean", required: false, description: "Disable Next.js anonymous telemetry." },
    PORT: { type: "integer", required: false, description: "Local server port." },
    VERCEL: { type: "boolean", required: false, description: "Set by Vercel when running in its platform." },
    VERCEL_URL: { type: "string", required: false, description: "Deployment URL supplied by Vercel." },
  },
  vite: {
    BASE_URL: { type: "string", required: false, description: "Vite public base path." },
    DEV: { type: "boolean", required: false, description: "Vite development-mode flag." },
    MODE: { type: "string", required: false, description: "Vite mode name." },
    NODE_ENV: { type: "enum", required: false, default: "development", values: ["development", "test", "production"], description: "Node.js runtime environment." },
    PORT: { type: "integer", required: false, description: "Local server port." },
    PROD: { type: "boolean", required: false, description: "Vite production-mode flag." },
    SSR: { type: "boolean", required: false, description: "Vite server-side-rendering flag." },
  },
  fastapi: {
    APP_ENV: { type: "string", required: false, description: "Application environment name." },
    DATABASE_URL: { type: "url", required: false, description: "Database connection URL." },
    HOST: { type: "string", required: false, description: "API server bind host." },
    PORT: { type: "integer", required: false, description: "Local API server port." },
  },
  django: {
    ALLOWED_HOSTS: { type: "string", required: false, description: "Comma-separated Django host allowlist." },
    DATABASE_URL: { type: "url", required: false, description: "Database connection URL." },
    DEBUG: { type: "boolean", required: false, description: "Django debug mode." },
    DJANGO_SETTINGS_MODULE: { type: "string", required: false, description: "Python path to Django settings." },
    SECRET_KEY: { type: "string", required: true, secret: true, description: "Django signing secret." },
  },
  "docker-compose": {
    COMPOSE_PROFILES: { type: "string", required: false, description: "Comma-separated Docker Compose profiles." },
    COMPOSE_PROJECT_NAME: { type: "string", required: false, description: "Docker Compose project name." },
    DOCKER_HOST: { type: "string", required: false, description: "Docker daemon endpoint." },
    PORT: { type: "integer", required: false, description: "Service port commonly passed to Compose." },
  },
};

const SAMPLE = {
  env: [
    "DATABASE_URL=postgres://localhost:5432/envlens",
    "PORT=not-a-number",
    "NODE_ENV=staging",
    "PUBLIC_API_URL=https://api.example.com",
    "NEXT_PUBLIC_SECRET_KEY=replace-me",
  ].join("\n"),
  example: [
    "DATABASE_URL=postgres://localhost:5432/envlens",
    "PORT=3000",
    "NODE_ENV=development",
    "PUBLIC_API_URL=https://api.example.com",
    "OLD_FEATURE_FLAG=false",
  ].join("\n"),
  schema: [
    "DATABASE_URL:",
    "  type: url",
    "  required: true",
    "  description: Database connection string.",
    "",
    "PORT:",
    "  type: integer",
    "  required: true",
    "  default: 3000",
    "  description: Local web server port.",
    "",
    "NODE_ENV:",
    "  type: enum",
    "  values: [development, test, production]",
    "  default: development",
    "  description: Runtime environment.",
    "",
    "PUBLIC_API_URL:",
    "  type: url",
    "  required: true",
    "  public: true",
    "  description: Public API base URL.",
    "",
    "BILLING_TOKEN:",
    "  type: string",
    "  required: true",
    "  secret: true",
    "  description: Server-side billing token.",
  ].join("\n"),
  source: [
    "// file: src/app.ts",
    "const apiUrl = import.meta.env.PUBLIC_API_URL;",
    "const nodeEnv = process.env.NODE_ENV;",
    "const billingToken = process.env.BILLING_TOKEN;",
    "const unsafePublicKey = process.env.NEXT_PUBLIC_SECRET_KEY;",
    "",
    "# file: src/settings.py",
    "import os",
    "DATABASE_URL = os.environ[\"DATABASE_URL\"]",
    "PORT = int(os.getenv(\"PORT\", \"3000\"))",
  ].join("\n"),
};

const state = {
  analysis: null,
  filter: "all",
  activeView: "issues",
  theme: "light",
};

const els = {
  envInput: document.getElementById("envInput"),
  exampleInput: document.getElementById("exampleInput"),
  schemaInput: document.getElementById("schemaInput"),
  sourceInput: document.getElementById("sourceInput"),
  strictMode: document.getElementById("strictMode"),
  scanSource: document.getElementById("scanSource"),
  ignoreKeys: document.getElementById("ignoreKeys"),
  issueList: document.getElementById("issueList"),
  variableRows: document.getElementById("variableRows"),
  variableSearch: document.getElementById("variableSearch"),
  explainKey: document.getElementById("explainKey"),
  explainBody: document.getElementById("explainBody"),
  fixPlanBody: document.getElementById("fixPlanBody"),
  schemaOutput: document.getElementById("schemaOutput"),
  docsOutput: document.getElementById("docsOutput"),
  cliOutput: document.getElementById("cliOutput"),
  exportOutput: document.getElementById("exportOutput"),
  exportFormat: document.getElementById("exportFormat"),
  scoreValue: document.getElementById("scoreValue"),
  scoreMeter: document.getElementById("scoreMeter"),
  errorCount: document.getElementById("errorCount"),
  warningCount: document.getElementById("warningCount"),
  infoCount: document.getElementById("infoCount"),
  keyCount: document.getElementById("keyCount"),
  usageCount: document.getElementById("usageCount"),
  statusDot: document.getElementById("statusDot"),
  statusTitle: document.getElementById("statusTitle"),
  statusText: document.getElementById("statusText"),
  toast: document.getElementById("toast"),
  fileInput: document.getElementById("fileInput"),
  dropZone: document.getElementById("dropZone"),
  themeToggle: document.getElementById("themeToggle"),
  shareState: document.getElementById("shareState"),
};

function parseEnv(text, path) {
  const entries = {};
  const duplicates = [];
  const problems = [];
  const seen = {};

  text.split(/\r?\n/).forEach((raw, index) => {
    const line = raw.trim();
    const lineNumber = index + 1;
    if (!line || line.startsWith("#")) {
      return;
    }

    const normalized = line.startsWith("export ") ? line.slice(7).trim() : line;
    const equals = normalized.indexOf("=");
    if (equals === -1) {
      problems.push({ path, line: lineNumber, message: "expected KEY=value" });
      return;
    }

    const key = normalized.slice(0, equals).trim();
    let value = normalized.slice(equals + 1).trim();
    if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(key)) {
      problems.push({ path, line: lineNumber, message: `invalid env key ${key}` });
      return;
    }
    if ((value.startsWith("\"") && value.endsWith("\"")) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (seen[key]) {
      duplicates.push({ key, path, firstLine: seen[key], duplicateLine: lineNumber });
    }
    seen[key] = seen[key] || lineNumber;
    entries[key] = { key, value, path, line: lineNumber, raw };
  });

  return { path, entries, duplicates, problems, exists: true };
}

function parseSchema(text) {
  const schema = { path: "env.schema.yml", specs: {}, problems: [], exists: text.trim().length > 0 };
  if (!text.trim()) {
    return schema;
  }

  let data;
  try {
    data = text.trim().startsWith("{") ? JSON.parse(text) : parseSimpleYaml(text);
  } catch (error) {
    schema.problems.push({ path: schema.path, line: 1, message: error.message });
    return schema;
  }

  if (!data || typeof data !== "object" || Array.isArray(data)) {
    schema.problems.push({ path: schema.path, line: 1, message: "schema root must be an object" });
    return schema;
  }

  Object.entries(data).forEach(([key, rawSpec]) => {
    schema.specs[key] = normalizeSpec(key, rawSpec);
  });
  return schema;
}

function parseSimpleYaml(text) {
  const result = {};
  let currentKey = null;
  text.split(/\r?\n/).forEach((raw, index) => {
    if (!raw.trim() || raw.trimStart().startsWith("#")) {
      return;
    }
    const indent = raw.length - raw.trimStart().length;
    const line = raw.trim();
    if (indent === 0) {
      if (!line.includes(":")) {
        throw new Error(`line ${index + 1}: expected KEY:`);
      }
      const [key, ...rest] = line.split(":");
      currentKey = key.trim();
      if (!currentKey) {
        throw new Error(`line ${index + 1}: empty schema key`);
      }
      const value = rest.join(":").trim();
      result[currentKey] = value ? parseScalar(value) : {};
      return;
    }

    if (!currentKey) {
      throw new Error(`line ${index + 1}: property without a parent key`);
    }
    if (!line.includes(":")) {
      throw new Error(`line ${index + 1}: expected property: value`);
    }
    const [property, ...rest] = line.split(":");
    const parent = result[currentKey];
    if (!parent || typeof parent !== "object" || Array.isArray(parent)) {
      throw new Error(`line ${index + 1}: cannot add properties to scalar ${currentKey}`);
    }
    parent[property.trim()] = parseScalar(rest.join(":").trim());
  });
  return result;
}

function parseScalar(value) {
  if (value === "") {
    return "";
  }
  const lowered = value.toLowerCase();
  if (["true", "yes", "on"].includes(lowered)) {
    return true;
  }
  if (["false", "no", "off"].includes(lowered)) {
    return false;
  }
  if (["null", "none"].includes(lowered)) {
    return null;
  }
  if (value.startsWith("[") && value.endsWith("]")) {
    const inner = value.slice(1, -1).trim();
    return inner ? inner.split(",").map((item) => parseScalar(item.trim())) : [];
  }
  if ((value.startsWith("\"") && value.endsWith("\"")) || (value.startsWith("'") && value.endsWith("'"))) {
    return value.slice(1, -1);
  }
  return value;
}

function normalizeSpec(key, rawSpec) {
  if (rawSpec === null || rawSpec === undefined) {
    return { key, type: "string", required: true, default: null, values: [], description: "" };
  }
  if (typeof rawSpec === "string") {
    return { key, type: rawSpec.toLowerCase(), required: true, default: null, values: [], description: "" };
  }
  if (typeof rawSpec !== "object" || Array.isArray(rawSpec)) {
    return { key, type: "string", required: true, default: null, values: [], description: "" };
  }
  const defaultValue = rawSpec.default ?? null;
  const values = Array.isArray(rawSpec.values) ? rawSpec.values.map(String) : rawSpec.values ? [String(rawSpec.values)] : [];
  return {
    key,
    type: String(rawSpec.type || "string").toLowerCase(),
    required: rawSpec.required === undefined ? defaultValue === null : Boolean(rawSpec.required),
    default: defaultValue === null ? null : String(defaultValue),
    values,
    description: rawSpec.description ? String(rawSpec.description) : "",
    secret: rawSpec.secret === undefined ? null : Boolean(rawSpec.secret),
    public: rawSpec.public === undefined ? null : Boolean(rawSpec.public),
  };
}

function scanSource(text) {
  const patterns = [
    { language: "javascript", regex: /\bprocess\.env\.([A-Za-z_][A-Za-z0-9_]*)\b/g },
    { language: "javascript", regex: /\bprocess\.env\[['"]([A-Za-z_][A-Za-z0-9_]*)['"]\]/g },
    { language: "javascript", regex: /\bimport\.meta\.env\.([A-Za-z_][A-Za-z0-9_]*)\b/g },
    { language: "javascript", regex: /\bimport\.meta\.env\[['"]([A-Za-z_][A-Za-z0-9_]*)['"]\]/g },
    { language: "python", regex: /\bos\.getenv\(['"]([A-Za-z_][A-Za-z0-9_]*)['"](?:\s*,[^)]*)?\)/g },
    { language: "python", regex: /\bos\.environ\[['"]([A-Za-z_][A-Za-z0-9_]*)['"]\]/g },
    { language: "python", regex: /\bos\.environ\.get\(['"]([A-Za-z_][A-Za-z0-9_]*)['"](?:\s*,[^)]*)?\)/g },
    { language: "go", regex: /\bos\.Getenv\(['"]([A-Za-z_][A-Za-z0-9_]*)['"]\)/g },
    { language: "go", regex: /\bos\.LookupEnv\(['"]([A-Za-z_][A-Za-z0-9_]*)['"]\)/g },
    { language: "ruby", regex: /\bENV\[['"]([A-Za-z_][A-Za-z0-9_]*)['"]\]/g },
    { language: "ruby", regex: /\bENV\.fetch\(['"]([A-Za-z_][A-Za-z0-9_]*)['"](?:\s*,[^)]*)?\)/g },
    { language: "php", regex: /\bgetenv\(['"]([A-Za-z_][A-Za-z0-9_]*)['"]\)/g },
    { language: "php", regex: /\$_ENV\[['"]([A-Za-z_][A-Za-z0-9_]*)['"]\]/g },
    { language: "php", regex: /\$_SERVER\[['"]([A-Za-z_][A-Za-z0-9_]*)['"]\]/g },
  ];
  const usages = [];
  const seen = new Set();
  let currentPath = "source";

  text.split(/\r?\n/).forEach((line, index) => {
    const marker = line.match(/^\s*(?:\/\/|#|--)\s*file:\s*(.+)$/i);
    if (marker) {
      currentPath = marker[1].trim() || currentPath;
      return;
    }
    patterns.forEach(({ language, regex }) => {
      regex.lastIndex = 0;
      let match;
      while ((match = regex.exec(line))) {
        const expression = match[0];
        const fingerprint = `${match[1]}|${currentPath}|${index + 1}|${expression}`;
        if (!seen.has(fingerprint)) {
          seen.add(fingerprint);
          usages.push({ key: match[1], path: currentPath, line: index + 1, language, expression });
        }
      }
    });
  });

  return usages;
}

function analyze() {
  const envFile = parseEnv(els.envInput.value, ".env");
  const exampleFile = parseEnv(els.exampleInput.value, ".env.example");
  const schema = parseSchema(els.schemaInput.value);
  const ignoredKeys = parseIgnoredKeys(els.ignoreKeys.value);
  const selectedPresets = Array.from(document.querySelectorAll("input[name='preset']:checked")).map((input) => input.value);
  selectedPresets.forEach((presetName) => {
    Object.entries(PRESETS[presetName] || {}).forEach(([key, spec]) => {
      if (!schema.specs[key]) {
        schema.specs[key] = { key, ...spec, preset: presetName };
      }
    });
  });

  const usages = (els.scanSource.checked ? scanSource(els.sourceInput.value) : []).filter((usage) => !isIgnored(usage.key, ignoredKeys));
  const issues = [];
  issues.push(...parseIssues(envFile, exampleFile, schema));
  issues.push(...contractIssues(envFile, exampleFile, schema, usages));
  const visibleIssues = issues.filter((issue) => !issue.key || !isIgnored(issue.key, ignoredKeys)).sort(issueSortKey);

  const keys = new Set([
    ...Object.keys(envFile.entries),
    ...Object.keys(exampleFile.entries),
    ...Object.keys(schema.specs),
    ...usages.map((usage) => usage.key),
  ]);
  const visibleKeys = Array.from(keys).filter((key) => !isIgnored(key, ignoredKeys)).sort();

  const analysis = {
    envFile,
    exampleFile,
    schema,
    usages,
    issues: visibleIssues,
    keys: visibleKeys,
    ignoredKeys,
    selectedPresets,
    strict: els.strictMode.checked,
  };
  state.analysis = analysis;
  render();
  saveDraft();
}

function parseIgnoredKeys(text) {
  return text
    .split(/[,\n\s]+/)
    .map((key) => key.trim())
    .filter(Boolean);
}

function isIgnored(key, ignoredKeys) {
  return ignoredKeys.some((pattern) => {
    if (pattern.endsWith("*")) {
      return key.startsWith(pattern.slice(0, -1));
    }
    return key === pattern;
  });
}

function parseIssues(envFile, exampleFile, schema) {
  const issues = [];
  [envFile, exampleFile].forEach((file) => {
    file.problems.forEach((problem) => {
      issues.push({
        severity: "error",
        code: "parse-error",
        key: null,
        message: problem.message,
        path: problem.path,
        line: problem.line,
      });
    });
    file.duplicates.forEach((duplicate) => {
      issues.push({
        severity: "warning",
        code: "duplicate-key",
        key: duplicate.key,
        message: `${duplicate.key} is declared more than once`,
        path: duplicate.path,
        line: duplicate.duplicateLine,
        hint: `first declaration is on line ${duplicate.firstLine}`,
      });
    });
  });
  schema.problems.forEach((problem) => {
    issues.push({
      severity: "error",
      code: "schema-parse-error",
      key: null,
      message: problem.message,
      path: problem.path,
      line: problem.line,
    });
  });
  return issues;
}

function contractIssues(envFile, exampleFile, schema, usages) {
  const issues = [];
  const envKeys = new Set(Object.keys(envFile.entries));
  const exampleKeys = new Set(Object.keys(exampleFile.entries));
  const schemaKeys = new Set(Object.keys(schema.specs));
  const usedKeys = new Set(usages.map((usage) => usage.key));
  const contractKeys = new Set([...envKeys, ...exampleKeys, ...schemaKeys, ...usedKeys]);
  const usageByKey = groupBy(usages, "key");

  contractKeys.forEach((key) => {
    const spec = schema.specs[key];
    const required = spec ? spec.required : exampleKeys.has(key);
    if (required && !envKeys.has(key)) {
      issues.push({
        severity: "error",
        code: "missing-in-env",
        key,
        message: `${key} is required but missing from .env`,
        path: ".env",
        hint: "add the variable or mark it required: false",
      });
    }
  });

  envKeys.forEach((key) => {
    if (!exampleKeys.has(key) && !schemaKeys.has(key)) {
      const entry = envFile.entries[key];
      issues.push({
        severity: "warning",
        code: "undocumented-env",
        key,
        message: `${key} exists in .env but is not documented`,
        path: entry.path,
        line: entry.line,
        hint: "add it to .env.example or env.schema.yml",
      });
    }
    issues.push(...validateEntry(envFile.entries[key], schema.specs[key], false));
  });

  exampleKeys.forEach((key) => {
    issues.push(...validateEntry(exampleFile.entries[key], schema.specs[key], true));
  });

  usedKeys.forEach((key) => {
    if (!exampleKeys.has(key) && !schemaKeys.has(key)) {
      const usage = usageByKey[key][0];
      issues.push({
        severity: "error",
        code: "missing-in-example",
        key,
        message: `${key} is used in ${usage.path} but missing from .env.example`,
        path: usage.path,
        line: usage.line,
        hint: "add it to .env.example so contributors know it exists",
      });
    }
    if (!schemaKeys.has(key)) {
      const usage = usageByKey[key][0];
      issues.push({
        severity: "info",
        code: "schema-missing-used",
        key,
        message: `${key} is used in code but has no schema entry`,
        path: usage.path,
        line: usage.line,
        hint: "add type and description metadata",
      });
    }
  });

  exampleKeys.forEach((key) => {
    if (!usedKeys.has(key) && !schemaKeys.has(key)) {
      const entry = exampleFile.entries[key];
      issues.push({
        severity: "warning",
        code: "unused-example",
        key,
        message: `${key} is listed in .env.example but was not found in scanned code`,
        path: entry.path,
        line: entry.line,
        hint: "remove it if stale or add it to env.schema.yml if external",
      });
    }
  });

  schemaKeys.forEach((key) => {
    const spec = schema.specs[key];
    if (!usedKeys.has(key) && !exampleKeys.has(key) && !spec.preset) {
      issues.push({
        severity: "info",
        code: "schema-unused",
        key,
        message: `${key} is in env.schema.yml but was not found in code or .env.example`,
        path: "env.schema.yml",
        hint: "keep it if it is consumed outside source scanning",
      });
    }
  });

  issues.push(...caseCollisions(envFile));
  issues.push(...caseCollisions(exampleFile));
  return issues;
}

function validateEntry(entry, spec, inExample) {
  const issues = [];
  const secretLike = isSecretName(entry.key, spec);
  const publicLike = isPublicName(entry.key, spec);

  if (spec && spec.required && entry.value === "") {
    issues.push({
      severity: "error",
      code: "empty-required",
      key: entry.key,
      message: `${entry.key} is required but has an empty value`,
      path: entry.path,
      line: entry.line,
    });
  }

  if (spec && entry.value !== "") {
    const typeIssue = validateType(entry, spec);
    if (typeIssue) {
      issues.push(typeIssue);
    }
  }

  if (publicLike && secretLike) {
    issues.push({
      severity: "warning",
      code: "public-secret-name",
      key: entry.key,
      message: `${entry.key} looks public and secret at the same time`,
      path: entry.path,
      line: entry.line,
      hint: "public client-side variables should not contain secrets",
    });
  }

  if (inExample && secretLike && looksLikeRealSecret(entry.value)) {
    issues.push({
      severity: "warning",
      code: "secret-in-example",
      key: entry.key,
      message: `${entry.key} in sample env appears to contain a real secret`,
      path: entry.path,
      line: entry.line,
      hint: "replace it with a clear placeholder",
    });
  }

  if (!inExample && secretLike && weakSecretValue(entry.value)) {
    issues.push({
      severity: "warning",
      code: "weak-secret",
      key: entry.key,
      message: `${entry.key} has a weak placeholder-like value`,
      path: entry.path,
      line: entry.line,
    });
  }

  return issues;
}

function validateType(entry, spec) {
  const value = entry.value;
  const type = spec.type;
  if (["string", "str"].includes(type)) {
    return null;
  }
  if (["number", "float"].includes(type) && Number.isFinite(Number(value))) {
    return null;
  }
  if (["integer", "int"].includes(type) && /^-?\d+$/.test(value)) {
    return null;
  }
  if (["boolean", "bool"].includes(type) && ["1", "0", "true", "false", "yes", "no", "on", "off"].includes(value.toLowerCase())) {
    return null;
  }
  if (type === "url") {
    try {
      const parsed = new URL(value);
      if (parsed.protocol && parsed.host) {
        return null;
      }
    } catch (_error) {
      return typeMismatch(entry, "expected a URL with scheme and host");
    }
  }
  if (type === "email" && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value)) {
    return null;
  }
  if (type === "enum") {
    if (spec.values.includes(value)) {
      return null;
    }
    return {
      severity: "error",
      code: "invalid-enum",
      key: entry.key,
      message: `${entry.key} must be one of: ${spec.values.join(", ")}`,
      path: entry.path,
      line: entry.line,
    };
  }
  if (["number", "float"].includes(type)) {
    return typeMismatch(entry, "expected a number");
  }
  if (["integer", "int"].includes(type)) {
    return typeMismatch(entry, "expected an integer");
  }
  if (["boolean", "bool"].includes(type)) {
    return typeMismatch(entry, "expected a boolean");
  }
  if (type === "url") {
    return typeMismatch(entry, "expected a URL with scheme and host");
  }
  if (type === "email") {
    return typeMismatch(entry, "expected an email address");
  }
  return {
    severity: "warning",
    code: "unknown-type",
    key: entry.key,
    message: `${entry.key} uses unknown schema type ${type}`,
    path: entry.path,
    line: entry.line,
  };
}

function typeMismatch(entry, detail) {
  return {
    severity: "error",
    code: "type-mismatch",
    key: entry.key,
    message: `${entry.key} has value ${JSON.stringify(entry.value)}: ${detail}`,
    path: entry.path,
    line: entry.line,
  };
}

function isSecretName(key, spec) {
  if (spec && spec.secret !== null && spec.secret !== undefined) {
    return spec.secret;
  }
  const upper = key.toUpperCase();
  return SECRET_WORDS.some((word) => upper.includes(word));
}

function isPublicName(key, spec) {
  if (spec && spec.public !== null && spec.public !== undefined) {
    return spec.public;
  }
  const upper = key.toUpperCase();
  return PUBLIC_PREFIXES.some((prefix) => upper.startsWith(prefix));
}

function weakSecretValue(value) {
  const lowered = value.trim().toLowerCase();
  return PLACEHOLDER_VALUES.has(lowered) || (value.length > 0 && value.length < 12);
}

function looksLikeRealSecret(value) {
  const stripped = value.trim();
  if (!stripped || PLACEHOLDER_VALUES.has(stripped.toLowerCase())) {
    return false;
  }
  const providerPrefixes = ["sk_" + "live_", "gh" + "p_", "gh" + "o_", "github" + "_pat_", "xo" + "xb-", "AK" + "IA"];
  if (providerPrefixes.some((prefix) => stripped.includes(prefix))) {
    return true;
  }
  return stripped.length >= 24 && /[A-Za-z]/.test(stripped) && /\d/.test(stripped);
}

function caseCollisions(file) {
  const byLower = {};
  Object.values(file.entries).forEach((entry) => {
    const lower = entry.key.toLowerCase();
    byLower[lower] = byLower[lower] || [];
    byLower[lower].push(entry);
  });
  return Object.values(byLower)
    .filter((entries) => new Set(entries.map((entry) => entry.key)).size > 1)
    .map((entries) => ({
      severity: "warning",
      code: "case-collision",
      key: entries[0].key,
      message: `${file.path} contains keys that differ only by case: ${entries.map((entry) => entry.key).sort().join(", ")}`,
      path: entries[0].path,
      line: entries[0].line,
    }));
}

function render() {
  const analysis = state.analysis;
  if (!analysis) {
    return;
  }
  const counts = countSeverities(analysis.issues);
  const score = Math.max(0, 100 - counts.error * 20 - counts.warning * 8 - counts.info * 2);
  els.scoreValue.textContent = String(score);
  els.scoreMeter.style.width = `${score}%`;
  els.errorCount.textContent = String(counts.error);
  els.warningCount.textContent = String(counts.warning);
  els.infoCount.textContent = String(counts.info);
  els.keyCount.textContent = String(analysis.keys.length);
  els.usageCount.textContent = String(analysis.usages.length);

  els.statusDot.classList.toggle("has-errors", counts.error > 0);
  els.statusDot.classList.toggle("has-warnings", counts.error === 0 && counts.warning > 0);
  els.statusTitle.textContent = counts.error ? "Action needed" : counts.warning ? "Review" : "Clean";
  els.statusText.textContent = analysis.strict && counts.warning && !counts.error
    ? "Strict mode would fail on warnings."
    : `${analysis.keys.length} keys, ${analysis.usages.length} source usages, ${analysis.issues.length} findings.`;

  renderIssues();
  renderVariables();
  renderExplain();
  renderFixPlan();
  els.schemaOutput.value = renderGeneratedSchema(analysis);
  els.docsOutput.value = renderDocs(analysis);
  els.cliOutput.value = renderCli(analysis);
  renderExport();
}

function renderIssues() {
  const analysis = state.analysis;
  const issues = state.filter === "all" ? analysis.issues : analysis.issues.filter((issue) => issue.severity === state.filter);
  if (!issues.length) {
    els.issueList.innerHTML = `<div class="empty-state">No ${state.filter === "all" ? "" : state.filter} findings.</div>`;
    return;
  }
  els.issueList.innerHTML = issues.map((issue) => `
    <article class="issue-card ${escapeHtml(issue.severity)}">
      <div><span class="severity-pill ${escapeHtml(issue.severity)}">${escapeHtml(issue.severity)}</span></div>
      <div>
        <h3>${escapeHtml(issue.key || issue.code)} <span class="source-pill">${escapeHtml(issue.code)}</span></h3>
        <p>${escapeHtml(issue.message)}</p>
        <div class="issue-meta">
          ${issue.path ? `<span class="source-pill">${escapeHtml(issue.path)}${issue.line ? `:${issue.line}` : ""}</span>` : ""}
          ${issue.hint ? `<span class="source-pill">${escapeHtml(issue.hint)}</span>` : ""}
        </div>
      </div>
    </article>
  `).join("");
}

function renderVariables() {
  const analysis = state.analysis;
  const query = els.variableSearch.value.trim().toLowerCase();
  const rows = analysis.keys
    .filter((key) => !query || key.toLowerCase().includes(query))
    .map((key) => {
      const spec = analysis.schema.specs[key];
      const keyIssues = analysis.issues.filter((issue) => issue.key === key);
      const status = keyIssues.some((issue) => issue.severity === "error") ? "problem" : keyIssues.length ? "warn" : "clean";
      const sources = [];
      if (analysis.envFile.entries[key]) sources.push(".env");
      if (analysis.exampleFile.entries[key]) sources.push("example");
      if (spec) sources.push(spec.preset ? `${spec.preset} preset` : "schema");
      if (analysis.usages.some((usage) => usage.key === key)) sources.push("source");
      return `
        <tr>
          <td class="key-cell">${escapeHtml(key)}</td>
          <td>${escapeHtml(spec ? spec.type : inferTypeName(key))}</td>
          <td>${spec ? (spec.required ? "yes" : "no") : analysis.exampleFile.entries[key] ? "yes" : "no"}</td>
          <td>${sources.map((source) => `<span class="source-pill">${escapeHtml(source)}</span>`).join(" ")}</td>
          <td><span class="status-pill ${status}">${status === "clean" ? "clean" : status === "problem" ? "error" : "review"}</span></td>
        </tr>
      `;
    });
  els.variableRows.innerHTML = rows.join("") || `<tr><td colspan="5" class="empty-state">No variables found.</td></tr>`;

  const previous = els.explainKey.value;
  els.explainKey.innerHTML = analysis.keys.map((key) => `<option value="${escapeHtml(key)}">${escapeHtml(key)}</option>`).join("");
  if (analysis.keys.includes(previous)) {
    els.explainKey.value = previous;
  }
}

function renderExplain() {
  const analysis = state.analysis;
  const key = els.explainKey.value || analysis.keys[0];
  if (!key) {
    els.explainBody.innerHTML = `<div class="empty-state">No variable selected.</div>`;
    return;
  }
  const spec = analysis.schema.specs[key];
  const envEntry = analysis.envFile.entries[key];
  const exampleEntry = analysis.exampleFile.entries[key];
  const usages = analysis.usages.filter((usage) => usage.key === key);
  const issues = analysis.issues.filter((issue) => issue.key === key);
  els.explainBody.innerHTML = [
    explainSection("Schema", spec ? [
      `type: ${spec.type}`,
      `required: ${spec.required ? "yes" : "no"}`,
      spec.default !== null && spec.default !== undefined ? `default: ${spec.default}` : null,
      spec.values && spec.values.length ? `values: ${spec.values.join(", ")}` : null,
      spec.description || null,
    ].filter(Boolean) : ["No schema metadata."]),
    explainSection("Env Files", [
      envEntry ? `.env:${envEntry.line}` : ".env missing",
      exampleEntry ? `.env.example:${exampleEntry.line}` : ".env.example missing",
    ]),
    explainSection("Source Usage", usages.length ? usages.map((usage) => `${usage.path}:${usage.line} ${usage.expression}`) : ["No scanned usage."]),
    explainSection("Findings", issues.length ? issues.map((issue) => `${issue.severity}: ${issue.code} - ${issue.message}`) : ["No findings for this key."]),
  ].join("");
}

function explainSection(title, items) {
  return `
    <section class="explain-section">
      <h3>${escapeHtml(title)}</h3>
      <ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </section>
  `;
}

const FIX_ADVICE = {
  "missing-in-env": "Add the required key to the validated env file, or mark it required: false in the schema.",
  "missing-in-example": "Add the used key to .env.example so contributors know it exists.",
  "type-mismatch": "Update the value or correct the schema type.",
  "invalid-enum": "Use one of the allowed enum values, or expand the schema values list.",
  "unused-example": "Remove stale sample keys, or document externally consumed keys in the schema.",
  "undocumented-env": "Add local-only keys to .env.example or env.schema.yml.",
  "public-secret-name": "Rename public client-side variables so they do not look like private secrets.",
  "weak-secret": "Use a real local secret value or keep placeholders only in .env.example.",
  "schema-missing-used": "Add type and description metadata for scanned keys.",
  "schema-unused": "Keep the key if an external platform uses it, otherwise remove stale schema metadata.",
  "duplicate-key": "Keep one declaration per env file.",
  "case-collision": "Normalize key casing so one logical variable has one spelling.",
  "parse-error": "Fix malformed env file lines.",
  "schema-parse-error": "Fix malformed schema syntax.",
};

function renderFixPlan() {
  const analysis = state.analysis;
  if (!analysis.issues.length) {
    els.fixPlanBody.innerHTML = `<div class="empty-state">No fixes needed. The current contract is clean.</div>`;
    return;
  }
  const grouped = groupBy(analysis.issues, "code");
  els.fixPlanBody.innerHTML = Object.entries(grouped).map(([code, issues]) => {
    const severity = issues.some((issue) => issue.severity === "error") ? "error" : issues.some((issue) => issue.severity === "warning") ? "warning" : "info";
    return `
      <article class="plan-card ${severity}">
        <h3>${escapeHtml(code)} <span class="source-pill">${issues.length} finding${issues.length === 1 ? "" : "s"}</span></h3>
        <p>${escapeHtml(FIX_ADVICE[code] || "Review these findings and update the contract.")}</p>
        <ul>
          ${issues.slice(0, 8).map((issue) => `<li>${escapeHtml(issue.key || "-")}: ${escapeHtml(issue.message)}</li>`).join("")}
        </ul>
      </article>
    `;
  }).join("");
}

function renderFixPlanText(analysis) {
  if (!analysis.issues.length) {
    return "envlens fix plan\n\nNo fixes needed. The current contract is clean.";
  }
  const grouped = groupBy(analysis.issues, "code");
  const lines = ["envlens fix plan", ""];
  Object.entries(grouped).forEach(([code, issues]) => {
    lines.push(`${code} (${issues.length})`);
    lines.push(FIX_ADVICE[code] || "Review these findings and update the contract.");
    issues.slice(0, 8).forEach((issue) => {
      lines.push(`- ${issue.key || "-"}: ${issue.message}`);
    });
    lines.push("");
  });
  return lines.join("\n").trimEnd();
}

function renderGeneratedSchema(analysis) {
  if (!analysis.keys.length) {
    return "# No variables detected yet.\n";
  }
  const blocks = [];
  analysis.keys.forEach((key) => {
    const spec = analysis.schema.specs[key];
    const envEntry = analysis.envFile.entries[key] || analysis.exampleFile.entries[key];
    const type = spec ? spec.type : inferTypeName(key);
    const required = spec ? spec.required : Boolean(analysis.usages.some((usage) => usage.key === key) || analysis.exampleFile.entries[key]);
    blocks.push(`${key}:`);
    blocks.push(`  type: ${type}`);
    blocks.push(`  required: ${required ? "true" : "false"}`);
    if (spec && spec.values && spec.values.length) {
      blocks.push(`  values: [${spec.values.join(", ")}]`);
    }
    if (spec && spec.default !== null && spec.default !== undefined) {
      blocks.push(`  default: ${yamlScalar(spec.default)}`);
    } else if (envEntry && envEntry.value && !isSecretName(key, spec)) {
      blocks.push(`  default: ${yamlScalar(envEntry.value)}`);
    }
    if (spec && spec.secret !== null && spec.secret !== undefined) {
      blocks.push(`  secret: ${spec.secret ? "true" : "false"}`);
    } else if (isSecretName(key, spec)) {
      blocks.push("  secret: true");
    }
    if (spec && spec.public !== null && spec.public !== undefined) {
      blocks.push(`  public: ${spec.public ? "true" : "false"}`);
    } else if (isPublicName(key, spec)) {
      blocks.push("  public: true");
    }
    blocks.push(`  description: ${yamlScalar(spec && spec.description ? spec.description : "")}`);
    blocks.push("");
  });
  return blocks.join("\n").trimEnd() + "\n";
}

function yamlScalar(value) {
  const text = String(value ?? "");
  if (text === "" || /[:|#[\]{},\n]/.test(text) || /^\s|\s$/.test(text)) {
    return JSON.stringify(text);
  }
  return text;
}

function renderCli(analysis) {
  const presets = analysis.selectedPresets.map((preset) => ` --preset ${preset}`).join("");
  const ignores = analysis.ignoredKeys.map((key) => ` --ignore ${key}`).join("");
  const strict = analysis.strict ? " --strict" : "";
  const lines = [
    "# Local check",
    `envlens check --env .env --example .env.example --schema env.schema.yml${presets}${ignores}${strict}`,
    "",
    "# GitHub annotations",
    `envlens check --format github --env .env --example .env.example --schema env.schema.yml${presets}${ignores}${strict}`,
    "",
    "# SARIF export",
    `envlens check --format sarif --env .env --example .env.example --schema env.schema.yml${presets}${ignores} > envlens.sarif`,
    "",
    "# Generate docs",
    "envlens docs --schema env.schema.yml > ENVIRONMENT.md",
    "",
    "# Explain a key",
    `envlens explain ${analysis.keys[0] || "DATABASE_URL"} --env .env --example .env.example --schema env.schema.yml`,
    "",
    "# GitHub Actions",
    "name: envlens",
    "on: [pull_request]",
    "jobs:",
    "  envlens:",
    "    runs-on: ubuntu-latest",
    "    steps:",
    "      - uses: actions/checkout@v5",
    "      - uses: Luckymeyo/envlens@main",
    "        with:",
    "          path: .",
    "          format: github",
    `          strict: "${analysis.strict ? "true" : "false"}"`,
    "          summary: \"true\"",
  ];
  return lines.join("\n");
}

function renderDocs(analysis) {
  const rows = [
    "| Variable | Required | Type | Default | Description |",
    "| --- | --- | --- | --- | --- |",
  ];
  analysis.keys.forEach((key) => {
    const spec = analysis.schema.specs[key];
    rows.push(`| ${escapeMarkdown(key)} | ${spec && spec.required ? "yes" : "no"} | ${escapeMarkdown(spec ? spec.type : inferTypeName(key))} | ${escapeMarkdown(spec && spec.default ? spec.default : "")} | ${escapeMarkdown(spec ? spec.description : "")} |`);
  });
  return rows.join("\n");
}

function renderExport() {
  if (!state.analysis) {
    return;
  }
  const format = els.exportFormat.value;
  const renderers = {
    text: renderText,
    json: renderJson,
    github: renderGithub,
    sarif: renderSarif,
  };
  els.exportOutput.value = renderers[format](state.analysis);
  updateExportDownloadName();
}

function renderText(analysis) {
  if (!analysis.issues.length) {
    return "No environment contract issues found.";
  }
  const lines = analysis.issues.map((issue) => {
    const location = issue.path ? ` (${issue.path}${issue.line ? `:${issue.line}` : ""})` : "";
    return `${issue.severity.toUpperCase().padEnd(8)} ${String(issue.key || "-").padEnd(24)} ${issue.code.padEnd(22)} ${issue.message}${location}`;
  });
  const counts = countSeverities(analysis.issues);
  lines.push("");
  lines.push(`${analysis.issues.length} issues found: ${counts.error} errors, ${counts.warning} warnings, ${counts.info} info`);
  return lines.join("\n");
}

function renderJson(analysis) {
  return JSON.stringify({
    summary: {
      issues: analysis.issues.length,
      errors: countSeverities(analysis.issues).error,
      warnings: countSeverities(analysis.issues).warning,
      info: countSeverities(analysis.issues).info,
      keys: analysis.keys.length,
      usages: analysis.usages.length,
      ignored: analysis.ignoredKeys,
    },
    issues: analysis.issues,
    usages: analysis.usages,
  }, null, 2);
}

function renderGithub(analysis) {
  if (!analysis.issues.length) {
    return "No environment contract issues found.";
  }
  return analysis.issues.map((issue) => {
    const command = issue.severity === "error" ? "error" : issue.severity === "warning" ? "warning" : "notice";
    const props = [];
    if (issue.path) props.push(`file=${issue.path}`);
    if (issue.line) props.push(`line=${issue.line}`);
    props.push(`title=${escapeGithub(issue.code)}`);
    const message = issue.hint ? `${issue.message} Hint: ${issue.hint}` : issue.message;
    return `::${command} ${props.join(",")}::${escapeGithub(message)}`;
  }).join("\n");
}

function renderSarif(analysis) {
  const rules = {};
  const results = analysis.issues.map((issue) => {
    rules[issue.code] = {
      id: issue.code,
      name: issue.code,
      shortDescription: { text: titleCase(issue.code.replace(/-/g, " ")) },
      help: { text: issue.hint || issue.message },
    };
    const result = {
      ruleId: issue.code,
      level: { error: "error", warning: "warning", info: "note" }[issue.severity] || "note",
      message: { text: issue.message },
    };
    if (issue.path) {
      result.locations = [{
        physicalLocation: {
          artifactLocation: { uri: issue.path.replace(/\\/g, "/") },
          region: { startLine: issue.line || 1 },
        },
      }];
    }
    return result;
  });
  return JSON.stringify({
    $schema: "https://json.schemastore.org/sarif-2.1.0.json",
    version: "2.1.0",
    runs: [{
      tool: {
        driver: {
          name: "envlens-web",
          informationUri: "https://github.com/Luckymeyo/envlens",
          rules: Object.values(rules).sort((a, b) => a.id.localeCompare(b.id)),
        },
      },
      results,
    }],
  }, null, 2);
}

function groupBy(items, key) {
  return items.reduce((grouped, item) => {
    const value = item[key];
    grouped[value] = grouped[value] || [];
    grouped[value].push(item);
    return grouped;
  }, {});
}

function issueSortKey(a, b) {
  const severityOrder = { error: 0, warning: 1, info: 2 };
  return (severityOrder[a.severity] - severityOrder[b.severity])
    || a.code.localeCompare(b.code)
    || String(a.key || "").localeCompare(String(b.key || ""))
    || String(a.path || "").localeCompare(String(b.path || ""))
    || Number(a.line || 0) - Number(b.line || 0);
}

function countSeverities(issues) {
  return issues.reduce((counts, issue) => {
    counts[issue.severity] += 1;
    return counts;
  }, { error: 0, warning: 0, info: 0 });
}

function inferTypeName(key) {
  const upper = key.toUpperCase();
  if (upper.endsWith("URL") || upper.endsWith("_URL")) return "url";
  if (upper === "PORT" || upper.endsWith("_PORT")) return "integer";
  if (upper.startsWith("IS_") || upper.startsWith("HAS_") || upper.endsWith("_ENABLED")) return "boolean";
  return "string";
}

function titleCase(text) {
  return text.replace(/\b\w/g, (char) => char.toUpperCase());
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeMarkdown(value) {
  return String(value ?? "").replace(/\|/g, "\\|").replace(/\n/g, " ");
}

function escapeGithub(value) {
  return String(value ?? "")
    .replace(/%/g, "%25")
    .replace(/\r/g, "%0D")
    .replace(/\n/g, "%0A")
    .replace(/,/g, "%2C")
    .replace(/:/g, "%3A");
}

function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => showToast("Copied"));
    return;
  }
  const scratch = document.createElement("textarea");
  scratch.value = text;
  document.body.appendChild(scratch);
  scratch.select();
  document.execCommand("copy");
  scratch.remove();
  showToast("Copied");
}

function downloadText(text, filename) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  showToast("Downloaded");
}

function currentPayload() {
  return {
    env: els.envInput.value,
    example: els.exampleInput.value,
    schema: els.schemaInput.value,
    source: els.sourceInput.value,
    ignore: els.ignoreKeys.value,
    strict: els.strictMode.checked,
    scan: els.scanSource.checked,
    theme: state.theme,
    presets: Array.from(document.querySelectorAll("input[name='preset']:checked")).map((input) => input.value),
  };
}

function encodePayload(payload) {
  const bytes = new TextEncoder().encode(JSON.stringify(payload));
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function decodePayload(encoded) {
  const padded = encoded.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - encoded.length % 4) % 4);
  const binary = atob(padded);
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
  return JSON.parse(new TextDecoder().decode(bytes));
}

function copyShareLink() {
  const url = new URL(window.location.href);
  url.hash = `state=${encodePayload(currentPayload())}`;
  copyText(url.toString());
}

function setTheme(theme) {
  state.theme = theme === "dark" ? "dark" : "light";
  document.body.dataset.theme = state.theme;
  localStorage.setItem("envlens-web-theme", state.theme);
}

function toggleTheme() {
  setTheme(state.theme === "dark" ? "light" : "dark");
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.add("is-visible");
  window.setTimeout(() => els.toast.classList.remove("is-visible"), 1400);
}

function loadSample() {
  els.envInput.value = SAMPLE.env;
  els.exampleInput.value = SAMPLE.example;
  els.schemaInput.value = SAMPLE.schema;
  els.sourceInput.value = SAMPLE.source;
  els.ignoreKeys.value = "";
  document.querySelectorAll("input[name='preset']").forEach((input) => {
    input.checked = false;
  });
  document.querySelector("input[name='preset'][value='nextjs']").checked = true;
  analyze();
}

function clearAll() {
  els.envInput.value = "";
  els.exampleInput.value = "";
  els.schemaInput.value = "";
  els.sourceInput.value = "";
  els.ignoreKeys.value = "";
  document.querySelectorAll("input[name='preset']").forEach((input) => {
    input.checked = false;
  });
  analyze();
}

function saveDraft() {
  localStorage.setItem("envlens-web-draft", JSON.stringify(currentPayload()));
}

function restoreDraft() {
  const hashMatch = window.location.hash.match(/^#state=(.+)$/);
  const raw = hashMatch ? null : localStorage.getItem("envlens-web-draft");
  if (hashMatch) {
    try {
      applyPayload(decodePayload(hashMatch[1]));
      analyze();
      showToast("Loaded shared state");
      return;
    } catch (_error) {
      window.location.hash = "";
      showToast("Share link could not be loaded");
    }
  }
  if (!raw) {
    setTheme(localStorage.getItem("envlens-web-theme") || "light");
    loadSample();
    return;
  }
  try {
    applyPayload(JSON.parse(raw));
    analyze();
  } catch (_error) {
    loadSample();
  }
}

function applyPayload(payload) {
  els.envInput.value = payload.env || "";
  els.exampleInput.value = payload.example || "";
  els.schemaInput.value = payload.schema || "";
  els.sourceInput.value = payload.source || "";
  els.ignoreKeys.value = payload.ignore || "";
  els.strictMode.checked = Boolean(payload.strict);
  els.scanSource.checked = payload.scan !== false;
  setTheme(payload.theme || localStorage.getItem("envlens-web-theme") || "light");
  document.querySelectorAll("input[name='preset']").forEach((input) => {
    input.checked = (payload.presets || []).includes(input.value);
  });
}

function handleFiles(files) {
  Array.from(files).forEach((file) => {
    const reader = new FileReader();
    reader.onload = () => assignFile(file.name, String(reader.result || ""));
    reader.readAsText(file);
  });
}

function assignFile(name, content) {
  const lower = name.toLowerCase();
  if (lower.includes("schema") && (lower.endsWith(".yml") || lower.endsWith(".yaml") || lower.endsWith(".json"))) {
    els.schemaInput.value = content;
  } else if (lower.includes("example") || lower.endsWith(".env.example")) {
    els.exampleInput.value = content;
  } else if (lower === ".env" || lower.endsWith(".env") || lower.includes(".env.")) {
    els.envInput.value = content;
  } else {
    const prefix = els.sourceInput.value.trim() ? "\n\n" : "";
    const marker = lower.endsWith(".py") ? "# file:" : "// file:";
    els.sourceInput.value += `${prefix}${marker} ${name}\n${content}`;
  }
  analyze();
}

function wireEvents() {
  document.getElementById("runAnalysis").addEventListener("click", analyze);
  document.getElementById("loadSample").addEventListener("click", loadSample);
  document.getElementById("clearAll").addEventListener("click", clearAll);
  document.getElementById("copySummary").addEventListener("click", () => copyText(renderText(state.analysis)));
  els.shareState.addEventListener("click", copyShareLink);
  els.themeToggle.addEventListener("click", toggleTheme);

  [els.envInput, els.exampleInput, els.schemaInput, els.sourceInput, els.ignoreKeys].forEach((textarea) => {
    textarea.addEventListener("input", debounce(analyze, 220));
  });
  [els.strictMode, els.scanSource, els.exportFormat, els.variableSearch, els.explainKey].forEach((input) => {
    input.addEventListener("input", input === els.exportFormat ? () => {
      renderExport();
      updateExportDownloadName();
    } : input === els.variableSearch ? renderVariables : input === els.explainKey ? renderExplain : analyze);
  });
  document.querySelectorAll("input[name='preset']").forEach((input) => input.addEventListener("change", analyze));

  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeView = button.dataset.view;
      document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("is-active", tab === button));
      document.querySelectorAll(".view-panel").forEach((panel) => panel.classList.toggle("is-visible", panel.id === `view-${state.activeView}`));
    });
  });

  document.querySelectorAll(".segment").forEach((button) => {
    button.addEventListener("click", () => {
      state.filter = button.dataset.filter;
      document.querySelectorAll(".segment").forEach((segment) => segment.classList.toggle("is-active", segment === button));
      renderIssues();
    });
  });

  document.querySelectorAll("[data-copy-target]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.getElementById(button.dataset.copyTarget);
      copyText(target.value);
    });
  });
  document.querySelectorAll("[data-copy-render]").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.copyRender === "fixplan") {
        copyText(renderFixPlanText(state.analysis));
      }
    });
  });
  document.querySelectorAll("[data-download-target]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.getElementById(button.dataset.downloadTarget);
      downloadText(target.value, button.dataset.filename || "envlens-output.txt");
    });
  });

  els.fileInput.addEventListener("change", (event) => handleFiles(event.target.files));
  ["dragenter", "dragover"].forEach((type) => {
    els.dropZone.addEventListener(type, (event) => {
      event.preventDefault();
      els.dropZone.classList.add("is-dragging");
    });
  });
  ["dragleave", "drop"].forEach((type) => {
    els.dropZone.addEventListener(type, (event) => {
      event.preventDefault();
      els.dropZone.classList.remove("is-dragging");
    });
  });
  els.dropZone.addEventListener("drop", (event) => handleFiles(event.dataTransfer.files));
}

function updateExportDownloadName() {
  const button = document.querySelector("[data-download-target='exportOutput']");
  if (!button) {
    return;
  }
  const filenames = {
    text: "envlens-report.txt",
    json: "envlens-report.json",
    github: "envlens-annotations.txt",
    sarif: "envlens.sarif",
  };
  button.dataset.filename = filenames[els.exportFormat.value] || "envlens-report.txt";
}

function debounce(fn, wait) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = window.setTimeout(() => fn(...args), wait);
  };
}

wireEvents();
restoreDraft();
