import csv
from core.tarifs import Tarif

class GrilleTarifs:
    """
    Charge les tarifs depuis un fichier CSV.
    """

    def __init__(self):
        self.tarifs = {}

    @classmethod
    def depuis_fichier(cls, fichier: str):
        grille = cls()

        with open(fichier, newline="", encoding="utf-8") as f:
            lecteur = csv.DictReader(f, delimiter=";")
            for ligne in lecteur:
                grille.tarifs[ligne["id"]] = Tarif(
                    float(ligne["prix_semaine"]),
                    float(ligne["prix_weekend"]),
                )

        return grille

    def obtenir(self, id_tarif: str) -> Tarif:
        """
        Retourne le tarif correspondant à l'identifiant donné.
        """
        if id_tarif not in self.tarifs:
            raise ValueError(f"Tarif '{id_tarif}' inexistant")
        return self.tarifs[id_tarif]