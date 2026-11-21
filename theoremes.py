from itertools import combinations
from reasoning import est_coherent, consequence
from defaults import Theory
from extensions import extensions, instancier


def _classe(d):
    """'normal' : justification == conclusion, single justification
       'semi-normal' : single justification that entails the conclusion
       'general' : anything else"""
    if len(d.justifications) == 1:
        j = d.justifications[0]
        if consequence([j], d.conclusion) and consequence([d.conclusion], j):
            return "normal"
        if consequence([j], d.conclusion):
            return "semi-normal"
    return "general"


def classifier(theorie):
    """Returns 'normal', 'semi-normal' or 'general' for the whole theory."""
    classes = {_classe(d) for d in instancier(theorie).defauts}
    if classes <= {"normal"}:
        return "normal"
    if classes <= {"normal", "semi-normal"}:
        return "semi-normal"
    return "general"


def _sous_theorie(inst, indices):
    t = Theory()
    t.faits = list(inst.faits)
    t.defauts = [inst.defauts[i] for i in indices]
    return t

# a normal theory meaning that all defaults are normal or semi normal 
# + consistent W (set of facts), means those facts don’t contradict each other: 
# at least one truth assignment makes all of them true at once
# = > at least one extension exists.
def verifier_existence(theorie):
    """Normal + consistent W  =>  at least one extension."""
    return len(extensions(theorie)) >= 1


def verifier_orthogonalite(theorie):
    """Distinct extensions must be pairwise jointly inconsistent."""
    exts = extensions(theorie)
    for a, b in combinations(exts, 2):
        if est_coherent(a.base + b.base):
            return False, (a, b)
    return True, None


def verifier_semi_monotonie(theorie):
    """Add the defaults one by one: every extension of the smaller theory
    must be contained in some extension of the larger one."""
    inst = instancier(theorie)
    n = len(inst.defauts)
    for k in range(n):
        petite = extensions(_sous_theorie(inst, range(k)))
        grande = extensions(_sous_theorie(inst, range(k + 1)))
        for E in petite:
            if not any(all(consequence(F.base, f) for f in E.base) for F in grande):
                return False, k
    return True, None


def audit(theorie):
    """Full report as a list of (theorem, status, comment)."""
    classe = classifier(theorie)
    rapport = [("Classe de la théorie", classe, "")]
    if not est_coherent(theorie.faits):
        rapport.append(("W incohérent", "ATTENTION",
                        "La seule extension est l'ensemble de toutes les formules."))
        return rapport
    if classe != "normal":
        rapport.append(("Garanties de Reiter", "non applicables",
                        "Théorie non normale : une extension peut ne pas exister "
                        "et les extensions peuvent ne pas être orthogonales."))
        return rapport
    ok = verifier_existence(theorie)
    rapport.append(("Existence d'une extension", "OK" if ok else "VIOLÉ (bug ?)", ""))
    ok, _ = verifier_orthogonalite(theorie)
    rapport.append(("Orthogonalité des extensions", "OK" if ok else "VIOLÉ (bug ?)", ""))
    ok, k = verifier_semi_monotonie(theorie)
    rapport.append(("Semi-monotonie", "OK" if ok else f"VIOLÉ au défaut {k + 1}", ""))
    return rapport


def reparations(theorie, max_taille=3):
    """Minimal sets of defaults whose removal makes an extension exist."""
    inst = instancier(theorie)
    n = len(inst.defauts)
    if extensions(theorie):
        return []                      # nothing to repair
    trouvees = []
    for k in range(1, min(n, max_taille) + 1):
        for retire in combinations(range(n), k):
            if any(set(t) <= set(retire) for t in trouvees):
                continue
            restants = [i for i in range(n) if i not in retire]
            if extensions(_sous_theorie(inst, restants)):
                trouvees.append(retire)
    return [[str(inst.defauts[i]) for i in r] for r in trouvees]