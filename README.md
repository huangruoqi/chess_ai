# chess_ai
## Phases:
<!-- 1. minimax data collection
  - run `save.py` to collect minimax data
  - change `DEPTH` to calculate different depth
2. fit the MLP with minimax data (train1)
  - run `train_bp_minimax.py` to train with backpropagation
  - test different layers and epochs to find the best model -->
1. use genetic algorithm: minimax (train2)
  - run `train_ga_minimax.py` to train against minimax
  - check model output occasionally
  - increase depth if model have better win rate
2. use genetic algorithm: ai (train3)
  - run `train_ga_self.py` to train against another model
  - reconsider ranking system 

