import argparse
import sys

from calculateur import CalculateurLocation
from calendrier_tarifaire import CalendrierTarifaire
from datetime import date, timedelta
from grille_tarifs import GrilleTarifs
from pathlib import Path
from tableau_tarifs import TableauTarifs
from utils import date_fr

# Détermination du dossier de base (script Python ou .exe PyInstaller)
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent

JOURS_MINI = 2


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
    """
    # Configuration des arguments de la ligne de commande (CLI)
    parser = argparse.ArgumentParser(description="Calcul de location saisonnière")

    # Argument pour la date de début
    parser.add_argument("-d", "--date-debut", help="Date de début (JJ-MM-AAAA, ...)")

    # Argument pour la date de fin OU le nombre de jours
    group_fin = parser.add_mutually_exclusive_group()
    group_fin.add_argument("-f", "--date-fin", help="Date de fin (JJ-MM-AAAA, ...)")
    group_fin.add_argument("-n", "--nb-jours", type=int, help="Nombre de jours de location")

    # Switch pour activer le mode tableau
    parser.add_argument("-t", "--tableau", action="store_true",
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

    # --- Gestion des dates ---
    date_debut = None
    date_fin = None

    # 1. Date de début
    if args.date_debut:
        date_debut = date_fr(args.date_debut)
    else:
        print("Date de début absente → saisie requise")
        date_debut = demander_date("Date de début : ")

    # 2. Date de fin (calculée ou saisie)
    if args.nb_jours:
        if args.nb_jours < JOURS_MINI:
            raise ValueError(f"La durée minimum de séjour est de {JOURS_MINI} jours.")
        # Si on a un nombre de jours, la date de fin est début + (N-1) jours
        # (Ex: début le 1er, 3 jours -> 1, 2, 3. Fin le 3)
        date_fin = date_debut + timedelta(days=args.nb_jours - 1)
    elif args.date_fin:
        date_fin = date_fr(args.date_fin)
    else:
        print("Date de fin ou durée absente → saisie requise")
        choix = input("Voulez-vous saisir une (f)in ou une (d)urée ? [f/d] : ").lower()
        if choix == 'd':
            while True:
                try:
                    n = int(input("Nombre de jours : "))
                    if n < JOURS_MINI:
                        print(f"Erreur : Le séjour doit être de {JOURS_MINI} jours minimum.")
                        continue
                    date_fin = date_debut + timedelta(days=n - 1)
                    break
                except ValueError:
                    print("Veuillez saisir un nombre entier.")
        else:
            while True:
                date_fin = demander_date(f"Date de fin (séjour mini {JOURS_MINI} jours) : ")
                if (date_fin - date_debut).days + 1 < JOURS_MINI:
                    print(
                        f"Erreur : La date de fin doit être au moins le {(date_debut + timedelta(days=1)).strftime('%d/%m/%Y')}")
                else:
                    break

    # Validation métier finale
    nb_jours = (date_fin - date_debut).days + 1
    if nb_jours < JOURS_MINI:
        raise ValueError(f"Séjour trop court ({nb_jours} jour(s)). Le minimum est de {JOURS_MINI} jours.")

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
        nom_fichier = f"tableau_tarifs_{plateforme}.csv" if plateforme else "tableau_tarifs.csv"
        tableau.exporter_csv_plage(nom_fichier, date_debut, date_fin)
        print("\nTableau exporté dans 'tableau_tarifs_plage.csv'")
        return

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