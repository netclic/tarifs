from datetime import datetime, date


def date_fr(chaine_date: str) -> date:
    """
    Convertit une chaîne de caractères en objet date.
    Accepte plusieurs séparateurs : '-', '/', '.'
    """
    formats_possibles = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
    ]

    nettoyee = chaine_date.strip()

    for fmt in formats_possibles:
        try:
            return datetime.strptime(nettoyee, fmt).date()
        except ValueError:
            continue

    raise ValueError(
        f"Format de date invalide : '{chaine_date}'. "
        "Utilisez JJ-MM-AAAA, JJ/MM/AAAA ou JJ.MM.AAAA"
    )


def formater_date_jour(d: date) -> str:
    """Retourne la date au format 'lundi 01-01-2026'."""
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    nom_jour = jours[d.weekday()]
    return f"{nom_jour:<9} {d.strftime('%d-%m-%Y')}"