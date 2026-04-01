import sqlglot
import sqlglot.expressions as exp
from core.scorer import ScoreResult
from core.rules import (
    check_select_star,
    check_cartesian_join,
    check_join_density,
    check_non_sargable,
    check_missing_where,
    check_subquery_depth,
    check_cte_overuse
)

def analyze(query: str) -> ScoreResult:
    tree = sqlglot.parse_one(query, dialect="snowflake")
    result = ScoreResult()

    # Extract all patterns
    stars = list(tree.find_all(exp.Star))
    joins = list(tree.find_all(exp.Join))
    tables = list(tree.find_all(exp.Table))
    where = tree.find(exp.Where)
    subqueries = list(tree.find_all(exp.Subquery))
    ctes = list(tree.find_all(exp.CTE))
    line_count = len(query.strip().split("\n"))

    # Non-SARGable detection
    # Operators to exclude — these are not functions
    EXCLUDE_TYPES = (
        exp.And,
        exp.Or,
        exp.Not,
        exp.GT,
        exp.GTE,
        exp.LT,
        exp.LTE,
        exp.EQ,
        exp.NEQ,
        exp.Between,
        exp.In,
        exp.Is,
        exp.Like,
        exp.Cast,
    )

    non_sargable = []
    if where:
        for func in where.find_all(exp.Func):
            if isinstance(func, EXCLUDE_TYPES):
                continue
            for col in func.find_all(exp.Column):
                non_sargable.append(col)

    # SELECT * inside subqueries
    subquery_stars = []
    for sub in subqueries:
        subquery_stars.extend(list(sub.find_all(exp.Star)))

    # Cartesian joins
    cartesian = [
        j for j in joins
        if j.args.get("on") is None
        and j.args.get("using") is None
    ]

    # Run all rules and collect issues
    all_issues = (
        check_select_star(stars, subquery_stars) +
        check_cartesian_join(cartesian) +
        check_join_density(joins, tables, line_count) +
        check_non_sargable(non_sargable) +
        check_missing_where(where, tables) +
        check_subquery_depth(subqueries, line_count) +
        check_cte_overuse(ctes, line_count)
    )

    for issue in all_issues:
        result.add_issue(issue)

    return result