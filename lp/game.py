from functools import partial
import os

from colors import black

with open(os.path.join(
    os.path.dirname(__file__), 'words', 'Words', '{}.txt'.format(
        os.environ.get('LP_LANG', 'en').lower()
    )
)) as wf:
    WORDS = [
        w.rstrip('\n').lower() for w in
        wf.readlines()
    ]
OPPONENT = 'o'
PLAYER = 'p'
NOBODY = 'u'

GRID_SIZE = 5


class NoSuchPriorityError(ValueError):
    pass


class Grid(object):
    """
    A representation of the state of a grid in a given game.
    """

    NET_SCORE_PRIORITY = 'ns'
    AVOID_SPREADING_PRIORITY = 'plg'

    PRIORITIES = {
        NET_SCORE_PRIORITY: (
            "Focus exclusively on increasing your score relative to your "
            "opponents."
        ),
        AVOID_SPREADING_PRIORITY: (
            "Try only to take tiles from your opponent. Useful in late-game "
            "situations when you're trying not to give away an easy word "
            "that'll let your opponent win."
        ),
    }

    def __init__(self, letters, ownership, priority=NET_SCORE_PRIORITY):
        letters = letters.lower()

        self.tiles = [
            Tile(l, s, self, i)
            for i, (l, s) in enumerate(zip(letters, ownership))
        ]

        # and, just to make looking up words quicker:
        self.letters = letters

        self.priority = priority

    def __str__(self):
        return '{}\n{}'.format(
            '{:>6} - {}'.format(self.player_score(), self.opponent_score()),
            '\n'.join(
                ''.join((str(t) for t in row)) for row in self.rows()
            )
        )

    @classmethod
    def from_image(cls, image, **kw):
        from lp.image import parse_image
        return cls(*parse_image(image), **kw)

    def _score_for(self, player):
        return len([t for t in self.tiles if t.ownership == player])

    def player_score(self):
        return self._score_for(PLAYER)

    def opponent_score(self):
        return self._score_for(OPPONENT)

    def word_is_playable(self, word):
        available_letters = list(self.letters)
        for letter in word:
            try:
                available_letters.remove(letter)
            except ValueError:
                return False

        return True

    def get_playable_words(self):
        for word in WORDS:
            if self.word_is_playable(word):
                yield word

    def get_unique_playable_words(self):
        """
        Yield all words that can be played on this grid, excluding those that
        would leave room for the opponent to play a longer version.
        """

        playable = sorted(
            self.get_playable_words(),
            key=lambda w: len(w),
            reverse=True,
        )

        blocked = set()

        for word in playable:
            if word not in blocked:
                yield word

            for i in range(1, len(word)):
                blocked.add(word[:i])

    def get_value_of_word(self, word):
        undefended_opponent_letters = [
            t.letter for t in self.tiles
            if t.ownership == OPPONENT and not t.is_defended()
        ]
        unclaimed_letters = [
            t.letter for t in self.tiles
            if t.ownership == NOBODY
        ]

        score = 0

        for letter in word:
            if letter in undefended_opponent_letters:
                if self.priority == Grid.NET_SCORE_PRIORITY:
                    score += 2
                elif self.priority == Grid.AVOID_SPREADING_PRIORITY:
                    score += 1
                else:
                    raise NoSuchPriorityError()

                undefended_opponent_letters.remove(letter)
            elif letter in unclaimed_letters:
                if self.priority == Grid.NET_SCORE_PRIORITY:
                    score += 1
                elif self.priority == Grid.AVOID_SPREADING_PRIORITY:
                    score -= 1
                else:
                    raise NoSuchPriorityError()

                unclaimed_letters.remove(letter)

        if len(unclaimed_letters) == 0 and score > (
            self.opponent_score() - self.player_score()
        ):
            score += float('inf')

        return score

    def get_best_words(self):
        return sorted((
            (w, self.get_value_of_word(w))
            for w in self.get_unique_playable_words()
        ), key=lambda ws: (ws[1], -len(ws[0])), reverse=True)

    def rows(self):
        for i in range(GRID_SIZE):
            yield self.tiles[i * GRID_SIZE:(i + 1) * GRID_SIZE]


class Tile(object):
    def __init__(self, letter, ownership, grid, index):
        self.letter = letter
        self.ownership = ownership
        self.grid = grid
        self.index = index

    def __str__(self):
        d = 'negative'
        return {
            (OPPONENT, True): partial(black, bg='red', style=d),
            (OPPONENT, False): partial(black, bg='red'),
            (NOBODY, False): partial(black, bg='white'),
            (PLAYER, False): partial(black, bg='blue'),
            (PLAYER, True): partial(black, bg='blue', style=d),
        }[
            (self.ownership, self.is_defended())
        ](
            ' {} '.format(self.letter.upper())
        )

    def get_neighbours(self):
        return (
            self.grid.tiles[i] for i in range(GRID_SIZE ** 2) if
            (self.index - i == 1 and self.index % GRID_SIZE) or
            (self.index - i == -1 and i % GRID_SIZE) or
            self.index - i in (GRID_SIZE, -GRID_SIZE)
        )

    def is_defended(self):
        return self.ownership != NOBODY and all((
            t.ownership == self.ownership
            for t in self.get_neighbours()
        ))
