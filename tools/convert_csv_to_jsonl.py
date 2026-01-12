import subprocess
import json
import sys
import argparse
import pandas as pd
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1] # will make script run from any directory
sys.path.insert(0, str(REPO_ROOT))  # Add repo root to Python path

from models.jailbreak_guardrail import JailbreakGuardrailItem


def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def get_changed_csv_files():
    """Get CSV files changed in the push/PR commit range."""
    # Use GitHub Actions environment variables if available, otherwise use HEAD^..HEAD
    commit_before = os.getenv("GIT_BEFORE") or run("git rev-parse HEAD^")
    commit_after = os.getenv("GIT_AFTER") or run("git rev-parse HEAD")

    print(f"Checking changes between {commit_before} and {commit_after}")

    # shows the status and filename (path) of changed files (note: \t tab separator between status and filename)
    # it shows all files that changed between the previous main commit and the merge commit, i.e., all files introduced or changed by the PR (across all its commits)
    diff = run(f"git diff --name-status {commit_before} {commit_after}").splitlines()
    print("Changed files:")
    for line in diff:
        print(f"  {line}")
    changed_csvs = []

    for line in diff:
        status, path = line.split("\t", 1)
        if status == "D":
            continue
        p = Path(path)
        if p.suffix == ".csv" and "components" in p.parts:
            changed_csvs.append(p)
    return changed_csvs

    
def infer_component_from_path(path: Path):
    """Infer component name from the file path.
    It assumes the path follows the hierarchy: 'components/<component_name>/'.
    """
    try:
        idx = path.parts.index("components") + 1
        return path.parts[idx]
    except Exception:
        print(f"Cannot determine component from {path}")
        sys.exit(1)


def parse_row_with_model(row_dict, component: str):
    """
    Convert CSV row dict into Pydantic model.
    Add more components here as needed.
    """
    if component == "jailbreak_guardrail":
        return JailbreakGuardrailItem(**row_dict)
    else:
        raise NotImplementedError(f"Component {component} not implemented")


def csv_to_jsonl(csv_path: Path, dry_run=True):
    component = infer_component_from_path(csv_path)
    print(f"Processing {csv_path} ({component})")

    # Read CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return False

    # validate and convert rows
    jsonl_records = []
    for i, row in df.iterrows():
        try:
            model_instance = parse_row_with_model(row.to_dict(), component)
            jsonl_records.append(model_instance.model_dump())
        except Exception as e:
            print(f"Validation failed for {csv_path}")
            print(f"   Row {i+1} (line {i+2} in CSV) error: {e}")
            print(f"   Row data: {row.to_dict()}")
            return False

    print(f"Model validation successful: {len(jsonl_records)} rows validated")

    # construct output path: replace /csv/ with /jsonl/
    jsonl_path = Path(str(csv_path).replace("/csv/", "/jsonl/")).with_suffix(".jsonl")
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    # write JSONL
    if dry_run:
        print(f"Would write: {jsonl_path}")
    else:
        with jsonl_path.open("w", encoding="utf-8") as f:
            for obj in jsonl_records:
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        print(f"Written: {jsonl_path}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Convert CSV files to JSONL")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    args = parser.parse_args()

    changed_csvs = get_changed_csv_files()
    
    if not changed_csvs:
        print("No CSV files changed in this commit.")
        return
    
    print(f"Found {len(changed_csvs)} changed CSV file(s)")
    
    failed = []
    for csv_path in changed_csvs:
        if not csv_to_jsonl(csv_path, dry_run=args.dry_run):
            failed.append(csv_path)
    
    if failed:
        print(f"Failed to process {len(failed)} file(s):")
        for f in failed:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"Successfully processed all files")


if __name__ == "__main__":
    main()