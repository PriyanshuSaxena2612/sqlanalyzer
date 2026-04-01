import sqlglot
import sqlglot.expressions as exp

query = """
    SELECT *
    FROM patients p
    JOIN encounters e ON p.id = e.patient_id
    JOIN claims c ON e.id = c.encounter_id
    LEFT JOIN providers pr ON p.provider_id = pr.id
    WHERE DATE(p.created_at) = '2024-01-01'
"""

tree = sqlglot.parse_one(query, dialect="snowflake")

# 1. SELECT *
stars = list(tree.find_all(exp.Star))

# 2. JOINs
joins = list(tree.find_all(exp.Join))

# 3. Tables touched
tables = list(tree.find_all(exp.Table))

# 4. WHERE clause exists
where = tree.find(exp.Where)

# 5. Subqueries
subqueries = list(tree.find_all(exp.Subquery))

# 6. CTEs
ctes = list(tree.find_all(exp.CTE))

# 7. Non-SARGable filters
# Functions applied directly on columns in WHERE clause
# e.g. DATE(column) = value, UPPER(column) = value
non_sargable = []
if where:
    for func in where.find_all(exp.Anonymous, exp.Func):
        for col in func.find_all(exp.Column):
            non_sargable.append(col)

# 8. Cartesian joins
# JOIN with no ON condition
cartesian = [
    j for j in joins
    if j.args.get("on") is None
    and j.args.get("using") is None
]

# 9. SELECT *  inside subqueries specifically
subquery_stars = []
for sub in subqueries:
    subquery_stars.extend(list(sub.find_all(exp.Star)))

# 10. Query line count
line_count = len(query.strip().split("\n"))

print(f"SELECT *:          {len(stars)}")
print(f"JOINs:             {len(joins)}")
print(f"Tables:            {len(tables)}")
print(f"Has WHERE:         {where is not None}")
print(f"Subqueries:        {len(subqueries)}")
print(f"CTEs:              {len(ctes)}")
print(f"Non-SARGable:      {len(non_sargable)}")
print(f"Cartesian JOINs:   {len(cartesian)}")
print(f"Subquery SELECT *: {len(subquery_stars)}")
print(f"Line count:        {line_count}")