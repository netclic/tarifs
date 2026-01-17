import csv
from datetime import date, timedelta
from periode import Periode
from utils import date_fr

class CalendrierTarifaire:
    """
    Gère les périodes tarifaires issues d'un CSV.
    """

    def __init__(self, periodes):
        self.periodes = sorted(periodes, key=lambda p: p.debut)

    @classmethod
    def depuis_fichier(cls, fichier: str, grille_tarifs):
        periodes = []

        with open(fichier, newline="", encoding="utf-8") as f:
            lecteur = csv.DictReader(f, delimiter=";")
            for ligne in lecteur:
                id_tarif = ligne["id"]

                if id_tarif not in grille_tarifs.tarifs:
                    raise ValueError(
                        f"Tarif '{id_tarif}' absent de prix.csv"
                    )

                periodes.append(
                    Periode(
                        date_fr(ligne["date_debut"]),
                        date_fr(ligne["date_fin"]),
                        id_tarif,
                    )
                )

        calendrier = cls(periodes)
        calendrier._verifier_consecutivite()
        return calendrier

    def _verifier_consecutivite(self):
        for i in range(1, len(self.periodes)):
            prec = self.periodes[i - 1]
            curr = self.periodes[i]

            if curr.debut != prec.fin + timedelta(days=1):
                raise ValueError(
                    "Périodes non consécutives : "
                    f"{prec.fin} -> {curr.debut}"
                )


    def periode_pour_jour(self, jour: date) -> Periode:
        """
        Retourne la période correspondant à une date donnée.
        """
        for periode in self.periodes:
            if periode.contient(jour):
                return periode

        raise ValueError(f"Aucune période trouvée pour {jour}")
