# grant_navigator/sources.py

"""
Grant Navigator – IDBDC
Radar surse de finantare

Acest modul centralizeaza toate sursele de informatii
despre oportunitati de finantare pentru cercetare.

Structura este extensibila: pot fi adaugate noi portaluri
fara a modifica restul sistemului.
"""

from datetime import datetime, timedelta


def get_available_sources():
    """
    Returneaza lista tuturor surselor cunoscute.
    """

    sources = [

        {
            "id": "EU_PORTALS",
            "name": "Portaluri finantare UE",
            "description": "Horizon Europe, Interreg, alte programe europene"
        },

        {
            "id": "ROMANIA_PORTALS",
            "name": "Portaluri finantare Romania",
            "description": "UEFISCDI, ministere, programe nationale"
        },

        {
            "id": "SEE_GRANTS",
            "name": "SEE / EEA Grants",
            "description": "Granturi SEE si Norway Grants"
        },

        {
            "id": "PUBLIC_AUTHORITIES",
            "name": "Administratii publice",
            "description": "Programe lansate de autoritati locale sau regionale"
        },

        {
            "id": "INTERNATIONAL_AGENCIES",
            "name": "Agentii internationale",
            "description": "UNESCO, OECD, World Bank, alte programe internationale"
        }

    ]

    return sources


def fetch_calls_from_sources(query="", limit=50):
    """
    Functie generica pentru obtinerea oportunitatilor.

    In aceasta versiune initiala returneaza date demonstrative.
    Conectorii reali catre platforme vor fi adaugati ulterior.
    """

    today = datetime.today()

    results = [

        {
            "source": "EU_PORTALS",
            "title": "Horizon Europe – Research Infrastructure Call",
            "deadline": (today + timedelta(days=60)).strftime("%Y-%m-%d"),
            "country": "EU",
            "url": ""
        },

        {
            "source": "ROMANIA_PORTALS",
            "title": "Competitie UEFISCDI – Proiecte de Cercetare Exploratorie",
            "deadline": (today + timedelta(days=45)).strftime("%Y-%m-%d"),
            "country": "Romania",
            "url": ""
        },

        {
            "source": "SEE_GRANTS",
            "title": "EEA Grants – Collaborative Research Programme",
            "deadline": (today + timedelta(days=75)).strftime("%Y-%m-%d"),
            "country": "International",
            "url": ""
        },

        {
            "source": "PUBLIC_AUTHORITIES",
            "title": "Program Regional Inovare – Administratie Publica",
            "deadline": (today + timedelta(days=90)).strftime("%Y-%m-%d"),
            "country": "Romania",
            "url": ""
        },

        {
            "source": "INTERNATIONAL_AGENCIES",
            "title": "UNESCO – Research and Innovation Programme",
            "deadline": (today + timedelta(days=120)).strftime("%Y-%m-%d"),
            "country": "International",
            "url": ""
        }

    ]

    if query:

        q = query.lower()

        results = [
            r for r in results
            if q in r["title"].lower()
        ]

    return results[:limit]
