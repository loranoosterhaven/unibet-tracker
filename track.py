import requests
import time
import sys

class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush() # If you want the output to be visible immediately
    def flush(self) :
        for f in self.files:
            f.flush()


f = open('output.txt', 'w')
original = sys.stdout
sys.stdout = Tee(sys.stdout, f)

event_ids = [1005492442, 1005498786, 1005498836, 1005498838, 1005498839, 1005498360, 1005498358, 1005498357, 1005498357,
             1005498356, 1005498359, 1005495775, 1005495777, 1005495755, 1005496190, 1005495754, 1005495776, 1005496191,
             1005495782, 1005496189]

valid_ids = {}
event_names = {}

print 'Start tracking of evens ' + str(event_ids) + '\n'

for event_id in event_ids:
    url = 'https://eu-offering.kambicdn.org/offering/v2018/ub/betoffer/event/' + str(event_id) \
          + '.json'

    try:
        r = requests.get(url)
        unibet_data = r.json()

        if not unibet_data or 'error' in unibet_data or unibet_data['events'][0]['state'] == 'STARTED':
            valid_ids[event_id] = False
            print 'Event ' + str(event_id) + ' is no longer valid'
        else:
            event_data = unibet_data['events'][0]

            print 'Event [' + str(event_id) + ', ' + event_data['group'] + ', ' + event_data['name'] \
                  + ', ' + event_data['start'] + ']'

            event_names[event_id] = event_data['name']
            valid_ids[event_id] = True

    except Exception:
        valid_ids[event_id] = False
        print 'Initial error while processing ' + str(event_id)

    time.sleep(2)

under_2500_list = {}
over_2500_list = {}

for event_id in event_ids:
    under_2500_list[event_id] = []
    over_2500_list[event_id] = []

while 1:
    if not any(valid_ids):
        print 'No valid events left, shutting down...'
        exit(0)

    for event_id in event_ids:
        url = 'https://eu-offering.kambicdn.org/offering/v2018/ub/betoffer/event/' + str(event_id) \
              + '.json'

        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        try:
            if valid_ids[event_id]:
                r = requests.get(url)
                unibet_data = r.json()

                if unibet_data and 'error' not in unibet_data and unibet_data['events'][0]['state'] != 'STARTED':
                    bet_data = unibet_data['betOffers'];

                    for bet_offer in bet_data:
                        if bet_offer['betOfferType']['name'] == 'Over/Under':
                            if bet_offer['criterion']['label'] == 'Total Goals' and bet_offer['outcomes'][1]['line'] == 2500:
                                measurementUnder = {'odds' : float(bet_offer['outcomes'][1]['odds'])/1000.0,
                                                              'time' : int(time.time())}

                                if not under_2500_list[event_id]:
                                    print time_str + ': ' + event_names[event_id] + ' initial under 2.5 odds are ' + str(measurementUnder['odds'])

                                if under_2500_list[event_id]:
                                    difference = under_2500_list[event_id][-1]['odds'] - measurementUnder['odds']

                                    if difference > 0.0:
                                        print time_str + ': ' + event_names[event_id] + ' under 2.5 odds dropped by ' + str(difference) \
                                              + ' from ' + str(under_2500_list[event_id][-1]['odds']) + ' to ' + str(measurementUnder['odds'])

                                measurementOver = {'odds': float(bet_offer['outcomes'][0]['odds']) / 1000.0,
                                                   'time': int(time.time())}

                                under_2500_list[event_id].append(measurementUnder)

                                if not over_2500_list[event_id]:
                                    print time_str + ': ' + event_names[event_id] + ' initial over 2.5 odds are ' + str(measurementOver['odds'])

                                if over_2500_list[event_id]:
                                    difference = over_2500_list[event_id][-1]['odds'] - measurementOver['odds']

                                    if difference > 0.0:
                                        print time_str + ': ' + event_names[event_id] + ' over 2.5 odds dropped by ' + str(difference) \
                                              + ' from ' + str(over_2500_list[event_id][-1]['odds']) + ' to ' + str(measurementOver['odds'])

                                over_2500_list[event_id].append(measurementOver)
                else:
                    valid_ids[event_id] = False
                    print time_str + ': ' + 'Event ' + event_names[event_id] + ' is no longer valid'

        except Exception:
            print time_str + ': ' + 'Error while processing event ' + event_names[event_id]

        time.sleep(2)
