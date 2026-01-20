import csv
from datetime import date, timedelta
from core.periode import Periode
from core.utils import date_fr

class CalendrierTarifaire:
    """
    Gère la chronologie des périodes tarifaires et assure leur cohérence.

    Cette classe permet de charger des périodes depuis un fichier CSV, de vérifier
    qu'elles se suivent sans trou ni chevauchement, et de retrouver le tarif
    applicable à une date précise.
    """

    def __init__(self, periodes):
        """
        Initialise le calendrier avec une liste d'objets Periode.

        :param periodes: Liste d'instances de la classe Periode.
        """
        self.periodes = sorted(periodes, key=lambda p: p.debut)

    @classmethod
    def depuis_fichier(cls, fichier: str, grille_tarifs):
        """
        Crée une instance de CalendrierTarifaire à partir d'un fichier CSV.

        Le fichier doit utiliser le point-virgule (;) comme délimiteur et 
        contenir les colonnes 'id', 'date_debut' et 'date_fin'.

        :param fichier: Chemin vers le fichier CSV des périodes.
        :param grille_tarifs: Instance de GrilleTarifs pour validation des IDs.
        :return: Une instance configurée de CalendrierTarifaire.
        :raises ValueError: Si un ID de tarif est inconnu ou si les périodes 
                            ne sont pas consécutives.
        """
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
        """
        Vérifie que chaque période commence exactement le lendemain de la précédente.

        :raises ValueError: Si un écart ou un chevauchement est détecté entre deux périodes.
        """
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
        Identifie la période correspondant à une date spécifique.

        :param jour: La date (objet date) à rechercher.
        :return: L'objet Periode englobant cette date.
        :raises ValueError: Si la date ne correspond à aucune période définie.
        """
        for periode in self.periodes:
            if periode.contient(jour):
                return periode

        raise ValueError(f"Aucune période trouvée pour {jour}")