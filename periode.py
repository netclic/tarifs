from datetime import date

class Periode:
    """
    Représente une période calendaire associée à un tarif.
    """

    def __init__(self, debut: date, fin: date, id_tarif: str):
        if fin < debut:
            raise ValueError("La date de fin est antérieure à la date de début")

        self.debut = debut
        self.fin = fin
        self.id_tarif = id_tarif

    def contient(self, jour: date) -> bool:
        """
        Indique si une date appartient à cette période.
        """
        return self.debut <= jour <= self.fin
