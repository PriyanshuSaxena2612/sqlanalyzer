# sqlanalyzer

> Stop bad SQL from reaching production. Save compute. Save money.

sqlanalyzer is a static analysis tool for Snowflake SQL queries. It parses your SQL using an Abstract Syntax Tree (AST), detects performance anti-patterns, and scores your query from 0–100 — before it ever hits your warehouse.

---

## Why This Exists

Production SQL is expensive. A single poorly written query with a missing WHERE clause, a cartesian join, or a function wrapped around an indexed column can silently cost your company thousands in Snowflake compute credits — and nobody notices until the bill arrives.

sqlanalyzer was built after seeing too many queries like this reach production:

```sql
-- This looks fine. It isn't.
SELECT *
FROM patients p
JOIN encounters e ON p.id = e.patient_id
WHERE DATE(p.created_at) = '2024-01-01'
```

Two issues. 35/100. Moderate risk. Caught before execution.

---

## What It Detects

| Rule | Severity | Description |
|---|---|---|
| `SELECT_STAR` | Warning | SELECT * increases data transfer and breaks on schema changes |
| `NON_SARGABLE_FILTER` | Critical | Functions on columns in WHERE prevent index usage — full table scan |
| `CARTESIAN_JOIN` | Critical | JOIN with no ON condition — row count explodes exponentially |
| `HIGH_JOIN_DENSITY` | Warning | Too many JOINs relative to query size |
| `MISSING_WHERE` | Warning | No WHERE clause — full table scan on every table |
| `SUBQUERY_NESTING` | Warning | Nested subqueries — consider refactoring to CTEs |
| `SUBQUERY_SELECT_STAR` | Critical | SELECT * inside subquery forces full row materialisation |
| `CTE_OVERUSE` | Info | Excessive CTEs can prevent Snowflake optimiser from pushing predicates |

---

## Scoring

Queries are scored **0–100** based on weighted, context-aware penalties:

| Score | Grade | Meaning |
|---|---|---|
| 0–30 | ✅ Clean | Good to go |
| 31–60 | ⚠️ Moderate | Review recommended |
| 61–85 | 🔴 High | Likely performance issues |
| 86–100 | 💀 Critical | Needs refactoring before production |

Penalties are **context-aware** — not hardcoded thresholds. A query with 5 JOINs across 200 lines scores differently than 5 JOINs across 15 lines.

---

## Installation

```bash
git clone https://github.com/PriyanshuSaxena2612/sqlanalyzer.git
cd sqlanalyzer
pip install -r requirements.txt
```

---

## Usage

**Analyze a .sql file:**
```bash
python main.py query.sql
```

**Analyze a raw SQL string:**
```bash
python main.py --query "SELECT * FROM patients WHERE DATE(created_at) = '2024-01-01'"
```

**Save results to JSON:**
```bash
python main.py query.sql --output report.json
```

---

## Example Output

```
Score: 35/100
Grade: Moderate

Issues found: 2

  [WARNING] SELECT_STAR
  Problem:    SELECT * used 1 time(s)
  Fix:        Explicitly name required columns to reduce data transfer

  [CRITICAL] NON_SARGABLE_FILTER
  Problem:    Function applied on column 'created_at' prevents index usage
  Fix:        Replace DATE(col) = '2024-01-01' with
              col >= '2024-01-01' AND col < '2024-01-02'
```

---

## JSON Output

```json
{
  "final_score": 35,
  "grade": "Moderate",
  "issues": [
    {
      "rule": "SELECT_STAR",
      "severity": "warning",
      "penalty": 15,
      "message": "SELECT * used 1 time(s)",
      "suggestion": "Explicitly name required columns"
    },
    {
      "rule": "NON_SARGABLE_FILTER",
      "severity": "critical",
      "penalty": 20,
      "message": "Function applied on column 'created_at' prevents index usage",
      "suggestion": "Rewrite filter to isolate the column"
    }
  ]
}
```

---

## Project Structure

```
sqlanalyzer/
├── core/
│   ├── __init__.py
│   ├── parser.py      # AST parsing and pattern extraction
│   ├── scorer.py      # ScoreResult and Issue dataclasses
│   └── rules.py       # Individual rule definitions
├── main.py            # CLI entry point
├── requirements.txt
└── README.md
```

---

## How It Works

1. SQL is parsed into an **Abstract Syntax Tree** using [sqlglot](https://github.com/tobymao/sqlglot) with Snowflake dialect
2. The AST is traversed to extract patterns — JOINs, WHERE conditions, CTEs, subqueries
3. Each pattern is evaluated by a **rule function** that returns weighted, context-aware penalties
4. Penalties are accumulated into a **ScoreResult** with a final 0–100 score and grade
5. Results are printed to terminal and optionally saved as JSON

---

## Roadmap

- [ ] Web UI (Flask)
- [ ] Folder input — analyze all .sql files in a directory
- [ ] Schema-aware analysis — provide DDL to detect non-indexed column filters
- [ ] CI/CD integration — fail pipeline if score exceeds threshold
- [ ] Support for additional dialects — BigQuery, Postgres

---

## Contributing

Rules are modular by design — adding a new detection rule takes under 10 lines. See `core/rules.py` for examples. PRs welcome.

---

## Dialect Support

Currently tuned for **Snowflake SQL**. Other dialects are partially supported via sqlglot's dialect system but not tested.

---

## Acknowledgements

Built on top of [sqlglot](https://github.com/tobymao/sqlglot) — an outstanding open source SQL parser.
