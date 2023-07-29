import streamlit as st
import numpy as np
import scipy
import plotly.figure_factory as ff
import json
import replay_typing

KEYS = ('moveLeft', 'moveRight', 'rotateCW', 'rotateCCW', 'rotate180', 'hardDrop', 'softDrop', 'hold')

def parse_events(events: 'list[dict]') -> replay_typing.MovementFrames:
  key_duration = {k: [] for k in KEYS}
  last_pressed = {k: -1 for k in KEYS}

  for event in events.get('events'):
    type = event.get('type')
    if type == 'keyup' or type == 'keydown':
      keypress = type == 'keydown'
      key = event.get('data').get('key')
      frame = event.get('frame') + event.get('data').get('subframe')
      if keypress:
        last_pressed[key] = frame
      else:
        key_duration[key].append(frame - last_pressed[key])
  return key_duration

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
      stats:replay_typing.MovementFrames = playerStats[i]['stats']
      place_times:list[float] = stats['hardDrop']
      player_names.append(player)
      player_place_times.append(place_times)
    fig = ff.create_distplot(player_place_times, player_names, bin_size=1)
    st.plotly_chart(fig, use_container_width=True)

def parse_replay_file(obj: dict):
  ismulti = obj.get('ismulti', None)
  if ismulti == None: return
  for round in obj.get('data', []):
    if ismulti: # 2P game
      display_round(parse_multiplayer_round(round))
    else: # 1P game
      pass

uploaded_files = st.file_uploader("Choose a TTRM file", accept_multiple_files=True)
for uploaded_file in uploaded_files:
  obj = json.load(uploaded_file)
  parse_replay_file(obj)
  # st.write(obj)