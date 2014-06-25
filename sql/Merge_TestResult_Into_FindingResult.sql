DELETE 
FROM drugtrials_findingresult as B USING (
   SELECT
  drugtrials_testresult.drug_trial_id, 
    drugtrials_finding.id as finding_id, 
      drugtrials_findingtype.id as finding_type_id, 
  drugtrials_testresult.test_time, 
  drugtrials_testresult.result, 
  drugtrials_testresult.severity, 
  drugtrials_testresult.percent_max, 
  drugtrials_testresult.descriptor_id, 
  drugtrials_testresult.value,  
  drugtrials_testresult.percent_min, 
  drugtrials_testresult.value_units_id, 
  drugtrials_testresult.time_units_id
  
FROM 
  public.drugtrials_testresult, 
  public.drugtrials_test, 
  public.drugtrials_finding, 
  public.drugtrials_testtype, 
  public.drugtrials_findingtype
WHERE 
  drugtrials_testresult.test_name_id = drugtrials_test.id AND
  drugtrials_test.test_name = drugtrials_finding.finding_name AND
  drugtrials_test.test_type_id = drugtrials_testtype.id AND
  drugtrials_testtype.test_type = drugtrials_findingtype.finding_type) as A 
  WHERE B.drug_trial_id = A.drug_trial_id and 
  B.finding_name_id = A.finding_id  ;

INSERT INTO drugtrials_findingresult(drug_trial_id, 
  finding_name_id, 
  finding_time, 
  result, 
  severity, 
  percent_max, 
  descriptor_id, 
  value, 
  percent_min, 
  value_units_id, 
  time_units_id)


SELECT 
   
  drugtrials_testresult.drug_trial_id, 
    drugtrials_finding.id, 
     
  drugtrials_testresult.test_time, 
  drugtrials_testresult.result, 
  drugtrials_testresult.severity, 
  drugtrials_testresult.percent_max, 
  drugtrials_testresult.descriptor_id, 
  drugtrials_testresult.value,  
  drugtrials_testresult.percent_min, 
  drugtrials_testresult.value_units_id, 
  drugtrials_testresult.time_units_id
  
FROM 
  public.drugtrials_testresult, 
  public.drugtrials_test, 
  public.drugtrials_finding, 
  public.drugtrials_testtype, 
  public.drugtrials_findingtype
WHERE 
  drugtrials_testresult.test_name_id = drugtrials_test.id AND
  drugtrials_test.test_name = drugtrials_finding.finding_name AND
  drugtrials_test.test_type_id = drugtrials_testtype.id AND
  drugtrials_testtype.test_type = drugtrials_findingtype.finding_type;
