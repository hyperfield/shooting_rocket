from highscores import load_high_scores, register_score


class GameState:
    """Track score, wave progression, and failure state."""

    def __init__(self, max_misses, wave_size):
        self.score = 0
        self.wave = 1
        self.missed = 0
        self.max_misses = max_misses
        self.wave_size = wave_size
        self.game_over = False
        self.game_over_message = ""
        self.restart_requested = False
        self.quit_requested = False
        self.score_recorded = False
        self.high_scores = load_high_scores()

    def register_hit(self):
        if self.game_over:
            return
        self.score += 1
        if self.score % self.wave_size == 0:
            self.wave += 1

    def register_miss(self):
        if self.game_over:
            return
        self.missed += 1
        if self.missed >= self.max_misses:
            self.trigger_game_over("Too much junk slipped through!")

    def trigger_game_over(self, message):
        if self.game_over:
            return
        self.game_over = True
        self.game_over_message = message
        self.finalize_score()

    def finalize_score(self):
        if self.score_recorded:
            return
        self.high_scores = register_score(self.score)
        self.score_recorded = True

    def request_restart(self):
        self.restart_requested = True
        self.game_over = True

    def request_quit(self):
        self.quit_requested = True
        self.restart_requested = True
        self.game_over = True

    def difficulty_multiplier(self):
        """Increase difficulty slightly with every wave."""
        return 1 + (self.wave - 1) * 0.15

    def is_active(self):
        return not (self.game_over or self.restart_requested or self.quit_requested)
