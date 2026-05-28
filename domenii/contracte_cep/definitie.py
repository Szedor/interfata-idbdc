# =========================================================
# domenii/contracte_cep/definitie.py
# v.modul.1.0 - Definiție Contracte CEP
# =========================================================

TIP_LABEL = "CEP"
BASE_TABLE = "base_contracte_cep"
TABS = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă"]

# Mapare coloane pentru Date de bază
FIELDS_BAZA = {
    "cod_identificare": "NR.CONTRACT",
    "data_contract": "📅 DATA CONTRACTULUI",
    "obiectul_contractului": "📝 OBIECTUL CONTRACTULUI",
    "denumire_beneficiar": "🏢 BENEFICIAR",
    "data_inceput": "📅 DATA DE INCEPUT",
    "data_sfarsit": "📅 DATA DE SFARSIT",
    "durata": "⏱️ DURATA (luni)",
    "status_contract_proiect": "🔖 STATUS CONTRACT",
}

# Coloane care nu au emoticon (câmpuri de sistem)
NO_EMOJI_FIELDS = {"cod_identificare", "durata"}

def get_label(field: str) -> str:
    """Returnează eticheta vizuală pentru un câmp."""
    if field in FIELDS_BAZA:
        return FIELDS_BAZA[field]
    return field.replace("_", " ").capitalize()
