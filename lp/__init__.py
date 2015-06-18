from functools import partial
import os

from colors import black


WORDS = [
    w.rstrip('\n') for w in
    open(os.path.join(
        os.path.dirname(__file__), 'words', 'Words', '{}.txt'.format(
            os.environ.get('LP_LANG', 'en').lower()
        )
    )).readlines()
]

GRID_SIZE = 5


def word_is_playable(word, available):
    available_letters = list(available)
    for letter in word:
        try:
            available_letters.remove(letter)
        except ValueError:
            return False

    return True


def get_playable_words(available):
    for word in WORDS:
        if word_is_playable(word, available):
            yield word


def is_prefix_of(word, of):
    return of.startswith(word) and len(of) > len(word)


def get_unique_playable_words(available):
    playable = sorted(
        get_playable_words(available),
        key=lambda w: len(w),
        reverse=True,
    )

    blocked = set()

    for word in playable:
        if word not in blocked:
            yield word

        for i in range(1, len(word)):
            blocked.add(word[:i])


def get_score(word, targets, unclaimed, win_at):
    target_letters = list(targets)
    unclaimed_letters = list(unclaimed)

    score = 0

    for letter in word:
        if letter in target_letters:
            score += 2
            target_letters.remove(letter)
        elif letter in unclaimed_letters:
            score += 1
            unclaimed_letters.remove(letter)

    if len(unclaimed_letters) == 0 and score > win_at:
        score += float('inf')

    return score


def get_best_words(playable_words, targets, unclaimed, win_at):
    return sorted((
        (w, get_score(w, targets, unclaimed, win_at))
        for w in playable_words
    ), key=lambda ws: (ws[1], -len(ws[0])), reverse=True)


def render_grid(state, letters):
    d = 'negative'
    ed = partial(black, bg='red', style=d)
    e = partial(black, bg='red')
    u = partial(black, bg='white')
    m = partial(black, bg='blue')
    md = partial(black, bg='blue', style=d)

    state_funcs = [{
        'E': ed,
        'e': e,
        'u': u,
        'm': m,
        'M': md,
    }[s] for s in state]

    return ''.join(
        state_funcs[index](' {} '.format(letter)) + (
            '' if (index+1) % GRID_SIZE else '\n')
        for index, letter in enumerate(letters)
    ).strip()


def get_best_words_for_letters(defended, targets, unclaimed, owned):
    unclaimable = defended + owned
    available = targets + unclaimed + unclaimable

    if len(available) != GRID_SIZE ** 2:
        raise ValueError(
            'You provided {} letters. That is not a letterpress grid.'
            .format(len(available))
        )

    home = len(owned)
    away = len(targets + defended)

    playable = get_unique_playable_words(available)

    return get_best_words(playable, targets, unclaimed, away-home)


def example_grid():
    return render_grid('eummMEeeemememmmmeeeMmeEE',
                       'GQGNMSVZSNRGLRENDPDIHFARM')
