from datetime import date

class Tarif:
    """
    Représente un tarif avec un prix semaine et un prix week-end.
    """

    def __init__(self, prix_semaine: float, prix_weekend: float):
        self.prix_semaine = prix_semaine
        self.prix_weekend = prix_weekend

    def prix_pour_jour(self, jour: date) -> float:
        """
        Retourne le prix applicable pour une date donnée.
        Samedi (5) et dimanche (6) = week-end.
        """
        if jour.weekday() >= 5:
            return self.prix_weekend
        return self.prix_semaine