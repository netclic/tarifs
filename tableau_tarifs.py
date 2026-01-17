import csv
from datetime import timedelta, date

class TableauTarifs:
    """
    Génère un tableau récapitulatif des périodes et tarifs,
    et permet de l'afficher ou de l'exporter en CSV.
    """

    def __init__(self, calculateur):
        """
        :param calculateur: instance de CalculateurLocation
        """
        self.calculateur = calculateur

    # ---------- Tableau complet ----------
    def generer_tableau(self):
        """
        Génère le tableau complet (toutes les périodes) avec colonne Prix à la semaine.
        """
        tableau = []
        for periode in self.calculateur.calendrier.periodes:
            tarif = self.calculateur.grille_tarifs.obtenir(periode.id_tarif)
            duree = (periode.fin - periode.debut).days + 1
            if duree >= 7:
                total_semaine = 0
                for i in range(7):
                    jour_courant = periode.debut + timedelta(days=i)
                    total_semaine += tarif.prix_pour_jour(jour_courant)
                prix_semaine_7j = f"{total_semaine:.2f} €"
            else:
                prix_semaine_7j = "période trop courte"

            tableau.append({
                "debut": periode.debut.strftime("%d-%m-%Y"),
                "fin": periode.fin.strftime("%d-%m-%Y"),
                "periode": periode.id_tarif,
                "prix_semaine_unit": f"{tarif.prix_semaine:.2f}",
                "prix_weekend_unit": f"{tarif.prix_weekend:.2f}",
                "prix_semaine_7j": prix_semaine_7j
            })
        return tableau

    def afficher(self):
        """
        Affiche le tableau complet dans la console.
        """
        print(f"\nTableau des périodes et tarifs (toutes périodes)")
        print(f"{'Début':<12} {'Fin':<12} {'Période':<8} "
              f"{'Prix semaine':<12} {'Prix weekend':<12} {'Prix 7j':<20}")
        print("-" * 80)
        for ligne in self.generer_tableau():
            print(f"{ligne['debut']:<12} {ligne['fin']:<12} "
                  f"{ligne['periode']:<8} {ligne['prix_semaine_unit']:<12} "
                  f"{ligne['prix_weekend_unit']:<12} {ligne['prix_semaine_7j']:<20}")
        print("\nWARNING : La colonne 'Prix à la semaine' est donnée à titre indicatif.")

    def exporter_csv(self, chemin_fichier):
        """
        Exporte le tableau complet dans un fichier CSV.
        """
        with open(chemin_fichier, "w", newline="", encoding="utf-8") as f:
            champs = ["debut", "fin", "periode", "prix_semaine_unit", "prix_weekend_unit", "prix_semaine_7j"]
            writer = csv.DictWriter(f, fieldnames=champs, delimiter=";")
            writer.writeheader()
            for ligne in self.generer_tableau():
                writer.writerow(ligne)

    # ---------- Tableau limité à une plage ----------
    def generer_tableau_plage(self, date_debut: date, date_fin: date):
        """
        Génère un tableau limité à la plage [date_debut, date_fin].
        Découpe la première et dernière ligne si nécessaire.
        Ajoute colonne Prix à la semaine.
        """
        tableau = []
        jour = date_debut

        while jour < date_fin:
            periode = self.calculateur.calendrier.periode_pour_jour(jour)
            tarif = self.calculateur.grille_tarifs.obtenir(periode.id_tarif)

            debut_ligne = jour
            fin_ligne = min(periode.fin, date_fin - timedelta(days=1))

            duree = (fin_ligne - debut_ligne).days + 1
            if duree >= 7:
                total_semaine = 0
                for i in range(7):
                    jour_courant = debut_ligne + timedelta(days=i)
                    if jour_courant > fin_ligne:
                        break
                    total_semaine += tarif.prix_pour_jour(jour_courant)
                prix_semaine_7j = f"{total_semaine:.2f} €"
            else:
                prix_semaine_7j = "période trop courte"

            tableau.append({
                "debut": debut_ligne.strftime("%d-%m-%Y"),
                "fin": fin_ligne.strftime("%d-%m-%Y"),
                "periode": periode.id_tarif,
                "prix_semaine_unit": f"{tarif.prix_semaine:.2f}",
                "prix_weekend_unit": f"{tarif.prix_weekend:.2f}",
                "prix_semaine_7j": prix_semaine_7j
            })

            jour = fin_ligne + timedelta(days=1)

        return tableau

    def afficher_plage(self, date_debut: date, date_fin: date):
        """
        Affiche le tableau limité à la plage spécifiée avec colonne Prix à la semaine.
        """
        print(f"\nTableau des périodes et tarifs ({date_debut.strftime('%d-%m-%Y')} → {date_fin.strftime('%d-%m-%Y')})")
        print(f"{'Début':<12} {'Fin':<12} {'Période':<8} "
              f"{'Prix semaine':<12} {'Prix weekend':<12} {'Prix 7j':<20}")
        print("-" * 80)
        for ligne in self.generer_tableau_plage(date_debut, date_fin):
            print(f"{ligne['debut']:<12} {ligne['fin']:<12} "
                  f"{ligne['periode']:<8} {ligne['prix_semaine_unit']:<12} "
                  f"{ligne['prix_weekend_unit']:<12} {ligne['prix_semaine_7j']:<20}")
        print("\nWARNING : La colonne 'Prix à la semaine' est donnée à titre indicatif.")

    def exporter_csv_plage(self, chemin_fichier, date_debut: date, date_fin: date):
        """
        Exporte le tableau limité à la plage dans un CSV.
        """
        with open(chemin_fichier, "w", newline="", encoding="utf-8") as f:
            champs = ["debut", "fin", "periode", "prix_semaine_unit", "prix_weekend_unit", "prix_semaine_7j"]
            writer = csv.DictWriter(f, fieldnames=champs, delimiter=";")
            writer.writeheader()
            for ligne in self.generer_tableau_plage(date_debut, date_fin):
                writer.writerow(ligne)
