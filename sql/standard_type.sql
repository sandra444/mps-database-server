

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
SET standard_name = 'Fu',
standardized_units=units,
    standardized_value=value
Where bioactivity_type like 'fu';

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

Update public.bioactivities_bioactivity
SET standard_name = 'Time',
standardized_units='hr',
    standardized_value=value/3600.0*0.001
Where bioactivity_type like 'Time' and units in ('ms');

Update public.bioactivities_bioactivity
SET standard_name = 'Time',
standardized_units='hr',
    standardized_value=value/60
Where bioactivity_type like 'Time' and units in ('min');

Update public.bioactivities_bioactivity
SET standard_name = 'Permeability',
standardized_units='cm s-1',
    standardized_value=value*0.0001
Where bioactivity_type like 'permeability' and units in ('10''-4 cm/s');

Update public.bioactivities_bioactivity
SET standard_name = 'Permeability',
standardized_units='cm s-1',
    standardized_value=value*0.000001
Where bioactivity_type like 'permeability' and units in ('10''-6 cm/s');

Update public.bioactivities_bioactivity
SET standard_name = 'Permeability',
standardized_units='cm s-1',
    standardized_value=value*0.0000001
Where bioactivity_type like 'permeability' and units in ('nm/s');

Update public.bioactivities_bioactivity
SET standard_name = 'Potency',
standardized_units='nM',
    standardized_value=value*1000
Where bioactivity_type like 'Potency' and units in ('uM');

Update public.bioactivities_bioactivity
SET standard_name = 'Activity (mm)',
standardized_units='mm',
    standardized_value=value*10
Where bioactivity_type like 'Activity' and units in ('cm');

Update public.bioactivities_bioactivity
SET standard_name = 'Activity (nM)',
standardized_units='nM',
    standardized_value=value*1000000
Where bioactivity_type like 'Activity' and units in ('mmol/L');

Update public.bioactivities_bioactivity
SET standard_name = 'MIC50',
standardized_units='nM',
    standardized_value=value*1000000000
Where bioactivity_type like 'MIC50' and units in ('mmol/ml');

Update public.bioactivities_bioactivity
SET standard_name = 'Activity (weight)',
standardized_units='g',
    standardized_value=value*0.001
Where bioactivity_type like 'Activity' and units in ('mg');

Update public.bioactivities_bioactivity
SET standard_name = 'Activity (weight)',
standardized_units='g',
    standardized_value=value*0.000000001
Where bioactivity_type like 'Activity' and units in ('ng');

Update public.bioactivities_bioactivity
SET standard_name = 'Activity (weight)',
standardized_units='g',
    standardized_value=value*0.000001
Where bioactivity_type like 'Activity' and units in ('ug');

Update public.bioactivities_bioactivity
SET standard_name = 'ED50 (mg.kg-1)',
standardized_units='mg.kg-1',
    standardized_value=value
Where bioactivity_type like 'ED50' and units in ('mg kg-1 day-1');


Update public.bioactivities_bioactivity
SET standard_name = 'Activity (nM)',
standardized_units='nM',
    standardized_value=value*1000000000
Where bioactivity_type like 'Activity' and units in ('M');

Update public.bioactivities_bioactivity
SET standard_name = 'Papp',
standardized_units='mm',
    standardized_value=value*10
Where bioactivity_type like 'Papp' and units in ('cm s-1');


Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value/molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units like 'ng.hr/ml';

Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value/molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units like 'ug/L/h';



Update public.bioactivities_bioactivity
SET standard_name = 'AUC',
standardized_units='uM hr',
    standardized_value=value
Where bioactivity_type like 'AUC' and units like 'nM.hr';

Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value*1000.0/molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units in('ug hr ml-1','ug hr-1 ml-1','ug.hr/ml','ug/ml/hr');

Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='mL.min-1.kg-1',
    standardized_value=value*1000.0
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'CL' and units in('mL.min-1.g-1');

Update public.bioactivities_bioactivity as s
SET standard_name = 'ID50 (mg.kg-1)',
	standardized_units='mg.kg-1',
    standardized_value=value*molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'ID50' and units in('mmol/Kg');

Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='nM',
    standardized_value=value*1000000.0/molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'Cmax' and units in('ug.mL-1');

Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='nM',
    standardized_value=value*1000.0/molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'Cmax' and units in('ng/ml');


Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value*10000
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( '10''-2 umol/ml');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value/molecular_weight*1000000
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
 and units in( 'umol ml-1','umol/ml');

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
    standardized_value=value*1000/molecular_weight
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
    standardized_value=value
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'pg/ml');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value*1000000/molecular_weight
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
    standardized_value=value*1000000/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'mg L-1');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value*1000000000/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'g dl-1','g/dL');
 
Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='nM',
    standardized_value=value/22.0/molecular_weight*1000000
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'IU/L');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name
from 
public.bioactivities_bioactivitytype as t
Where  s.bioactivity_type = t.chembl_bioactivity and s.standardized_units = t.standard_unit;
 
 


 


 



