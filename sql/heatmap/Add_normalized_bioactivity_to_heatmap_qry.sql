
SELECT compound,target,tbl.bioactivity,AVG(value) as value,units,
AVG(norm_value) as norm_value,organism,target_type
FROM (
SELECT compounds_compound.name as compound, 
        bioactivities_target.name as target, 
        bioactivities_bioactivity.standard_name as bioactivity, 
        bioactivities_bioactivity.standardized_value as value,bioactivities_bioactivity.standardized_units as units,  
        bioactivities_target.organism, 
        bioactivities_target.target_type,
        CASE WHEN agg_tbl.max_value-agg_tbl.min_value <> 0 THEN (standardized_value-agg_tbl.min_value)/(agg_tbl.max_value-agg_tbl.min_value) ELSE 1 END as norm_value
        FROM bioactivities_bioactivity 
        INNER JOIN compounds_compound 
        ON bioactivities_bioactivity.compound_id=compounds_compound.id 
        INNER JOIN bioactivities_target 
        ON bioactivities_bioactivity.target_id=bioactivities_target.id 
        INNER JOIN 
        (SELECT bioactivities_bioactivity.standard_name ,MAX(standardized_value) as max_value,MIN(standardized_value) as min_value
	FROM bioactivities_bioactivity 
	GROUP BY bioactivities_bioactivity.standard_name
        ) as agg_tbl ON bioactivities_bioactivity.standard_name = agg_tbl.standard_name
        ) as tbl
        
        GROUP BY compound,target,tbl.bioactivity,units,organism,target_type
        HAVING AVG(value) IS NOT NULL ;