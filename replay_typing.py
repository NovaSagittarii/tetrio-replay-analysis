from typing import TypedDict

class MovementFrames(TypedDict):
  moveLeft: 'list[float]'
  moveRight: 'list[float]'
  rotateCW: 'list[float]'
  rotateCCW: 'list[float]'
  rotate180: 'list[float]'
  hardDrop: 'list[float]'
  softDrop: 'list[float]'
  hold: 'list[float]'

class MovementDurationAndFrequency(TypedDict):
  duration: MovementFrames
  frequency: MovementFrames