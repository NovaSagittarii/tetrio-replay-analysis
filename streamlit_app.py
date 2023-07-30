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
      if key not in last_pressed: continue
      if keypress:
        if last_pressed[key] >= 0:
          frame_since_press = frame - last_pressed[key]
          pps = min((60 / frame_since_press) if frame_since_press else 10, 10)
          key_frequency[key].append(pps)
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
    results[i]['player'] = replay['events'][0]['data']['options']['username']
    results[i]['stats'] = parse_events(replay)
  return results

def display_round(playerStats: 'list[dict]'):
  with st.container():
    player_names:list[str] = []
    player_place_times:list[float] = []
    # st.write(playerStats)
    for i in range(len(playerStats)):
      player:str = playerStats[i]['player']
      stats:replay_typing.MovementDurationAndFrequency = playerStats[i]['stats']
      place_times:list[float] = stats['frequency']['hardDrop']
      player_names.append(player)
      player_place_times.append([0, 10] + place_times)
    col1, col2 = st.columns(2)
    col1.write('PPS Comparison ' + ' vs '.join(player_names))
    col2.write('avg ' + ' vs '.join(f'{sum(w)/len(w):.3f}' for w in player_place_times))
    fig = ff.create_distplot(player_place_times, player_names, bin_size=0.25)
    st.plotly_chart(fig, use_container_width=True)

def parse_replay_file(obj: dict):
  ismulti = obj.get('ismulti', None)
  if ismulti == None: return
  if ismulti: # 2P game
    rounds = []
    for round in obj.get('data', []):
      rounds.append(parse_multiplayer_round(round))
    with st.container():
      tabs = st.tabs([f'Round {i+1}' for i in range(len(rounds))] + ['Set average'])
      for i, round in enumerate(rounds):
        with tabs[i]:
          # st.header(f'Round {i+1}')
          display_round(round)
      for round in rounds[1:]:
        for i in range(len(round)):
          playerStats : replay_typing.MovementDurationAndFrequency = round[i]['stats']
          for type in playerStats:
            for key in playerStats[type]:
              rounds[0][i]['stats'][type][key] += playerStats[type][key]
      with tabs[-1]:
        # st.header('Set average')
        display_round(rounds[0])
  else: # 1P game
    pass

uploaded_files = st.file_uploader("Choose a TTRM file", accept_multiple_files=True)
for uploaded_file in uploaded_files:
  obj = json.load(uploaded_file)
  parse_replay_file(obj)
  # st.write(obj)