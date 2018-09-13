# coding=utf-8

from django.http import *
from .models import CompoundAdverseEvent, OpenFDACompound, AdverseEvent
import ujson as json
# TODO TODO TODO REVISE IN PYTHON 3
import cgi

# imports by Dale
import urllib2
import psycopg2
import psycopg2.extras
#import time

import mps_AATCcredentials


def rList(nct_id,key):
    l = [d for d in key if d['nct_id'] == nct_id]
    if len(l) < 1:
        return None
    else:
        return l

def main(request):
    """Default to Server Error"""
    return HttpResponseServerError()

def fetch_auto_drug_trial_data(request):
    # This should be replaced by query in the future, testing purposes only
    if(request.POST.get('disease', None) is not None):
        disease = request.POST.get('disease')
    else:
        disease = "nafld"

    #startTime = time.time()
    #print'Starting..')
# https://clinicaltrials.gov/ct2/results?cond=&term=&type=Intr&rslt=With&recrs=e&age_v=&gndr=&intr=&titles=&outc=&spons=&lead=&id=&cntry=US&state=&city=&dist=&locn=&strd_s=&strd_e=&prcd_s=&prcd_e=&sfpd_s=&sfpd_e=&lupd_s=&lupd_e=
    studyIDs = []
    try:
        url = "https://clinicaltrials.gov/ct2/results/download_fields?cond=" + disease + "&term=&type=Intr&rslt=With&recrs=e&age_v=&gndr=&intr=&titles=&outc=&spons=&lead=&id=&cntry=US&state=&city=&dist=&locn=&strd_s=&strd_e=&prcd_s=&prcd_e=&sfpd_s=&sfpd_e=&lupd_s=&lupd_e=&down_count=10000&down_fmt=plain"
        file = urllib2.urlopen(url)
        link = "https://ClinicalTrials.gov/show/"
        for line in file:
            if link in line:
                ID = line[line.find(link)+len(link):line.find(link)+len(link)+11]
                studyIDs.append(ID)
    except:
        return HttpResponse(
            json.dumps({'data':{'nct_id':'','outcomeAll':['','',''],'conditions':'','drugs':'','studies':''}}),
            content_type="application/json"
            )

    #def lst2pgarr(alist):
        #return '{' + ','.join(alist) + '}'


    #studyIDs = (lst2pgarr(studyIDs))


    #print'Collected Study IDs from Clinical Trials: ' + str(time.time() - startTime))
    userName = mps_AATCcredentials.userid
    passWord = mps_AATCcredentials.pw

    try:
        conn = psycopg2.connect(dbname="aact", host="aact-db.ctti-clinicaltrials.org", user=userName, password=passWord, port=5432)
    except Exception, e:
        print "Cannot connect to database"
        print e

    del userName
    del passWord

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    studyInfo = []
    for ID in studyIDs:
        ##printID)
        ID = [ID]
        cur.execute("SELECT nct_id,name,description FROM interventions WHERE \
                    nct_id = ANY(%s)",(ID,))  # (SELECT nct_id FROM conditions WHERE downcase_name= %s )", [condition])
        drugs = cur.fetchall()
        cur.execute("SELECT nct_id,start_date, enrollment, completion_date, \
                    overall_status,phase,results_first_posted_date \
                    FROM studies WHERE nct_id = ANY(%s)",(ID,))
        studies = cur.fetchall()
        #cur.execute("SELECT nct_id,description FROM brief_summaries WHERE nct_id = ANY(%s)",(studyIDs,))
        #brief_summaries = cur.fetchall()
        cur.execute("SELECT nct_id,name FROM conditions WHERE nct_id = ANY(%s)",(ID,))
        conditions = cur.fetchall()
        #cur.execute("SELECT nct_id,agency_class,lead_or_collaborator,name FROM sponsors WHERE nct_id = ANY(%s)",(studyIDs,))
        #sponsors = cur.fetchall()
        #cur.execute("SELECT nct_id,description FROM detailed_descriptions WHERE nct_id = ANY(%s)",(studyIDs,))
        #detailed_descriptions = cur.fetchall()
        #cur.execute("SELECT nct_id,group_type,title,description FROM design_groups WHERE nct_id = ANY(%s)",(studyIDs,))
        #design_groups = cur.fetchall()
        #for i in range(0,len(interventions)):
            #if interventions[i]['intervention_type']=='Drug':
                #drugs.append(interventions[i])
        #cur.execute("SELECT nct_id,outcome_type,measure,time_frame,population,description \
    #                FROM design_outcomes WHERE (nct_id = ANY(%s))",(studyIDs,))
        #design_outcomes = cur.fetchall()
        #cur.execute("SELECT nct_id,gender,minimum_age,maximum_age,population,criteria FROM eligibilities WHERE \
                    #nct_id = ANY(%s)",(studyIDs,))  # (SELECT nct_id FROM conditions WHERE downcase_name= %s )", [condition])
        #eligibilities = cur.fetchall()
        #cur.execute("SELECT nct_id,url,description FROM links WHERE nct_id = ANY(%s)",(studyIDs,))
        #links = cur.fetchall()
        #cur.execute("SELECT nct_id,pmid,reference_type FROM study_references WHERE nct_id = ANY(%s)",(studyIDs,))
        #study_references = cur.fetchall()
        #cur.execute("SELECT nct_id,result_group_id,time_frame,event_type,description,event_count, \
        #            organ_system,adverse_event_term,frequency_threshold FROM reported_events WHERE nct_id = ANY(%s)",(studyIDs,))
        #reported_events = cur.fetchall()
        cur.execute("SELECT id,nct_id,result_type,title,description FROM result_groups \
                    WHERE nct_id = ANY(%s)",(ID,)) # IN (SELECT nct_id FROM conditions WHERE downcase_name= %s )", [condition])
        result_groups = cur.fetchall()
        cur.execute("SELECT nct_id,outcome_id,result_group_id,classification,category,title, \
                    description,units,param_type,param_value,param_value_num, dispersion_type, \
                    dispersion_value, dispersion_value_num, \
                    explanation_of_na FROM outcome_measurements WHERE nct_id = ANY(%s)",(ID,))
        outcome_measurements = cur.fetchall()
        cur.execute("SELECT nct_id,outcome_id,param_type,param_value,p_value_modifier,p_value, \
                    method,method_description,groups_description FROM outcome_analyses WHERE nct_id = ANY(%s)",(ID,))
        outcome_analyses = cur.fetchall()
        cur.execute("SELECT id,nct_id,outcome_type,title,description,time_frame,population,units, \
                    units_analyzed FROM outcomes WHERE nct_id = ANY(%s)",(ID,))
        cur.execute("SELECT * FROM outcomes WHERE nct_id = ANY(%s) AND outcome_type='Primary'",(ID,))
        outcomes = cur.fetchall()

        study = {#'brief_summaries': (item for item in brief_summaries if item["nct_id"] == nct_id).next(), \
                 'conditions': conditions,\
                 #rList(nct_id,conditions), \
                # 'design_groups': rList(nct_id,design_groups), \
                # 'design_outcomes': rList(nct_id,design_outcomes), \
                # 'detailed_descriptions': rList(nct_id,detailed_descriptions), \
                 'drugs': drugs,\
                 #rList(nct_id,drugs), \
                # 'eligibilities': (item for item in eligibilities if item["nct_id"] == nct_id).next(), \
                # 'interventions': rList(nct_id,interventions), \
                # 'links': rList(nct_id,links), \
                 'outcome_analyses': outcome_analyses, \
                 #rList(nct_id,outcome_analyses), \
                 'outcome_measurements': outcome_measurements, \
                 #rList(nct_id,outcome_measurements), \
                 'outcomes': outcomes, \
                 #rList(nct_id, outcomes), \
                # 'reported_events': rList(nct_id,reported_events), \
                 'result_groups': result_groups, \
                 #rList(nct_id,result_groups), \
                # 'sponsors': rList(nct_id,sponsors), \
                 'studies': studies[0], \
                 #'study_references': rList(nct_id,study_references), \
                 'nct_id': studies[0]['nct_id']
                }
        studyInfo.append(study)



    cur.close()
    conn.close()
    #print'All study info collected ' + str(time.time() - startTime))

    outcomeData = []
    for i in range(0, len(studyInfo)):
        for j in range(0, len(studyInfo[i]["outcomes"])):
            outcomeInfo = {'nct_id': studyInfo[i]["nct_id"],\
                            #'enrollment': studyInfo[i]["enrollment"],\
                            'outcomeAll': [studyInfo[i]["outcomes"][j], studyInfo[i]["outcome_measurements"], studyInfo[i]["outcome_analyses"], studyInfo[i]["result_groups"]],\
                            'conditions':studyInfo[i]["conditions"],\
                            'drugs':studyInfo[i]["drugs"],\
                            'studies':studyInfo[i]["studies"]}
            outcomeData.append(outcomeInfo)
    outcomeDataDisplay = {'data': outcomeData}
    #studyData = { 'data' : studyInfo }
    #print'Data formatted and sent to dispaly ' + str(time.time() - startTime))
    return HttpResponse(
        json.dumps(outcomeDataDisplay),
        content_type="application/json"
    )

