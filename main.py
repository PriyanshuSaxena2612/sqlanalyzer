import argparse
import json
from core.parser import analyze

def print_results(result):
    print(f"\nScore: {result.final_score}/100")
    print(f"Grade: {result.grade}")
    print(f"\nIssues found: {len(result.issues)}")
    for issue in result.issues:
        print(f"\n  [{issue.severity.upper()}] {issue.rule}")
        print(f"  Problem:    {issue.message}")
        print(f"  Fix:        {issue.suggestion}")
        print(f"  Penalty:    -{issue.penalty} pts")

def save_json(result, output_path):
    data = result.to_dict()
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nReport saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="SQL Query Complexity Analyzer for Snowflake"
    )

    # Mutually exclusive — file or raw query, not both
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "file",
        nargs="?",
        help="Path to a .sql file"
    )
    group.add_argument(
        "--query",
        help="Raw SQL string to analyze"
    )

    # Optional JSON output
    parser.add_argument(
        "--output",
        help="Save results to a JSON file (e.g. report.json)"
    )

    args = parser.parse_args()

    # Get SQL from file or raw string
    if args.file:
        try:
            with open(args.file, "r") as f:
                query = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            return
    else:
        query = args.query

    # Validate not empty
    if not query.strip():
        print("Error: Empty query provided")
        return

    # Analyze
    result = analyze(query)

    # Print to terminal
    print_results(result)

    # Save JSON if requested
    if args.output:
        save_json(result, args.output)

if __name__ == "__main__":
    main()