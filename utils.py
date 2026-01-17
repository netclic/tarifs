from datetime import datetime, date

def date_fr(texte: str) -> date:
    """
    Convertit une date JJ-MM-AAAA en date Python.
    """
    try:
        return datetime.strptime(texte, "%d-%m-%Y").date()
    except ValueError:
        raise ValueError(
            f"Date invalide '{texte}' (format attendu JJ-MM-AAAA)"
        )