def fetch_adverse_events_data(request):
    ae_data = list(CompoundAdverseEvent.objects.prefetch_related(
        'compound__compound',
        'event__organ'
    ).all().values(
        'compound_id',
        'compound__compound__name',
        'compound__compound_id',
        # Probably should be, you know, NAME
        'event__event',
        'frequency',
        'compound__estimated_usage',
        # WHY ISN'T THIS JUST NAME??
        'event__organ__organ_name',
        'compound__black_box',
        # SUBJECT TO CHANGE
        'compound__compound__tctc',
        'compound__compound__mps',
        'compound__compound__epa'
    ))

    data = []

    # A serializer would probably better serve us here...
    for ae in ae_data:
        project = u''

        if ae.get('compound__compound__tctc'):
            project += u'TCTC'

        if ae.get('compound__compound__epa'):
            project += u'EPA'

        if ae.get('compound__compound__mps'):
            project += u'MPS'

        if not project:
            project = u'Unassigned'

        organ_name = u''

        if ae.get('event__organ__organ_name'):
            organ_name = ae.get('event__organ__organ_name')

        black_box_warning = False

        if ae.get('compound__black_box'):
            black_box_warning = True

        normalized_reports = u''
        estimated_usage = u''

        if ae.get('compound__estimated_usage'):
            normalized_reports = u'{:,.2f}'.format(
                float(ae.get('frequency')) / ae.get('compound__estimated_usage') * 10000
            )
            estimated_usage = u'{:,}'.format(ae.get('compound__estimated_usage'))

        data.append(
            {
                'view': ae.get('compound_id'),
                'compound': {
                    'id': ae.get('compound__compound_id'),
                    'name': cgi.escape(ae.get('compound__compound__name'))
                },
                'event': {
                    'lower': cgi.escape(ae.get('event__event').lower()),
                    'name': cgi.escape(ae.get('event__event'))
                },
                'number_of_reports': u'{:,}'.format(
                    ae.get('frequency')
                ),
                'normalized_reports': normalized_reports,
                'estimated_usage': estimated_usage,
                'organ': organ_name,
                'black_box_warning': black_box_warning,
                'project': project,
            }
        )

    all_data = {
        'data': data
    }

    return HttpResponse(
        json.dumps(all_data),
        content_type="application/json"
    )


