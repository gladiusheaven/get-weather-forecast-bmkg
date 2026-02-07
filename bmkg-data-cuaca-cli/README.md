# BMKG Data Cuaca CLI

Small Node.js CLI to fetch weather data from the public repository: https://github.com/infoBMKG/data-cuaca.

## Requirements
- Node.js 18+

## Install
From this repo root:

```bash
cd bmkg-data-cuaca-cli
npm install
```

## Usage
List the root contents (files/folders) from the GitHub API:

```bash
node src/index.js --list
```

List a specific subfolder (example path):

```bash
node src/index.js --list --path data
```

Fetch raw JSON from the raw GitHub content endpoint:

```bash
node src/index.js --path data/aceh.json
```

Fetch raw content without JSON parsing (useful for non-JSON files):

```bash
node src/index.js --path data/aceh.json --raw
```

## Notes
- The `--path` argument is the path inside the `infoBMKG/data-cuaca` repository.
- If you hit GitHub rate limits, set a `GITHUB_TOKEN` in your environment to authenticate requests.
