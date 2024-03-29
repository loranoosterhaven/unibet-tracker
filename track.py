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

event_ids = [1005561878, 1005561880, 1005561885, 1005561879, 1005561877, 1005561882, 1005598864, 1005561888, 1005561887,
             1005561881, 1005575768, 1005575769, 1005575770, 1005575772, 1005575771, 1005575773, 1005575774, 1005567375]

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

            print 'Event [' + str(event_id) + ', ' + event_data['group'].encode('utf-8').strip() + ', ' \
                  + event_data['name'].encode('utf-8').strip() + ', ' + event_data['start'].encode('utf-8').strip() \
                  + ']'

            event_names[event_id] = event_data['name'].encode('utf-8').strip()
            valid_ids[event_id] = True

    except Exception, e:
        valid_ids[event_id] = False
        print 'Initial error while processing ' + str(event_id) + ' ' + str(e)

    time.sleep(2)

under_2500_list = {}

for event_id in event_ids:
    under_2500_list[event_id] = []

while 1:
    if not any(valid_id is True for valid_id in valid_ids.itervalues()):
        print 'No valid events left, shutting down...'
        exit(0)

    for event_id in event_ids:
        url = 'https://eu-offering.kambicdn.org/offering/v2018/ub/betoffer/event/' + str(event_id) \
              + '.json'

        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

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
                                    elif difference < 0.0:
                                        print time_str + ': ' + event_names[event_id] + ' under 2.5 odds increased by ' + str(-difference) \
                                              + ' from ' + str(under_2500_list[event_id][-1]['odds']) + ' to ' + str(measurementUnder['odds'])

                                under_2500_list[event_id].append(measurementUnder)

                else:
                    valid_ids[event_id] = False
                    print time_str + ': ' + 'Event ' + event_names[event_id] + ' is no longer valid'

        except Exception:
            print time_str + ': ' + 'Error while processing event ' + event_names[event_id]

        time.sleep(2)
