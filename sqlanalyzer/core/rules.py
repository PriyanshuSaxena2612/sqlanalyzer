from core.scorer import Issue

def check_select_star(stars, subquery_stars):
    issues = []
    if len(stars) > 0:
        issues.append(Issue(
            rule="SELECT_STAR",
            severity="warning",
            penalty=15,
            message=f"SELECT * used {len(stars)} time(s)",
            suggestion="Explicitly name required columns to reduce "
                      "data transfer and improve query clarity"
        ))
    if len(subquery_stars) > 0:
        issues.append(Issue(
            rule="SUBQUERY_SELECT_STAR",
            severity="critical",
            penalty=10,
            message=f"SELECT * used inside {len(subquery_stars)} subquery(s)",
            suggestion="SELECT * in subqueries forces full row "
                      "materialisation — always specify columns"
        ))
    return issues


def check_cartesian_join(cartesian):
    issues = []
    for _ in cartesian:
        issues.append(Issue(
            rule="CARTESIAN_JOIN",
            severity="critical",
            penalty=25,
            message="JOIN with no ON or USING condition detected",
            suggestion="Add an explicit JOIN condition — "
                      "cartesian products grow exponentially with table size"
        ))
    return issues


def check_join_density(joins, tables, line_count):
    issues = []
    if len(tables) == 0:
        return issues
    density = len(joins) / max(line_count, 1)
    if density > 0.3:
        penalty = min(15, round(density * 20))
        issues.append(Issue(
            rule="HIGH_JOIN_DENSITY",
            severity="warning",
            penalty=penalty,
            message=f"{len(joins)} JOINs across {line_count} lines "
                   f"(density: {density:.2f})",
            suggestion="Consider breaking into CTEs or staging tables "
                      "to reduce join complexity per query"
        ))
    return issues


def check_non_sargable(non_sargable):
    issues = []
    # Deduplicate by column name first
    seen = set()
    for col in non_sargable:
        col_name = str(col)
        if col_name not in seen:
            seen.add(col_name)
            issues.append(Issue(
                rule="NON_SARGABLE_FILTER",
                severity="critical",
                penalty=20,
                message=f"Function applied on column '{col}' in WHERE clause "
                       f"prevents index usage",
                suggestion="Rewrite filter to isolate the column — e.g. "
                          "replace DATE(col) = '2024-01-01' with "
                          "col >= '2024-01-01' AND col < '2024-01-02'"
            ))
    return issues


def check_missing_where(where, tables):
    issues = []
    if where is None and len(tables) > 0:
        issues.append(Issue(
            rule="MISSING_WHERE",
            severity="warning",
            penalty=10,
            message="Query has no WHERE clause",
            suggestion="Add a WHERE clause to limit rows scanned — "
                      "full table scans are expensive on large Snowflake tables"
        ))
    return issues


def check_subquery_depth(subqueries, line_count):
    issues = []
    if len(subqueries) > 0:
        depth_penalty = min(10, len(subqueries) * 3)
        issues.append(Issue(
            rule="SUBQUERY_NESTING",
            severity="warning",
            penalty=depth_penalty,
            message=f"{len(subqueries)} nested subquery(s) detected",
            suggestion="Refactor subqueries into CTEs for "
                      "readability and potential optimiser hints"
        ))
    return issues


def check_cte_overuse(ctes, line_count):
    issues = []
    if len(ctes) == 0:
        return issues
    cte_density = len(ctes) / max(line_count, 1)
    if cte_density > 0.15:
        issues.append(Issue(
            rule="CTE_OVERUSE",
            severity="info",
            penalty=5,
            message=f"{len(ctes)} CTEs in {line_count} lines",
            suggestion="Excessive CTEs can prevent Snowflake optimiser "
                      "from pushing predicates — consider consolidating"
        ))
    return issues