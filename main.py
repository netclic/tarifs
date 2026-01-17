import argparse
from datetime import date
from utils import date_fr
from grille_tarifs import GrilleTarifs
from calendrier_tarifaire import CalendrierTarifaire
from calculateur import CalculateurLocation
from tableau_tarifs import TableauTarifs


def demander_date(message: str) -> date:
    """
    Demande une date à l'utilisateur jusqu'à obtention d'un format valide.
    """
    while True:
        try:
            return date_fr(input(message))
        except ValueError as e:
            print(e)


def main():
    parser = argparse.ArgumentParser(description="Calcul de location saisonnière")
    parser.add_argument("--date_debut", help="JJ-MM-AAAA")
    parser.add_argument("--date_fin", help="JJ-MM-AAAA")
    parser.add_argument("--tableau", action="store_true",
                        help="Afficher le tableau résumé par période pour la plage de dates")
    args = parser.parse_args()

    # Gestion des dates (CLI ou saisie)
    if args.date_debut and args.date_fin:
        date_debut = date_fr(args.date_debut)
        date_fin = date_fr(args.date_fin)
    else:
        print("Dates absentes ou incomplètes → saisie requise")
        date_debut = demander_date("Date de début (JJ-MM-AAAA) : ")
        date_fin = demander_date("Date de fin   (JJ-MM-AAAA) : ")

    if date_fin <= date_debut:
        raise ValueError("La date de fin doit être postérieure à la date de début")

    # Chargement des fichiers CSV
    grille = GrilleTarifs.depuis_fichier("prix.csv")
    calendrier = CalendrierTarifaire.depuis_fichier("periode.csv", grille)
    calculateur = CalculateurLocation(calendrier, grille)

    # ---------- Mode tableau ----------
    if args.tableau:
        tableau = TableauTarifs(calculateur)
        tableau.afficher_plage(date_debut, date_fin)
        tableau.exporter_csv_plage("tableau_tarifs_plage.csv", date_debut, date_fin)
        print("\nTableau exporté dans 'tableau_tarifs_plage.csv'")
        return  # On ne fait plus le détail journalier

    # ---------- Mode normal : détail journalier ----------
    details, total = calculateur.calculer(date_debut, date_fin)
    print("\nDétail journalier :")
    for jour, prix in details:
        print(f"{jour.strftime('%d-%m-%Y')} : {prix:.2f} €")
    print(f"\nPrix total : {total:.2f} €")



if __name__ == "__main__":
    main()