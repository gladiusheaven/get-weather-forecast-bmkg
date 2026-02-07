#!/usr/bin/env node

const GITHUB_API_BASE = "https://api.github.com/repos/infoBMKG/data-cuaca/contents";
const RAW_BASE = "https://raw.githubusercontent.com/infoBMKG/data-cuaca/main";

const args = process.argv.slice(2);
const options = {
  list: args.includes("--list"),
  raw: args.includes("--raw"),
  path: null,
};

for (let i = 0; i < args.length; i += 1) {
  if (args[i] === "--path" && args[i + 1]) {
    options.path = args[i + 1];
  }
}

const headers = {};
if (process.env.GITHUB_TOKEN) {
  headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
}

const exitWithHelp = () => {
  console.log(`Usage:
  --list               List contents from GitHub API
  --path <path>        Path inside infoBMKG/data-cuaca
  --raw                Do not parse JSON when fetching raw content

Examples:
  node src/index.js --list
  node src/index.js --list --path data
  node src/index.js --path data/aceh.json
`);
  process.exit(0);
};

if (args.length === 0) {
  exitWithHelp();
}

const fetchJson = async (url) => {
  const response = await fetch(url, { headers });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }
  return response.json();
};

const fetchRaw = async (url) => {
  const response = await fetch(url, { headers });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }
  return response.text();
};

const main = async () => {
  try {
    if (options.list) {
      const pathSegment = options.path ? `/${options.path}` : "";
      const data = await fetchJson(`${GITHUB_API_BASE}${pathSegment}`);
      console.log(JSON.stringify(data, null, 2));
      return;
    }

    if (!options.path) {
      console.error("Error: --path is required when not using --list.");
      process.exit(1);
    }

    const rawUrl = `${RAW_BASE}/${options.path}`;
    const rawData = await fetchRaw(rawUrl);

    if (options.raw) {
      console.log(rawData);
      return;
    }

    try {
      const json = JSON.parse(rawData);
      console.log(JSON.stringify(json, null, 2));
    } catch (error) {
      console.error("Error: response is not valid JSON. Use --raw to print it as-is.");
      process.exit(1);
    }
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
};

main();
