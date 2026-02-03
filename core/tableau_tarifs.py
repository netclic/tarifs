import csv
from datetime import date, timedelta
from decimal import Decimal, ROUND_UP


class TableauTarifs:
    """
    Génère des tableaux récapitulatifs des périodes tarifaires,
    avec option de commission par plateforme.
    """

    COMMISSIONS = {
        "airbnb": 0.036,
        "booking": 0.164,
        "abritel": 0.08,
        "gites" : 0.03
    }

    def __init__(self, calculateur, plateforme=None):
        """
        :param calculateur: instance de CalculateurLocation
        :param plateforme: str, nom de la plateforme ('airbnb', 'booking', 'abritel')
        """
        self.calculateur = calculateur
        self.plateforme = plateforme.lower() if plateforme else None

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------
    def ajuster_prix(self, prix: float) -> int:
        """
        Ajuste le prix pour conserver le NET après commission
        et arrondit TOUJOURS à l'euro supérieur.
        """
        if self.plateforme in self.COMMISSIONS:
            taux = Decimal(str(self.COMMISSIONS[self.plateforme]))
            brut = Decimal(str(prix)) / (Decimal("1") - taux)
            return int(brut.quantize(Decimal("1"), rounding=ROUND_UP))

        return int(Decimal(str(prix)).quantize(Decimal("1"), rounding=ROUND_UP))


    def _prix_7_jours(self, debut: date, fin: date, tarif) -> str:
        """
        Calcule le prix pour 7 jours consécutifs à partir de 'debut'.
        Retourne une chaîne formatée sans le symbole € pour le CSV.
        """
        duree = (fin - debut).days + 1
        if duree < 7:
            return "trop court"

        total = 0.0
        for i in range(7):
            jour = debut + timedelta(days=i)
            prix_net = tarif.prix_pour_jour(jour)
            total += self.ajuster_prix(prix_net)

        return f"{total:.2f}" # On retire le € ici

    # ------------------------------------------------------------------
    # TABLEAU COMPLET (toutes les périodes)
    # ------------------------------------------------------------------
    def generer_tableau(self):
        """
        Génère le tableau pour toutes les périodes connues.
        """
        tableau = []

        for periode in self.calculateur.calendrier.periodes:
            tarif = self.calculateur.grille_tarifs.obtenir(periode.id_tarif)

            tableau.append({
                "debut": periode.debut.strftime("%d-%m-%Y"),
                "fin": periode.fin.strftime("%d-%m-%Y"),
                "periode": periode.id_tarif,
                "prix_semaine_unit": f"{self.ajuster_prix(tarif.prix_semaine):.2f}",
                "prix_weekend_unit": f"{self.ajuster_prix(tarif.prix_weekend):.2f}",
                "prix_semaine_7j": self._prix_7_jours(
                    periode.debut, periode.fin, tarif
                ),
            })

        return tableau

    def afficher(self):
        """
        Affiche le tableau complet dans la console.
        """
        print("\nTableau des périodes et tarifs (toutes périodes)")
        self._afficher_lignes(self.generer_tableau())

    def exporter_csv(self, chemin_fichier: str):
        """
        Exporte le tableau complet en CSV.
        """
        self._exporter_csv(chemin_fichier, self.generer_tableau())

    # ------------------------------------------------------------------
    # TABLEAU LIMITÉ À UNE PLAGE DE DATES
    # ------------------------------------------------------------------
    def generer_tableau_plage(self, date_debut: date, date_fin: date):
        """
        Génère le tableau limité à une plage de dates.
        Les périodes sont découpées si nécessaire.
        """
        tableau = []
        jour = date_debut

        while jour <= date_fin:
            periode = self.calculateur.calendrier.periode_pour_jour(jour)
            tarif = self.calculateur.grille_tarifs.obtenir(periode.id_tarif)

            debut_ligne = jour
            fin_ligne = min(periode.fin, date_fin)

            tableau.append({
                "debut": debut_ligne.strftime("%d-%m-%Y"),
                "fin": fin_ligne.strftime("%d-%m-%Y"),
                "periode": periode.id_tarif,
                "prix_semaine_unit": f"{self.ajuster_prix(tarif.prix_semaine):.2f}",
                "prix_weekend_unit": f"{self.ajuster_prix(tarif.prix_weekend):.2f}",
                "prix_semaine_7j": self._prix_7_jours(
                    debut_ligne, fin_ligne, tarif
                ),
            })

            jour = fin_ligne + timedelta(days=1)

        return tableau

    def afficher_plage(self, date_debut: date, date_fin: date):
        """
        Affiche le tableau limité à une plage de dates.
        """
        print(
            f"\nTableau des périodes et tarifs "
            f"({date_debut.strftime('%d-%m-%Y')} → {date_fin.strftime('%d-%m-%Y')})"
        )
        self._afficher_lignes(self.generer_tableau_plage(date_debut, date_fin))

    def exporter_csv_plage(self, chemin_fichier: str, date_debut: date, date_fin: date):
        """
        Exporte le tableau limité à une plage en CSV.
        """
        self._exporter_csv(
            chemin_fichier,
            self.generer_tableau_plage(date_debut, date_fin)
        )

    # ------------------------------------------------------------------
    # AFFICHAGE & EXPORT COMMUNS
    # ------------------------------------------------------------------
    def _afficher_lignes(self, lignes):
        if self.plateforme:
            taux = self.COMMISSIONS.get(self.plateforme, 0)
            print(f"MODE : Commission {self.plateforme.capitalize()} incluse ({taux*100:.1f}%)")
        else:
            print("MODE : Tarifs nets (aucune commission)")

        print("-" * 80)

        print(
            f"{'Début':<12} {'Fin':<12} {'Période':<15} "
            f"{'Prix semaine':<12} {'Prix weekend':<12} {'Prix 7j':<20}"
        )
        print("-" * 80)

        for l in lignes:
            print(
                f"{l['debut']:<12} {l['fin']:<12} {l['periode']:<15} "
                f"{l['prix_semaine_unit']:<12} {l['prix_weekend_unit']:<12} "
                f"{l['prix_semaine_7j']:<20}"
            )

        print("\nWARNING : La colonne 'Prix à la semaine' est donnée à titre indicatif.")

    def _exporter_csv(self, chemin_fichier: str, lignes):
        champs = [
            "debut",
            "fin",
            "periode",
            "prix_semaine_unit",
            "prix_weekend_unit",
            "prix_semaine_7j",
        ]

        # On utilise 'utf-8-sig' pour ajouter un BOM (Byte Order Mark)
        # Cela permet à LibreOffice/Excel de reconnaître l'UTF-8 immédiatement.
        with open(chemin_fichier, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=champs, delimiter=";")
            writer.writeheader()
            for ligne in lignes:
                writer.writerow(ligne)