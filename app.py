# Linia 6: Definiția funcției
def connect_db():
    # Linia 7: Acum este indentată corect
    return psycopg2.connect(
        host="host_ul_tau",
        database="nume_baza_date",
        user="utilizator",
        password="parola"
    )
