

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

--Change CHEMBL bioactivity_type 'ratio' to 'Ratio'
Update public.bioactivities_bioactivity
SET standard_name = 'Ratio',
standardized_units=units,
    standardized_value=value
Where bioactivity_type like 'ratio' and units='Unspecified';

--Change CHEMBL bioactivity_type 'logPapp' to 'LogP app'
Update public.bioactivities_bioactivity
SET standard_name = 'LogP app',
standardized_units=units,
    standardized_value=value
Where bioactivity_type like 'logPapp';

Update public.bioactivities_bioactivity
SET standard_name = 'Papp',
standardized_units='nm/s',
    standardized_value=value*10000000
Where bioactivity_type like 'Papp' and units in('cm s-1','cm/s') and value <1;

Update public.bioactivities_bioactivity
SET standard_name = 'Papp',
standardized_units='nm/s',
    standardized_value=value
Where bioactivity_type like 'Papp' and units ='nm s-1';

Update public.bioactivities_bioactivity
SET standard_name = 'Papp',
standardized_units='nm/s',
    standardized_value=value*10
Where bioactivity_type like 'Papp' and units in ('cm (s 10^6)-1','10''-6 cm/s','10''6cm/s','ucm/s','ucm s-1');


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
    standardized_value=value*1000/molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units in('ug hr ml-1', 'ug.hr/ml','ug/ml/hr','microg/hr/ml','ug/ml.hr');

Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value/molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units in('ng.hr/ml');

Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value/molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units in('ng.hr/ml','ng hr ml-1');



Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value/molecular_weight/60.0
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units in('ng min ml-1');

Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value*1000000/molecular_weight/60.0
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units in('mg min ml-1');


Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units in('uM.hr');

Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value/molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units in('ug/L/h');

Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value*1000/molecular_weight
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units in('mg hr L-1');


Update public.bioactivities_bioactivity as s
SET standard_name = bioactivity_type,
	standardized_units='uM hr',
    standardized_value=value*0.001
from public.compounds_compound as v
Where s.compound_id =v.id and
bioactivity_type like 'AUC' and units in('nM hr');


Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='uM',
    standardized_value=value*0.001/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'ug ml-1','ug.mL-1') and t.standard_unit='uM';

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='uM',
    standardized_value=value
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'um','uM');

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='uM',
    standardized_value=value*0.001
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'umol ml-1') and t.standard_unit='uM';

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
	standardized_units='uM',
    standardized_value=value
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'umol/L') and t.standard_unit='uM';

 Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='uM',
    standardized_value=value*0.001
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'umol/ml') and t.standard_unit='uM';

 Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='uM',
    standardized_value=value/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'ng ml-1','ng/ml') and t.standard_unit='uM';


Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='uM',
    standardized_value=value*0.000001
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'pmol') and t.standard_unit='uM';

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='uM',
    standardized_value=value*0.01/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'mg/dl','mg dl-1') and t.standard_unit='uM';

 Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='uM',
    standardized_value=value/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'mg ml-1') and t.standard_unit='uM';
 
Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='uM',
    standardized_value=value/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'mg L-1') and t.standard_unit='uM';

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='uM',
    standardized_value=value*10/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'g dl-1','g/dL') and t.standard_unit='uM';
 
Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name,
	standardized_units='uM',
    standardized_value=value*0.001/22.0/molecular_weight
from public.compounds_compound as v,
public.bioactivities_bioactivitytype as t
Where s.compound_id =v.id and s.bioactivity_type = t.chembl_bioactivity
 and units in( 'IU/L') and t.standard_unit='uM';

Update public.bioactivities_bioactivity as s
SET standard_name = t.standard_name
from 
public.bioactivities_bioactivitytype as t
Where  s.bioactivity_type = t.chembl_bioactivity and s.standardized_units = t.standard_unit;
 
 


 


 



