from compounds.models import Compound
from drugtrials.models import OpenFDACompound, CompoundAdverseEvent, AdverseEvent

import urllib, json

# Call this with the command: ./manage.py runscript update_adverse_events

def get_event_frequency(generic_name):
    events = []
    try:
        url = 'https://api.fda.gov/drug/event.json?api_key=uCe1k5sGtf3nadB8X5kyswJ6qZdzGyuIeYKxMClA&search=patient.drug.openfda.generic_name:"{}"&count=patient.reaction.reactionmeddrapt.exact'.format(generic_name)
        response = urllib.urlopen(url)
        data = json.loads(response.read())

        # Automatically take the first result, if it exists
        if data.get('results',''):
            first = data.get('results')[0]
            events.append((first.get('term'),first.get('count')))
        else:
            return []

        data_after_first = data.get('results','')[1:]
        highest_count = events[0][1]

        for event in data_after_first:
            term = event.get('term')
            count = event.get('count')

            # Only take the most frequent event and every event that is at least 50% the frequency
            if count >= highest_count*0.50:
                events.append((term,count))
            # End if the event count is smaller (data should be in order)
            else:
                return events

        # In the off chance that all of the events are at least 50%
        return events

    except:
        return []

def run():
    # existing = dict.fromkeys(AdverseEvent.objects.all().values_list('event', flat=True), True)

    for compound in Compound.objects.all():
        events = get_event_frequency(compound.name)

        if events:
            # Test to see if model already exists
            try:
                compound_model = OpenFDACompound.objects.get(compound=compound)

                # Delete all old adverse events
                adverse_events = CompoundAdverseEvent.objects.filter(compound=compound_model)

                for adverse_event in adverse_events:
                    if adverse_event.compound.id == compound_model.id:
                        adverse_event.delete()

            # Make a new OpenFDACompound model if it does not already exist
            except:
                compound_model = OpenFDACompound(compound=compound)
                compound_model.save()

            for event in events:
                # Replace ^ with '
                adverse_event = event[0].replace('^',"'")
                frequency = event[1]

                # if adverse_event not in existing:
                try:
                    adverse_event_model = AdverseEvent.objects.get(event=adverse_event)

                except:
                    adverse_event_model = AdverseEvent(event=adverse_event)
                    adverse_event_model.save()
                    # existing.update({adverse_event:True})

                adverse_event_model = CompoundAdverseEvent(compound=compound_model,event=adverse_event_model,frequency=frequency)
                adverse_event_model.save()
