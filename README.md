# chess_ai
* fitness = opponent_score + turn_score + match_score + piece_score
  * turn_score = -sqrt(turn)/4 + 2
  * match_score = 2 if win else -2 if lose else 0
  * piece_score = self.game.get_score(color)
