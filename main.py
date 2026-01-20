import argparse
import sys

from calculateur import CalculateurLocation
from calendrier_tarifaire import CalendrierTarifaire
from datetime import date
from grille_tarifs import GrilleTarifs
from pathlib import Path
from tableau_tarifs import TableauTarifs
from utils import date_fr

# Détermination du dossier de base (script Python ou .exe PyInstaller)
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent

def demander_date(message: str) -> date:
    """
    Demande une date à l'utilisateur via l'entrée standard.

    La fonction boucle tant que l'utilisateur ne saisit pas une date au format
    attendu (JJ-MM-AAAA). Elle utilise la fonction utilitaire date_fr.

    :param message: Le message d'invite à afficher à l'utilisateur.
    :return: Un objet date correspondant à la saisie.
    """
    while True:
        try:
            return date_fr(input(message))
        except ValueError as e:
            print(e)


def main():
    """
    Point d'entrée principal du script de calcul de tarifs de location.

    Le script peut être utilisé en mode interactif ou via des arguments CLI.
    Il permet soit d'afficher un détail journalier, soit de générer un tableau
    récapitulatif par période.
    """
    # Configuration des arguments de la ligne de commande (CLI)
    parser = argparse.ArgumentParser(description="Calcul de location saisonnière")

    # Argument pour la date de début au format JJ-MM-AAAA
    parser.add_argument("--date_debut", help="Date de début de séjour (JJ-MM-AAAA)")

    # Argument pour la date de fin au format JJ-MM-AAAA
    parser.add_argument("--date_fin", help="Date de fin de séjour (JJ-MM-AAAA)")

    # Switch pour activer le mode tableau (si présent, args.tableau sera True)
    parser.add_argument("--tableau", action="store_true",
                        help="Afficher le tableau résumé par période pour la plage de dates")

    # Argument pour la commission par plateforme
    parser.add_argument("-c", "--commission", choices=["airbnb", "booking", "abritel"],
                        help="Calculer le tableau avec la commission d'une plateforme")

    # On garde --airbnb pour la compatibilité ou on le retire, ici je le laisse comme alias
    parser.add_argument("--airbnb", action="store_true",
                        help="Ancien switch pour Airbnb (équivalent à -c airbnb)")

    args = parser.parse_args()

    # Unification de la plateforme
    plateforme = args.commission
    if args.airbnb:
        plateforme = "airbnb"

    # Gestion des dates : on vérifie si les deux dates ont été passées en argument
    if args.date_debut and args.date_fin:
        date_debut = date_fr(args.date_debut)
        date_fin = date_fr(args.date_fin)
    else:
        # Sinon, on bascule en mode interactif pour demander les informations manquantes
        print("Dates absentes ou incomplètes → saisie requise")
        date_debut = demander_date("Date de début (JJ-MM-AAAA) : ")
        date_fin = demander_date("Date de fin   (JJ-MM-AAAA) : ")

    # Validation métier : le séjour doit durer au moins une nuit
    if date_fin <= date_debut:
        raise ValueError("La date de fin doit être postérieure à la date de début")

    # Initialisation de la logique métier à partir des fichiers de configuration
    # 1. Chargement des tarifs unitaires
    grille = GrilleTarifs.depuis_fichier(str(BASE_DIR / "prix.csv"))

    # 2. Chargement du calendrier des périodes (haute saison, basse saison, etc.)
    calendrier = CalendrierTarifaire.depuis_fichier(str(BASE_DIR / "periode.csv"), grille)
    # 3. Création du moteur de calcul
    calculateur = CalculateurLocation(calendrier, grille)

    # Si une commission est demandée, on force le mode tableau
    if plateforme:
        args.tableau = True

    # ---------- Mode tableau ----------
    # Ce mode regroupe les jours par périodes tarifaires identiques
    if args.tableau:
        tableau = TableauTarifs(calculateur, plateforme=plateforme)
        # Affichage dans la console
        tableau.afficher_plage(date_debut, date_fin)
        # Génération du fichier de sortie CSV
        tableau.exporter_csv_plage("tableau_tarifs_plage.csv", date_debut, date_fin)
        print("\nTableau exporté dans 'tableau_tarifs_plage.csv'")
        return  # <--- IL MANQUAIT CE RETURN ICI

    # ---------- Mode normal : détail journalier ----------
    details, total = calculateur.calculer(date_debut, date_fin)
    nb_jours = (date_fin - date_debut).days + 1

    print("\nDétail journalier :")
    for jour, prix in details:
        print(f"{jour.strftime('%d-%m-%Y')} : {prix:.2f} €")
    print(f"\nPrix total : {total:.2f} €, pour {nb_jours} jours.")
    print(f"\nPrix moyen journalier : {total/nb_jours:.2f} €.")


if __name__ == "__main__":
    main()