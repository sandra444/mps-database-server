--clean existing view

drop view IF EXISTS bioactivity_target_compound_view;

 --create view

create view bioactivity_target_compound_view as
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'IC50')
AND (Bioactivities_bioactivity.standardized_units = 'nM')
AND (AVG(Bioactivities_bioactivity.standardized_value) BETWEEN 0.5 AND 1000000)
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'MIC')
AND (Bioactivities_bioactivity.standardized_units = 'ug.mL-1')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'concentration')
AND (Bioactivities_bioactivity.standardized_units = 'mg/dL')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Cell fraction')
AND (Bioactivities_bioactivity.standardized_units = '%')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Organ weight')
AND (Bioactivities_bioactivity.standardized_units = 'g')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Kd')
AND (Bioactivities_bioactivity.standardized_units = 'nM')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Activity')
AND (Bioactivities_bioactivity.standardized_units = '%')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Potency')
AND (Bioactivities_bioactivity.standardized_units = 'nM')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Cell count')
AND (Bioactivities_bioactivity.standardized_units = 'x10_4/uL')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Ki')
AND (Bioactivities_bioactivity.standardized_units = 'nM')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Inhibition')
AND (Bioactivities_bioactivity.standardized_units = '%')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'EC50')
AND (Bioactivities_bioactivity.standardized_units = 'nM')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'IZ')
AND (Bioactivities_bioactivity.standardized_units = 'mm')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'GI50')
AND (Bioactivities_bioactivity.standardized_units = 'nM')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Mean Corpuscular Hemoglobin')
AND (Bioactivities_bioactivity.standardized_units = 'pg')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Hematocrit')
AND (Bioactivities_bioactivity.standardized_units = '%')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Mean Corpuscular Hemoglobin Concentration')
AND (Bioactivities_bioactivity.standardized_units = '%')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Activated Partial Thromboplastin Time')
AND (Bioactivities_bioactivity.standardized_units = 's')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Prothrombin Time')
AND (Bioactivities_bioactivity.standardized_units = 's')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Mean Corpuscular Volume')
AND (Bioactivities_bioactivity.standardized_units = 'fL')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Fold change')
AND (Bioactivities_bioactivity.standardized_units = 'Unspecified')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'MIC90')
AND (Bioactivities_bioactivity.standardized_units = 'ug.mL-1')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'ED50')
AND (Bioactivities_bioactivity.standardized_units = 'mg.kg-1')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'MIC50')
AND (Bioactivities_bioactivity.standardized_units = 'ug.mL-1')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'T1/2')
AND (Bioactivities_bioactivity.standardized_units = 'hr')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Vdss')
AND (Bioactivities_bioactivity.standardized_units = 'L.kg-1')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'PD50')
AND (Bioactivities_bioactivity.standardized_units = 'mg kg-1')
UNION
SELECT Compounds_compound.name AS compound_name,
       Bioactivities_target.name AS target_name,
       Bioactivities_target.organism,
       Bioactivities_bioactivity.bioactivity_type,
       Bioactivities_bioactivity.standardized_units,
       AVG(Bioactivities_bioactivity.standardized_value) AS avg_standardized_value
FROM Bioactivities_bioactivity
INNER JOIN Bioactivities_assay ON Bioactivities_bioactivity.assay_id = Bioactivities_assay.id
INNER JOIN Bioactivities_target ON Bioactivities_bioactivity.target_id = Bioactivities_target.id
INNER JOIN Compounds_compound ON Bioactivities_bioactivity.compound_id = Compounds_compound.id
WHERE (Bioactivities_bioactivity.operator = '=')
GROUP BY Compounds_compound.name,
         Bioactivities_target.name,
         Bioactivities_target.organism,
         Bioactivities_bioactivity.bioactivity_type,
         Bioactivities_bioactivity.standardized_units HAVING (Bioactivities_bioactivity.bioactivity_type = 'Log10 cfu')
AND (Bioactivities_bioactivity.standardized_units = 'Unspecified');

 --Create pivot table of bioactivity vs compound and target

drop view IF EXISTS pivot_bioactivity_by_compound_and_target;


create view pivot_bioactivity_by_compound_and_target AS
SELECT *
FROM crosstab ( 'SELECT

  compound_name, target_name,bioactivity_type,

  avg_standardized_value



FROM

  public.bioactivity_target_compound_view Order by 1', 'SELECT DISTINCT bioactivity_type FROM   public.bioactivity_target_compound_view

   Order by 1' ) AS (compound_name varchar(200),
                                   target_name varchar(200),
                                               "Activated Partial Thromboplastin Time" float, "Activity" float, "Cell count" float, "Cell fraction" float, "concentration" float, "EC50" float, "ED50" float, "Fold change" float, "GI50" float, "Hematocrit" float, "IC50" float, "Inhibition" float, "IZ" float, "Kd" float, "Ki" float, "Log10 cfu" float, "Mean Corpuscular Hemoglobin" float, "Mean Corpuscular Hemoglobin Concentration" float, "Mean Corpuscular Volume" float, "MIC" float, "MIC50" float, "MIC90" float, "Organ weight" float, "PD50" float, "Potency" float, "Prothrombin Time" float, "T1/2" float, "Vdss" float);