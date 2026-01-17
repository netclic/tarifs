from datetime import date, timedelta

class CalculateurLocation:
    """
    Calcule le prix journalier et total d'une location saisonnière.
    """

    def __init__(self, calendrier, grille_tarifs):
        self.calendrier = calendrier
        self.grille_tarifs = grille_tarifs

    def calculer(self, date_debut: date, date_fin: date):
        """
        Calcule le détail jour par jour et le total.
        """
        jour = date_debut
        total = 0.0
        details = []

        while jour <= date_fin:
            periode = self.calendrier.periode_pour_jour(jour)
            tarif = self.grille_tarifs.obtenir(periode.id_tarif)

            montant = tarif.prix_pour_jour(jour)

            details.append((jour, montant))
            total += montant
            jour += timedelta(days=1)

        return details, total
