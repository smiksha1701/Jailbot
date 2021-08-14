import lib.plag as plag

class Data():
    def __init__(self) -> None:
        self.container = []
    def empty(self):
        self.container = []

    def find_best_match(self, text):
        max_i = -1
        max_score = -1
        fp1 = plag.get_fingerprint(text)
        for i, (_, fp2) in enumerate(self.container):
                score = plag.score(fp1, fp2)
                if  score > max_score:
                    max_score = score
                    max_i = i
        self.container.append((text, plag.get_fingerprint(text)))
        if max_i == -1:
            return "", 0.0
        return self.container[max_i][0], max_score