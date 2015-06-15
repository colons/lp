import os

WORDS = [
    w.rstrip('\n') for w in
    open(os.path.join(
        os.path.dirname(__file__), 'words', 'Words', '{}.txt'.format(
            os.environ.get('LP_LANG', 'en').lower()
        )
    )).readlines()
    if w.lower() == w
]


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
    playable = list(get_playable_words(available))
    return filter(
        lambda w: not any((is_prefix_of(w, a) for a in playable)),
        playable,
    )


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
    ), key=lambda ws: ws[1], reverse=True)


def example_grid():
    from colors import black
    from functools import partial

    d = 'negative'
    ed = partial(black, bg='red', style=d)
    e = partial(black, bg='red')
    u = partial(black, bg='white')
    m = partial(black, bg='blue')
    md = partial(black, bg='blue', style=d)

    state = [e, u, m, m, md,
             ed, e, e, e, m,
             e, m, e, m, m,
             m, m, e, e, e,
             md, m, e, ed, ed]
    grid = 'GQGNMSVZSNRGLRENDPDIHFARM'

    return ''.join(
        state[index](' {} '.format(letter)) + ('' if (index+1) % 5 else '\n')
        for index, letter in enumerate(grid)
    )
