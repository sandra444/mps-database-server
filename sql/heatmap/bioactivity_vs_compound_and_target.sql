COPY (
SELECT compound_name,
       target_name,
       INPUT_BIOACTIVITIES_LIST
FROM public.pivot_bioactivity_by_compound_and_target
WHERE target_name in ('Unchecked',
                      'ADMET',
                      'Rattus norvegicus',
                      'Cyclooxygenase-2')
) TO STDOUT WITH CSV HEADER;
