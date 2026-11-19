import json
from formulas import lire_formule, afficher_formule


class Default:
    """Default: prerequisite : justifications / conclusion"""

    def __init__(self, prerequis, justifications, conclusion):
        self.prerequis = prerequis
        self.justifications = justifications
        self.conclusion = conclusion

    @classmethod
    def depuis_texte(cls, texte):
        if ":" not in texte or "/" not in texte:
            raise ValueError("Format attendu : prérequis : justification / conclusion")
        prereq, reste = texte.split(":", 1)
        justifs, concl = reste.split("/", 1)
        prereq = lire_formule(prereq) if prereq.strip() else None
        justifs = [lire_formule(j) for j in justifs.split(";") if j.strip()]
        return cls(prereq, justifs, lire_formule(concl))

    def __str__(self):
        p = afficher_formule(self.prerequis) if self.prerequis is not None else ""
        j = " ; ".join(afficher_formule(x) for x in self.justifications)
        return f"{p} : {j} / {afficher_formule(self.conclusion)}"


class Theory:
    """Default theory (W, D)."""

    def __init__(self):
        self.faits = []
        self.defauts = []
        self._src_faits = []
        self._src_defauts = []

    def ajouter_fait(self, texte):
        self.faits.append(lire_formule(texte))
        self._src_faits.append(texte.strip())

    def ajouter_defaut(self, texte):
        self.defauts.append(Default.depuis_texte(texte))
        self._src_defauts.append(texte.strip())

    def sauvegarder(self, chemin):
        """Plain text: one fact or default per line (facts first)."""
        with open(chemin, "w", encoding="utf-8") as f:
            for x in self._src_faits + self._src_defauts:
                f.write(x + "\n")

    @classmethod
    def charger(cls, chemin):
        with open(chemin, encoding="utf-8") as f:
            contenu = f.read()
        t = cls()
        if contenu.lstrip().startswith("{"):      # old JSON format
            data = json.loads(contenu)
            faits, defauts = data["faits"], data["defauts"]
        else:
            faits, defauts = [], []
            for ligne in contenu.splitlines():
                ligne = ligne.strip()
                if not ligne or ligne.startswith("#"):
                    continue
                (defauts if (":" in ligne and "/" in ligne) else faits).append(ligne)
        for x in faits:
            t.ajouter_fait(x)
        for x in defauts:
            t.ajouter_defaut(x)
        return t

    def __str__(self):
        w = "\n".join(f"  {afficher_formule(f)}" for f in self.faits) or "  (vide)"
        d = "\n".join(f"  {x}" for x in self.defauts) or "  (vide)"
        return f"W =\n{w}\nD =\n{d}"