def fetch_aggregate_ae_by_compound(request):
    compounds = OpenFDACompound.objects.all().prefetch_related(
        'compound'
    )

    compound_frequency = {}
    ae_to_compound = {}

    for adverse_event in CompoundAdverseEvent.objects.all().prefetch_related('event', 'compound__compound'):
        compound_frequency.setdefault(adverse_event.compound_id, []).append(adverse_event.frequency)
        ae_to_compound.setdefault(adverse_event.event.event, {}).update({
            adverse_event.compound.compound.name: True
        })

    data = []

    for compound in compounds:
        estimated_usage = u''

        if compound.estimated_usage:
            estimated_usage = u'{:,}'.format(compound.estimated_usage)

        data.append({
            'checkbox': cgi.escape(compound.compound.name),
            'compound': compound.compound.name,
            'estimated_usage': estimated_usage,
            'frequency': u'{:,}'.format(sum(compound_frequency.get(compound.id, [0])))
        })

    all_data = {
        'data': data,
        'ae_to_compound': ae_to_compound
    }

    return HttpResponse(
        json.dumps(all_data),
        content_type="application/json"
    )


def fetch_aggregate_ae_by_event(request):
    adverse_events = AdverseEvent.objects.all().prefetch_related(
        'organ'
    )

    adverse_event_frequency = {}

    for adverse_event in CompoundAdverseEvent.objects.all():
        adverse_event_frequency.setdefault(adverse_event.event_id, []).append(adverse_event.frequency)

    data = []

    for adverse_event in adverse_events:
        frequency = sum(adverse_event_frequency.get(adverse_event.id, [0]))
        organ_name = u''

        if adverse_event.organ:
            organ_name = adverse_event.organ.organ_name

        if frequency:
            data.append({
                'checkbox': cgi.escape(adverse_event.event),
                'event': adverse_event.event,
                'organ': organ_name,
                'frequency': u'{:,}'.format(frequency)
            })

    all_data = {
        'data': data
    }

    return HttpResponse(
        json.dumps(all_data),
        content_type="application/json"
    )

switch = {
    'fetch_adverse_events_data': fetch_adverse_events_data,
    'fetch_aggregate_ae_by_event': fetch_aggregate_ae_by_event,
    'fetch_aggregate_ae_by_compound': fetch_aggregate_ae_by_compound,
    'fetch_auto_drug_trial_data': fetch_auto_drug_trial_data
}


# Should probably consolidate these (DRY)
def ajax(request):
    """Switch to correct function given POST call

    Receives the following from POST:
    call -- What function to redirect to
    """
    post_call = request.POST.get('call', '')

    # Abort if there is no valid call sent to us from Javascript
    if not post_call:
        return main(request)

    # Route the request to the correct handler function
    # and pass request to the functions
    try:
        # select the function from the dictionary
        procedure = switch[post_call]

    # If all else fails, handle the error message
    except KeyError:
        return main(request)

    else:
        # execute the function
        return procedure(request)
