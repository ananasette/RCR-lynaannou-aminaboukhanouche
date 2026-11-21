from dataclasses import dataclass


@dataclass
class Surprise:
    type: str          # "Théorème", "Définition" or "Exemple"
    titre: str
    enonce: str        # the formal statement
    explication: str   # plain-language explanation shown after the reveal
    exemple: str       # a concrete example from the app
    source: str


CATALOGUE = [
    Surprise(
        "Définition", "Extension (point fixe de Γ)",
        "E est une extension de (W, D) ssi E = Γ(E), où Γ(E) est le plus petit "
        "ensemble S tel que : (1) W ⊆ S ; (2) Th(S) = S ; (3) pour tout défaut "
        "α : β / γ de D, si α ∈ S et ¬β ∉ E, alors γ ∈ S.",
        "On devine un ensemble E de croyances, puis on vérifie qu'en repartant de W "
        "et en appliquant les défauts (justifications testées contre E), on retrouve "
        "exactement E. Une extension est donc un ensemble de croyances stable : "
        "il se justifie lui-même.",
        "Tweety : E = Th({oiseau(tweety), vole(tweety)}). Partir de W et appliquer "
        "le défaut redonne bien E.",
        "Reiter, A Logic for Default Reasoning, 1980"),

    Surprise(
        "Théorème", "Caractérisation quasi-inductive",
        "E est une extension ssi E = ∪ Eᵢ avec E₀ = W et "
        "Eᵢ₊₁ = Th(Eᵢ) ∪ { γ | α : β / γ ∈ D, α ∈ Eᵢ, ¬β ∉ E }.",
        "C'est la construction pas à pas d'une extension : à chaque étape on ajoute "
        "les conclusions des défauts dont le prérequis est déjà dérivé. Attention, "
        "la condition ¬β ∉ E porte sur E final, pas sur Eᵢ : c'est pour cela qu'on "
        "dit « quasi » inductif, car il faut deviner E à l'avance.",
        "Nixon avec E contenant pacifiste : E₁ ajoute pacifiste (quaker ∈ E₀ et "
        "¬pacifiste ∉ E). Le défaut républicain est bloqué.",
        "Reiter, 1980"),

    Surprise(
        "Théorème", "W incohérent",
        "Si W est incohérent, alors la seule extension de (W, D) est l'ensemble "
        "de toutes les formules.",
        "D'une contradiction tout se déduit (ex falso quodlibet), donc Th(W) contient "
        "déjà tout. Les défauts ne peuvent plus rien changer. C'est pourquoi les "
        "théorèmes de Reiter exigent un W cohérent.",
        "W = {p, ~p} : toute formule, y compris q et ~q, est conséquence.",
        "Reiter, 1980"),

    Surprise(
        "Théorème", "Existence (théories normales)",
        "Toute théorie normale fermée (W, D), avec W cohérent, possède au moins "
        "une extension.",
        "Un défaut normal α : β / β ne peut pas saboter sa propre justification : "
        "on suppose β cohérent puis on conclut β. Aucune contradiction interne "
        "n'est possible, donc le processus ne peut pas échouer sur lui-même.",
        "Nixon est normal : 2 extensions. Contre-exemple non normal : "
        "« : A / ~A » n'en a aucune.",
        "Reiter, 1980"),

    Surprise(
        "Théorème", "Orthogonalité",
        "Si E₁ et E₂ sont deux extensions distinctes d'une théorie normale fermée, "
        "alors E₁ ∪ E₂ est incohérent.",
        "Deux croyances rivales d'une théorie normale ne sont pas seulement "
        "différentes : elles se contredisent. Il n'existe pas de « demi-désaccord ».",
        "Nixon : une extension contient pacifiste, l'autre ~pacifiste. Leur union "
        "est incohérente.",
        "Reiter, 1980"),

    Surprise(
        "Théorème", "Semi-monotonie",
        "Pour des théories normales (W, D) et (W, D′) avec D ⊆ D′, toute extension "
        "de (W, D) est incluse dans une extension de (W, D′).",
        "Ajouter des défauts ne détruit jamais ce qu'on croyait déjà : cela peut "
        "seulement l'enrichir. Attention, ajouter un fait, lui, peut retirer des "
        "conclusions : c'est la non-monotonie.",
        "Tweety vole. On ajoute « les oiseaux ont des ailes » : il vole toujours, "
        "et il a des ailes.",
        "Reiter, 1980"),

    Surprise(
        "Théorème", "Processus clos et réussi",
        "E est une extension ssi E = In(Π) pour un processus Π à la fois clos "
        "(aucun défaut applicable en dehors de Π) et réussi (In(Π) ∩ Out(Π) = ∅).",
        "C'est la base de ton arbre de processus : on applique des défauts un à un, "
        "In note ce qu'on croit, Out note ce qu'on s'est interdit de croire. "
        "Une branche qui croit ce qu'elle s'est interdit échoue.",
        "« : A / ~A » : In = Th(~A), Out = {~A}, donc In ∩ Out ≠ ∅ : échec.",
        "Reiter, 1980"),

    Surprise(
        "Définition", "Crédule vs sceptique",
        "φ est une conséquence crédule de T si φ appartient à au moins une "
        "extension ; sceptique si φ appartient à toutes les extensions "
        "(et qu'il en existe au moins une, dans ton implémentation).",
        "Crédule = « c'est possible », sceptique = « c'est sûr ». Face à des "
        "extensions rivales, l'agent crédule choisit un camp, le sceptique "
        "s'abstient de trancher.",
        "Nixon : pacifiste est crédule (extension 1) mais pas sceptique.",
        "Littérature classique de la logique des défauts"),

    Surprise(
        "Exemple", "Le diamant de Nixon",
        "W = {quaker, républicain}, D = {quaker : pacifiste / pacifiste, "
        "républicain : ~pacifiste / ~pacifiste}.",
        "Deux défauts légitimes tirent en sens opposés. Appliquer l'un bloque "
        "l'autre, d'où deux extensions orthogonales. Le sceptique ne conclut rien, "
        "le crédule peut conclure l'un ou l'autre.",
        "Menu : d, puis 2, puis 6.",
        "Reiter & Criscuolo, 1981"),

    Surprise(
        "Exemple", "Pas d'extension : « : A / ~A »",
        "D = { : A / ~A }, W = ∅.",
        "On suppose A cohérent, donc on conclut ~A, ce qui contredit l'hypothèse. "
        "Si le défaut n'est pas appliqué, il reste applicable, donc le processus "
        "n'est pas clos. Aucune issue : pas d'extension.",
        "Menu : 2 avec « : A / ~A », puis 6, puis r pour la réparation.",
        "Reiter, 1980"),
]

_PAR_TITRE = {s.titre: s for s in CATALOGUE}

DECLENCHEURS = {
    "reiter": ["Extension (point fixe de Γ)", "Caractérisation quasi-inductive"],
    "1980":   ["Processus clos et réussi", "W incohérent"],
    "theory": ["Crédule vs sceptique", "Pas d'extension : « : A / ~A »"],
    "67":     ["Existence (théories normales)", "Orthogonalité"],
    "13":     ["Semi-monotonie", "Le diamant de Nixon"],
}

_compteurs = {k: 0 for k in DECLENCHEURS}


def est_secret(code):
    """True if the typed text is a hidden trigger."""
    return code.strip().lower() in DECLENCHEURS


def surprise(code):
    """Return the Surprise tied to this trigger; repeating the trigger
    alternates between its entries."""
    cle = code.strip().lower()
    titres = DECLENCHEURS[cle]
    choix = _PAR_TITRE[titres[_compteurs[cle] % len(titres)]]
    _compteurs[cle] += 1
    return choix