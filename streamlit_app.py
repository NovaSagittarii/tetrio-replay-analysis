import streamlit as st
import numpy as np
import scipy
import plotly.figure_factory as ff
import json
import replay_typing

KEYS = ('moveLeft', 'moveRight', 'rotateCW', 'rotateCCW', 'rotate180', 'hardDrop', 'softDrop', 'hold')

def parse_events(events: 'list[dict]') -> replay_typing.MovementDurationAndFrequency:
  key_duration = {k: [] for k in KEYS}
  key_frequency = {k: [] for k in KEYS}
  last_pressed = {k: -1 for k in KEYS}

  for event in events.get('events'):
    type = event.get('type')
    if type == 'keyup' or type == 'keydown':
      keypress = type == 'keydown'
      key = event.get('data').get('key')
      frame = event.get('frame') + event.get('data').get('subframe')
      if keypress:
        if last_pressed[key] >= 0: key_frequency[key].append(1 / ((frame - last_pressed[key]) / (1000/60) ))
        last_pressed[key] = frame
      else:
        key_duration[key].append(frame - last_pressed[key])
  return {
    'duration': key_duration,
    'frequency': key_frequency
  }

def parse_multiplayer_round(data: dict):
  players = list(board.get('user').get('username') for board in data.get('board'))
  results = [{} for i in range(len(players))]
  for i, replay in enumerate(data.get('replays')):
    results[i]['player'] = players[i]
    results[i]['stats'] = parse_events(replay)
  return results

def display_round(playerStats: 'list[dict]'):
  with st.container():
    player_names:list[str] = []
    player_place_times:list[float] = []
    for i in range(len(playerStats)):
      player:str = playerStats[i]['player']
      stats:replay_typing.MovementDurationAndFrequency = playerStats[i]['stats']
      place_times:list[float] = stats['frequency']['hardDrop']
      place_times.append(0)
      player_names.append(player)
      player_place_times.append(place_times)
    st.write('### PPS Comparison ' + ' vs '.join(player_names))
    fig = ff.create_distplot(player_place_times, player_names, bin_size=0.1)
    st.plotly_chart(fig, use_container_width=True)

def parse_replay_file(obj: dict):
  ismulti = obj.get('ismulti', None)
  if ismulti == None: return
  if ismulti: # 2P game
    rounds = []
    for round in obj.get('data', []):
      rounds.append(parse_multiplayer_round(round))
    for round in rounds[1:]:
      for i in range(len(round)):
        playerStats : replay_typing.MovementDurationAndFrequency = round[i]['stats']
        for type in playerStats:
          for key in playerStats[type]:
            rounds[0][i]['stats'][type][key] += playerStats[type][key]
    display_round(rounds[0])
  else: # 1P game
    pass

uploaded_files = st.file_uploader("Choose a TTRM file", accept_multiple_files=True)
for uploaded_file in uploaded_files:
  obj = json.load(uploaded_file)
  parse_replay_file(obj)
  # st.write(obj)