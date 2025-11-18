from functools import reduce
import numpy as np
import matplotlib.pyplot as plt


pts = {
    (1, 9),
    (1.25, 7),
    (2, 4),
    (4, 2),
    (7, 1),
    (6, 1),
    (9, 0.75),
    (6, 6),
    (4, 5),
    (7, 8),
    (9, 5),
    (3, 7),
    (5, 8),
    (7, 3),
}


def plot(pts):
    xs = [pt[0] for pt in pts]
    ys = [pt[1] for pt in pts]
    plt.scatter(xs, ys)
    plt.xlim(0, 10)
    plt.ylim(0, 10)
    plt.show()


plot(pts)


def dominates(p, q):
    """if for all i, pi <= qi AND there exists an i where p is strictly better than q"""
    score_diffs = np.array(p) - np.array(q)
    return all(d <= 0 for d in score_diffs) and any(d < 0 for d in score_diffs)


def reducer(S, p):
    return S - {q for q in S if dominates(p, q)}


nds = reduce(reducer, pts, pts)
plot(nds)
