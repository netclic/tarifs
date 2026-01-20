from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from datetime import date, timedelta
from services.calcul import calcul_tableau, calcul_detail, RESULTS_DIR
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from core.utils import formater_date_jour

import os

# On récupère le chemin absolu du projet pour éviter les erreurs 404
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Tarifs Location")

# On monte le dossier static pour les fichiers CSS/JS
app.mount("/static", StaticFiles(directory=os.path.join(BASE_PATH, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_PATH, "templates"))


@app.get("/")
def home(request: Request):
    # Calcul des dates par défaut (7 nuitées)
    aujourdhui = date.today()
    jour_depart = aujourdhui + timedelta(days=7) # Aujourd'hui + 7 jours
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "default_debut": aujourdhui.isoformat(),
        "default_fin": jour_depart.isoformat()
    })

@app.get("/tableau")
def tableau(
    date_debut: date = Query(...),
    date_fin: date = Query(...),
    plateforme: str = Query(None, enum=["airbnb", "booking", "abritel"])
):
    # On calcule jusqu'à la veille du départ
    derniere_nuitee = date_fin - timedelta(days=1)
    return calcul_tableau(date_debut, derniere_nuitee, plateforme)


@app.get("/detail")
def detail(
    date_debut: date = Query(...),
    date_fin: date = Query(...)
):
    # On calcule jusqu'à la veille du départ
    derniere_nuitee = date_fin - timedelta(days=1)
    details, total = calcul_detail(date_debut, derniere_nuitee)
    
    nb_nuitees = len(details)
    moyenne = total / nb_nuitees if nb_nuitees > 0 else 0
    
    # On utilise formater_date_jour pour envoyer une chaîne déjà prête
    formated_details = [[formater_date_jour(d), p] for d, p in details]
    
    return {
        "details": formated_details, 
        "total": total,
        "moyenne": moyenne,
        "nb_nuitees": nb_nuitees
    }

@app.get("/download-csv")
def download_csv(plateforme: str = Query(None)):
    nom_fichier = f"tableau_tarifs_{plateforme}.csv" if plateforme else "tableau_tarifs.csv"
    file_path = RESULTS_DIR / nom_fichier

    if not file_path.exists():
        # Optionnel : générer un fichier par défaut ou renvoyer une erreur plus propre
        return {"error": "Veuillez d'abord lancer un calcul."}

    return FileResponse(path=file_path, filename=nom_fichier)