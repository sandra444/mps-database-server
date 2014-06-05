

UPDATE bioactivities_bioactivity
SET standardized_units = NULL,
    standard_name = NULL,
     standardized_value = NULL;

UPDATE public.bioactivities_bioactivity as v
SET standard_name = s.standard_name,
standardized_units=s.standard_unit,
    standardized_value=value
FROM public.bioactivities_bioactivitytype as s
WHERE v.bioactivity_type = s.chembl_bioactivity and
v.units=s.standard_unit; 

Update public.bioactivities_bioactivity
SET standard_name = 'LogP app',
standardized_units=units,
    standardized_value=value
Where bioactivity_type like 'logPapp';

Update public.bioactivities_bioactivity
SET standard_name = '-Log MIC',
standardized_units=units,
    standardized_value=value
Where bioactivity_type like '-logMIC';

Update public.bioactivities_bioactivity
SET standard_name = 'MST',
standardized_units='days',
    standardized_value=value
Where bioactivity_type like 'MST' and units like 'day';

Update public.bioactivities_bioactivity
SET standard_name = 'Time',
standardized_units='hr',
    standardized_value=value*24
Where bioactivity_type like 'Time' and units in ('day','days');

Update public.bioactivities_bioactivity
SET standard_name = 'Time',
standardized_units='hr',
    standardized_value=value/3600.0
Where bioactivity_type like 'Time' and units in ('s');


Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value*0.001/molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units like 'ug hr%ml%';

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'ug ml-1','ug.mL-1');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value*1000
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'um','uM');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'umol ml-1');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='mg.kg-1',
    standardized_value=value*0.001*molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'umol.kg-1');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value*1000
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'umol/L');

 Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'umol/ml');

 Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value*0.001/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'ng ml-1','ng/ml');


Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value*0.001
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'pmol');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value*10/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'mg/dl','mg dl-1');

 Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value*1000/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'mg ml-1');
 
Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value*1000/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'mg L-1');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value*10000/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'g dl-1','g/dL');
 
Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value/22.0/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'IU/L');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name
from 
public.bioactivities_bioactivitytype as t
Where  s.bioactivity_type = t.chembl_bioactivity and s.standardized_units = t.standard_unit;
 
 


 


 



