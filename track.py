import argparse
import requests
import time

event_ids = [1005414753, 1005414754, 1005414757, 1005414758, 1005414762, 1005414763, 1005414767]
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

    if not unibet_data or 'error' in unibet_data:
        event_ids.remove(event_id)
        print 'Event ' + str(event_id) + ' removed due to error\n'
    else:
        event_data = unibet_data['events'][0]

        print 'League: ' + event_data['group']
        print 'Game: ' + event_data['name']
        print 'Time: ' + event_data['start'] + '\n'

        event_names[event_id] = event_data['name']

under_2500_list = {}

for event_id in event_ids:
    under_2500_list[event_id] = []

while 1:
    for event_id in event_ids:
        url = 'https://eu-offering.kambicdn.org/offering/v2018/ub/betoffer/event/' + str(event_id) \
              + '.json'

        try:
            r = requests.get(url)
            unibet_data = r.json()
        except requests.exceptions.RequestException:
            print 'Connection error, next attempt in 5 seconds...'

        if unibet_data:
            bet_data = unibet_data['betOffers'];

            for bet_offer in bet_data:
                if bet_offer['betOfferType']['name'] == 'Over/Under':
                    if bet_offer['criterion']['label'] == 'Total Goals' and bet_offer['outcomes'][1]['line'] == 2500:
                        measurement = {'odds' : float(bet_offer['outcomes'][1]['odds'])/1000.0,
                                                      'time' : time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}

                        if not under_2500_list[event_id]:
                            print event_names[event_id] + ' initial odds are ' + str(measurement['odds'])

                        if under_2500_list[event_id]:
                            if under_2500_list[event_id][-1]['odds'] - measurement['odds'] > 0.0:
                                print event_names[event_id] + ' odds dropped by ' + str(under_2500_list[event_id][-1]['odds']
                                        - measurement['odds']) + ' from ' + str(under_2500_list[event_id][-1]['odds']) + ' to ' \
                                        + str(measurement['odds'])

                        under_2500_list[event_id].append(measurement)

        time.sleep(5)
