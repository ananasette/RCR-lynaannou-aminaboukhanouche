from theorem import audit, reparations
from formulas import lire_formule, afficher_formule
from defaults import Theory
from reasoning import (est_coherent, consequence,
                       formules_incoherentes, sous_ensembles_incoherents)
from extensions import extensions, consequence_credulous, consequence_sceptique
from surprise import est_secret, surprise


MENU = """
================ Logique des défauts ================
 1. Ajouter un fait (W)            2. Ajouter un défaut (D)
 3. Afficher la théorie            4. Cohérence de W
 5. W |= formule ?                 6. Calculer les extensions
 7. Conséquence crédule/sceptique  8. Sauvegarder
 9. Charger                        d. Charger un exemple (Tweety / Nixon)
 0. Quitter                        a. Audit de la théorie            
r. Réparations (supprimer des défauts)
Syntaxe: ~ & | -> <->   |  défaut:  prérequis : justif1 ; justif2 / conclusion
Exemple: oiseau(tweety) : vole(tweety) / vole(tweety)
"""


def demo(nom):
    t = Theory()
    if nom == "1":
        t.ajouter_fait("oiseau(tweety)")
        t.ajouter_defaut("oiseau(tweety) : vole(tweety) / vole(tweety)")
    else:
        t.ajouter_fait("quaker")
        t.ajouter_fait("republicain")
        t.ajouter_defaut("quaker : pacifiste / pacifiste")
        t.ajouter_defaut("republicain : ~pacifiste / ~pacifiste")
    return t


def montrer_extensions(t):
    exts = extensions(t)
    if not exts:
        print("Aucune extension.")
        return
    print(f"{len(exts)} extension(s)")
    for i, E in enumerate(exts, 1):
        print(f"Extension {i}: " + " , ".join(afficher_formule(f) for f in E.base))
        print("   littéraux :", ", ".join(afficher_formule(l) for l in E.litteraux()) or "(aucun)")
        print("   défauts appliqués :", E.noms or "(aucun)")


def main():
    t = Theory()
    while True:
        print(MENU)
        c = input("Choix > ").strip().lower()
        try:
            if c == "1":
                t.ajouter_fait(input("Fait : "))
            elif c == "2":
                t.ajouter_defaut(input("Défaut : "))
            elif c == "3":
                print(t)
            elif c == "4":
                print("W cohérent :", est_coherent(t.faits))
                for f in formules_incoherentes(t.faits):
                    print("  Formule contradictoire :", afficher_formule(f))
                for s in sous_ensembles_incoherents(t.faits):
                    print("  Sous-ensemble incohérent :", [afficher_formule(f) for f in s])
            elif c == "5":
                f = lire_formule(input("Formule : "))
                print("W |= formule :", consequence(t.faits, f))
            elif c == "6":
                montrer_extensions(t)
            elif c == "7":
                f = lire_formule(input("Formule : "))
                print("Crédule  :", consequence_credulous(t, f))
                print("Sceptique:", consequence_sceptique(t, f))
            elif c == "8":
                t.sauvegarder(input("Fichier (ex: th.json) : "))
                print("Sauvegardé.")
            elif c == "9":
                t = Theory.charger(input("Fichier : "))
                print("Chargé.")
            elif c == "d":
                t = demo(input("1 = Tweety, 2 = Nixon : ").strip())
                print(t)
            elif c == "0":
                break
            elif c == "a":
                for nom, statut, comm in audit(t):
                    print(f"  {nom} : {statut}  {comm}")
            elif c == "r":
                reps = reparations(t)
                if not reps:
                    print("Rien à réparer (une extension existe déjà).")
                for r in reps:
                    print("  Retirer :", r)
            elif est_secret(c):
                s = surprise(c)
                print(f"\n*** {s.type} : {s.titre} ***")
                print(s.enonce)
                input("\n[Entrée pour l'explication] ")
                print("\nExplication :", s.explication)
                print("Exemple    :", s.exemple)
                print("Source     :", s.source)
            else:
                print("Choix inconnu.")
        except (ValueError, OSError) as e:
            print("ERREUR :", e)


if __name__ == "__main__":
    main()