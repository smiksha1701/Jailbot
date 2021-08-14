import zlib 

def clear_white_symbols(text):
    return text.translate({ord(i): None for i in  ' ,.!;:][{(})'})

def hash_ngrams(ngrams):
    hashes = []
    for i in ngrams:
        hashes.append(zlib.crc32(bytes(i,encoding = 'utf8')))
    return hashes

def fingerprint(windows):
    fingerprint = []
    for i, window in enumerate(windows):
        mini, minipl = minimum(window)
        potential_candidate = (mini, minipl+i)
        if(potential_candidate not in fingerprint):
            fingerprint.append(potential_candidate)
    return [h for h, _ in fingerprint]

def minimum(window):
    mini = window[0]
    minpl = 0
    for i, j in enumerate(window):
        if(j < mini):
            mini = j
            minpl = i
    return mini, minpl

def n_grams(to_ngram, n = 4):
    ngram = []
    length = len(to_ngram)
    for i in range (length-n-1):
        ngram.append(to_ngram[i:i + n])
    return ngram

def lcs(first, second):
    lf=len(first)
    ls=len(second)
    lcst=[[None]*ls for i in range(lf)]
    for i in range(lf):
        for j in range(ls):
            if(i == 0):
                if(j == 0):
                    if(first[0] == second[0]):
                        lcst[0][0] = 1
                    else:
                        lcst[0][0] = 0
                else:
                    lcst[0][j] = lcst[0][j-1]
            elif(j == 0):
                lcst[i][0] = lcst[i - 1][0]
            else:
                if(first[i] == second[j]):
                    lcst[i][j] = lcst[i - 1][j - 1] + 1
                else:
                    lcst[i][j] = max(lcst[i - 1][j], lcst[i][j - 1])
    return lcst[lf - 1][ls - 1]

def get_fingerprint(text):
    return fingerprint(n_grams(hash_ngrams(n_grams(clear_white_symbols(text)))))
    
def score(fp1, fp2):
    colisions = lcs(fp1, fp2)
    return colisions / min(len(fp1), len(fp2))
