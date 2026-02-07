import argparse
import json
import sys
from pathlib import Path
from urllib.request import urlopen


def load_source(source: str) -> str:
    if source.startswith("http://") or source.startswith("https://"):
        with urlopen(source) as response:
            return response.read().decode("utf-8")
    return Path(source).read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update cities.json from a provided JSON source."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="URL or file path containing a JSON array with {code, name} objects.",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parents[1] / "app" / "data" / "cities.json"),
        help="Output path for cities.json",
    )
    args = parser.parse_args()

    raw = load_source(args.source)
    payload = json.loads(raw)

    if not isinstance(payload, list):
        raise ValueError("Source must be a JSON array with {code, name} objects.")

    for entry in payload:
        if not isinstance(entry, dict) or "code" not in entry or "name" not in entry:
            raise ValueError("Each entry must be an object with 'code' and 'name'.")

    output_path = Path(args.output)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Updated {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 - keep CLI failure readable
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
