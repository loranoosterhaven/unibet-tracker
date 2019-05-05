import argparse
import requests
import time

event_ids = [1005414753, 1005414754, 1005414757, 1005414758, 1005414762, 1005414763, 1005414767]
valid_ids = {}
event_names = {}

print 'Start tracking of evens ' + str(event_ids) + '\n'

for event_id in event_ids:
    url = 'https://eu-offering.kambicdn.org/offering/v2018/ub/betoffer/event/' + str(event_id) \
          + '.json'

    try:
        r = requests.get(url)
        unibet_data = r.json()
    except requests.exceptions.RequestException:
        print 'Initial connection error'
        exit(0)

    if not unibet_data or 'error' in unibet_data:
        valid_ids[event_id] = False
        print 'Event ' + str(event_id) + ' is no longer valid\n'
    else:
        event_data = unibet_data['events'][0]

        print 'Event ID: ' + str(event_id)
        print 'League: ' + event_data['group']
        print 'Game: ' + event_data['name']
        print 'Time: ' + event_data['start'] + '\n'

        event_names[event_id] = event_data['name']
        valid_ids[event_id] = True

    time.sleep(1)

under_2500_list = {}

for event_id in event_ids:
    under_2500_list[event_id] = []

while 1:
    for event_id in event_ids:
        url = 'https://eu-offering.kambicdn.org/offering/v2018/ub/betoffer/event/' + str(event_id) \
              + '.json'

        try:
            if valid_ids[event_id]:
                r = requests.get(url)
                unibet_data = r.json()

                if unibet_data and 'error' not in unibet_data:
                    bet_data = unibet_data['betOffers'];

                    for bet_offer in bet_data:
                        if bet_offer['betOfferType']['name'] == 'Over/Under':
                            if bet_offer['criterion']['label'] == 'Total Goals' and bet_offer['outcomes'][1]['line'] == 2500:
                                measurement = {'odds' : float(bet_offer['outcomes'][1]['odds'])/1000.0,
                                                              'time' : int(time.time())}

                                time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

                                if not under_2500_list[event_id]:
                                    print time_str + ': ' + event_names[event_id] + ' initial odds are ' + str(measurement['odds'])

                                if under_2500_list[event_id]:
                                    difference = under_2500_list[event_id][-1]['odds'] - measurement['odds']

                                    if difference > 0.0:
                                        print time_str + ': ' + event_names[event_id] + ' odds dropped by ' + str(difference) \
                                              + ' from ' + str(under_2500_list[event_id][-1]['odds']) + ' to ' + str(measurement['odds'])
                                    elif difference < 0.0:
                                        print time_str + ': ' + event_names[event_id] + ' odds increased by ' + str(-difference) \
                                              + ' from ' + str(under_2500_list[event_id][-1]['odds']) + ' to ' + str(measurement['odds'])

                                under_2500_list[event_id].append(measurement)
                else:
                    valid_ids[event_id] = False
                    print 'Event ' + str(event_id) + ' is no longer valid\n'

        except requests.exceptions.RequestException:
            print 'Connection error, next attempt in 5 seconds...'

        time.sleep(5)
