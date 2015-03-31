from compounds.models import Compound
from bioactivities.models import PubChemBioactivity

import urllib, json

# Call this with the command: ./manage.py runscript update_pubchem

# 0.)AID	1.)AID Version	2.)AID Revision	3.)Panel Member ID	4.)SID
# 5.)CID	6.)Bioactivity Outcome	7.)Target GI	8.)Activity Value [uM]
# 9.)Activity Name	10.)Assay Name 11.)Bioassay Type 12.)PubMed ID
# 13.)RNAi 14.)Gene Target if RNAi


def get_bioactivities(name):
    url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/assaysummary/json'.format(name)
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    data = data.get('Table', '')

    if not data:
        return []

    activities = []
    assays = {}

    if data.get('Row',''):
        for entry in data.get('Row'):
            entry = entry.get('Cell','')

            if entry:
                AID = entry[0]
                CID = entry[5]
                outcome = entry[6]
                # The target is only sometimes listed
                target = entry[7]
                value = entry[8]
                # Please note that specifying the units as micromolar is superfluous and thus these strings are removed
                activity_name = entry[9].replace(' (uM)','').replace('_uM','').replace('_MICROM','')
                assay_name = entry[10]

                # TODO Insert code to add/handle Bioactivity Types?
                # Do not add outcome to returned data, assumed to be active
                if AID and CID and outcome == "Active" and value and activity_name:

                    if not AID in assays:
                        assays.update({AID: [len(activities)]})
                    else:
                        assays.get(AID).append(len(activities))

                    final_target = None

                    if target:
                        # TODO code to insert target and set up FK
                        final_target = target

                    activities.append({
                        'assay_id': AID,
                        'compound_id': CID,
                        'target': final_target,
                        'value': value,
                        'activity_name': activity_name,
                        'assay_name': assay_name
                    })

        # Some entries might be empty thus check for assays
        if assays:

            # flat_assays = ','.join([x for x in assays])
            #
            # assay_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{}/summary/json'.format(flat_assays)
            # assay_response = urllib.urlopen(assay_url)
            # assay_data = json.loads(assay_response.read())
            # assay_data = assay_data.get('AssaySummaries').get('AssaySummary')
            #
            # for assay in assay_data:
            #     aid = str(assay.get('AID'))
            #     source = assay.get('SourceName')
            #
            #     activities_to_change = assays.get(aid)
            #
            #     for index in activities_to_change:
            #         activities[index].update({'source':source})

            all_assays = [x for x in assays]
            flat_assays = []

            # Need to split into a series of queries due to the limit on URL length
            for i in range(0,len(all_assays),500):
                batch = ','.join(all_assays[i:i+500])
                flat_assays.append(batch)

            for assay in flat_assays:
                assay_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{}/summary/json'.format(assay)
                assay_response = urllib.urlopen(assay_url)
                assay_data = json.loads(assay_response.read())
                assay_data = assay_data.get('AssaySummaries').get('AssaySummary')

                for assay in assay_data:
                    aid = str(assay.get('AID'))
                    source = assay.get('SourceName')

                    activities_to_change = assays.get(aid)

                    for index in activities_to_change:
                        activities[index].update({'source':source})

        return activities

    else:
        return []

def run():

    # Remove all old bioactivities
    PubChemBioactivity.objects.all().delete()

    success = 0
    fail = 0
    # TODO make pubchem bioactivity entries for each activity
    for compound in Compound.objects.all():
        activities = get_bioactivities(compound.name)
        if activities:
            # Add CID to compound
            if not compound.pubchemid:
                cid = activities[0].get('compound_id')
                compound.pubchemid = cid
                compound.save()

            for activity in activities:
                # Add the bioactivity
                entry = {
                    'assay_id': activity.get('assay_id'),
                    'compound': compound,
                    'target': activity.get('target'),
                    'value': activity.get('value'),
                    'source': activity.get('source'),
                    'activity_name': activity.get('activity_name'),
                    'assay_name': activity.get('assay_name')
                }
                try:
                    PubChemBioactivity.objects.create(locked=True, **entry)
                    print "Success!"
                    success += 1
                except:
                    print "Fail..."
                    fail += 1
        else:
            print "Fail..."
            fail += 1

    print("Failures:{}".format(fail))
    print("Success:{}".format(success))


