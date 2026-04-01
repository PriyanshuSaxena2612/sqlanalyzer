SELECT *
FROM patients p
JOIN encounters e ON p.id = e.patient_id
WHERE DATE(p.created_at) = '2024-01-01'