from functools import lru_cache
from itertools import combinations
from sympy import And, Not
from sympy.logic.inference import satisfiable


@lru_cache(maxsize=None)
def _sat(f):
    # satisfiable() returns False or a model dict (which may be {}), so test "is not False"
    return satisfiable(f) is not False


def est_coherent(formules):
    """A set of formulas is coherent if some assignment satisfies all of them."""
    formules = list(formules)
    if not formules:
        return True
    return _sat(And(*formules))


def consequence(formules, conclusion):
    """Th |= phi  <=>  Th U {~phi} is incoherent."""
    return not est_coherent(list(formules) + [Not(conclusion)])


def formules_incoherentes(formules):
    """formulas that are contradictions on their own."""
    return [f for f in formules if not _sat(f)]


def sous_ensembles_incoherents(formules):
    """minimal inconsistent subsets."""
    formules = list(formules)
    trouves = []
    for k in range(1, len(formules) + 1):
        for sous in combinations(formules, k):
            if any(set(t) <= set(sous) for t in trouves):
                continue
            if not est_coherent(list(sous)):
                trouves.append(sous)
    return trouves