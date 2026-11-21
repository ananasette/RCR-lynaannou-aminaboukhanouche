import re
from dataclasses import dataclass, field
from itertools import product
from sympy import Symbol, Not
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
    """Kept only to verify results: Gamma(E) must be equivalent to E."""
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


# ---------------------------------------------------------------- extensions
@dataclass
class Extension:
    base: list                                      # In: W + conclusions of applied defaults
    appliques: list = field(default_factory=list)   # indices (in the instantiated theory)
    noms: list = field(default_factory=list)        # str() of the applied defaults
    out: list = field(default_factory=list)         # the ¬β commitments

    def litteraux(self):
        """Literals (a or ¬a) entailed by the extension."""
        atomes = {s for f in self.base for s in f.atoms(Symbol)}
        res = []
        for a in sorted(atomes, key=lambda s: s.name):
            if consequence(self.base, a):
                res.append(a)
            elif consequence(self.base, Not(a)):
                res.append(Not(a))
        return res

#reiter's process tree : replaces the exponential original function we were using ; where the original function was exploring all possible combinations of defaults, 
# this one explores only the applicable ones and prunes the branches that lead to incoherence. 
# We apply a default, add it to the list of applied defaults, and then explore the next applicable defaults. 
# If we reach a point where no more defaults can be applied, we check if the current set of applied defaults leads to a coherent extension. 
# If it does, we add it to the results. If not, we backtrack and try other combinations.
def extensions(theorie):
   
    theorie = instancier(theorie)
    D = theorie.defauts
    resultats = []
    vus = set()                       # sets of applied defaults already explored

    def explorer(appliques, In, Out):
        # 1. failed process: a committed ¬β became derivable (monotonic -> prune)
        if any(consequence(In, o) for o in Out):
            return
        # 2. applicable defaults not yet used
        candidats = [i for i, d in enumerate(D)
                     if i not in appliques and est_applicable(d, In)]
        # 3. closed and successful -> extension
        if not candidats:
            if not any(_equivalents(In, x.base) for x in resultats):
                resultats.append(Extension(list(In), list(appliques),
                                           [str(D[i]) for i in appliques],
                                           list(Out)))
            return
        # 4. branch on each applicable default
        for i in candidats:
            cle = frozenset(appliques) | {i}
            if cle in vus:            # same defaults reached in another order
                continue
            vus.add(cle)
            d = D[i]
            explorer(appliques + [i],
                     In + [d.conclusion],
                     Out + [Not(j) for j in d.justifications])

    explorer([], list(theorie.faits), [])
    return resultats


def consequence_credulous(theorie, formule):
    return any(consequence(E.base, formule) for E in extensions(theorie))


def consequence_sceptique(theorie, formule):
    exts = extensions(theorie)
    return bool(exts) and all(consequence(E.base, formule) for E in exts)