import re
from itertools import combinations, product
from sympy import Symbol
from reasoning import est_coherent, consequence
from defaults import Theory, Default

_ATOME = re.compile(r"^(\w+)\((.*)\)$")
_VARIABLE = re.compile(r"^[a-z]\d*$")   # variable = x, y, z, x1 ...; anything else = constant


def _arguments(symbole):
    m = _ATOME.match(symbole.name)
    if not m:
        return []
    return [a.strip() for a in m.group(2).split(",") if a.strip()]


def _parties(d):
    p = [d.prerequis] if d.prerequis is not None else []
    return p + list(d.justifications) + [d.conclusion]


def _constantes(theorie):
    formules = list(theorie.faits)
    for d in theorie.defauts:
        formules += _parties(d)
    return {a for f in formules for s in f.atoms(Symbol)
            for a in _arguments(s) if not _VARIABLE.match(a)}


def _substituer(f, valeurs):
    remp = {}
    for s in f.atoms(Symbol):
        m = _ATOME.match(s.name)
        if m:
            args = [valeurs.get(a.strip(), a.strip()) for a in m.group(2).split(",")]
            remp[s] = Symbol(f"{m.group(1)}({','.join(args)})")
    return f.xreplace(remp)


def instancier(theorie):
    """Replace the variables of every default by each constant of the theory."""
    consts = sorted(_constantes(theorie))
    res = Theory()
    res.faits = list(theorie.faits)
    vus = set()
    for d in theorie.defauts:
        vars_ = sorted({a for f in _parties(d) for s in f.atoms(Symbol)
                        for a in _arguments(s) if _VARIABLE.match(a)})
        if not vars_:
            instances = [d]
        else:
            instances = []
            for combo in product(consts, repeat=len(vars_)):
                v = dict(zip(vars_, combo))
                instances.append(Default(
                    _substituer(d.prerequis, v) if d.prerequis is not None else None,
                    [_substituer(j, v) for j in d.justifications],
                    _substituer(d.conclusion, v)))
        for inst in instances:
            if str(inst) not in vus:
                vus.add(str(inst))
                res.defauts.append(inst)
    return res


def est_applicable(defaut, connaissances, contexte=None):
    """Prerequisite follows from `connaissances`; every justification is
    consistent with `contexte` (defaults to `connaissances`)."""
    contexte = connaissances if contexte is None else contexte
    if defaut.prerequis is not None and not consequence(connaissances, defaut.prerequis):
        return False
    return all(est_coherent(list(contexte) + [j]) for j in defaut.justifications)


def _equivalents(A, B):
    return (all(consequence(A, f) for f in B) and
            all(consequence(B, f) for f in A))


def _gamma(theorie, E):
    courant = list(theorie.faits)
    appliques = set()
    changement = True
    while changement:
        changement = False
        for i, d in enumerate(theorie.defauts):
            if i in appliques:
                continue
            if est_applicable(d, courant, contexte=E):
                courant.append(d.conclusion)
                appliques.add(i)
                changement = True
    return courant


def extensions(theorie):
    theorie = instancier(theorie)
    n = len(theorie.defauts)
    trouvees = []
    for k in range(n + 1):
        for indices in combinations(range(n), k):
            E = list(theorie.faits) + [theorie.defauts[i].conclusion for i in indices]
            if _equivalents(_gamma(theorie, E), E):
                if not any(_equivalents(E, autre) for autre in trouvees):
                    trouvees.append(E)
    return trouvees


def consequence_credulous(theorie, formule):
    return any(consequence(E, formule) for E in extensions(theorie))


def consequence_sceptique(theorie, formule):
    exts = extensions(theorie)
    return bool(exts) and all(consequence(E, formule) for E in exts)