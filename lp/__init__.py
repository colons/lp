WORDS = [
    w.rstrip('\n') for w in
    open('/usr/share/dict/words').readlines()
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


def get_score(word, targets, unclaimed):
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

    return score


def get_best_words(playable_words, targets, unclaimed):
    return sorted((
        (w, get_score(w, targets, unclaimed))
        for w in playable_words
    ), key=lambda ws: ws[1], reverse=True)
