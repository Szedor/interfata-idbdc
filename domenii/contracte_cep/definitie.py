# =========================================================
# IDBDC/domenii/contracte_cep/definitie.py
# VERSIUNE: 1.0
# STATUS: NOU - definiție domeniu Contracte CEP
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Toate constantele specifice domeniului Contracte CEP:
#   tabele SQL, etichete vizuale, tab-uri, categorii.
#   Niciun alt fișier din domeniu nu definește aceste valori.
#   O modificare aici nu afectează niciun alt domeniu.
# =========================================================

CATEGORIE   = "Contracte"
TIP_LABEL   = "CEP"
TIP_SEL     = "CEP"

BASE_TABLE  = "base_contracte_cep"
FIN_TABLE   = "com_date_financiare"
ECHIPA_TABLE= "com_echipe_proiect"

TAB_LABELS  = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă"]

SECTIUNI_SALVARE = [BASE_TABLE, FIN_TABLE, ECHIPA_TABLE]
