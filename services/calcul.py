from pathlib import Path
from core.calculateur import CalculateurLocation
from core.calendrier_tarifaire import CalendrierTarifaire
from core.grille_tarifs import GrilleTarifs
from core.tableau_tarifs import TableauTarifs
from datetime import date

# On définit le chemin des dossiers par rapport à la racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

# On s'assure que le dossier results existe
RESULTS_DIR.mkdir(exist_ok=True)

def obtenir_calculateur() -> CalculateurLocation:
    """Initialise et retourne le moteur de calcul en utilisant le dossier data."""
    grille = GrilleTarifs.depuis_fichier(str(DATA_DIR / "prix.csv"))
    calendrier = CalendrierTarifaire.depuis_fichier(str(DATA_DIR / "periode.csv"), grille)
    return CalculateurLocation(calendrier, grille)


def calcul_tableau(date_debut: date, date_fin: date, plateforme: str = None):
    """
    Logique utilisée par FastAPI et le CLI pour obtenir les données du tableau.
    """
    calculateur = obtenir_calculateur()
    tableau = TableauTarifs(calculateur, plateforme=plateforme)

    # GÉNÉRATION DU CSV pour permettre le téléchargement immédiat
    nom_fichier = f"tableau_tarifs_{plateforme}.csv" if plateforme else "tableau_tarifs.csv"
    tableau.exporter_csv_plage(str(RESULTS_DIR / nom_fichier), date_debut, date_fin)

    # On utilise le bon nom de méthode : generer_tableau_plage
    return tableau.generer_tableau_plage(date_debut, date_fin)


def calcul_detail(date_debut: date, date_fin: date):
    """
    Logique pour obtenir le calcul détaillé (utilisé par le CLI et l'API).
    """
    calculateur = obtenir_calculateur()
    return calculateur.calculer(date_debut, date_fin)