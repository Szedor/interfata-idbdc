import os
import re
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(".").resolve()

# ce căutăm în cod ca să deducem stack-ul
IMPORT_HINTS = {
    "streamlit": ["streamlit"],
    "supabase": ["supabase", "supabase_py", "supabase.client"],
    "sqlalchemy": ["sqlalchemy"],
    "psycopg2": ["psycopg2"],
    "asyncpg": ["asyncpg"],
    "pg8000": ["pg8000"],
    "dotenv": ["dotenv", "python_dotenv"],
}

# cuvinte cheie pentru a găsi fișiere tip "administrare"
ADMIN_HINTS = ["administrare", "admin", "manage", "management", "operator", "editare", "fisa", "validare"]

# pattern-uri pentru tabele
TABLE_PATTERNS = [
    re.compile(r"\b(base_[a-zA-Z0-9_]+)\b"),
    re.compile(r"\b(com_[a-zA-Z0-9_]+)\b"),
]

def read_text_safe(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def list_tree(max_files=2000):
    py_files = []
    for p in ROOT.rglob("*.py"):
        # excludem venv, cache etc
        if any(part in ("venv", ".venv", "__pycache__", ".git") for part in p.parts):
            continue
        py_files.append(p)
        if len(py_files) >= max_files:
            break
    return py_files

def find_requirements():
    candidates = ["requirements.txt", "pyproject.toml", "Pipfile"]
    found = []
    for c in candidates:
        p = ROOT / c
        if p.exists():
            found.append(p)
    return found

def detect_imports(py_files):
    counts = Counter()
    files_by_hint = defaultdict(list)

    for p in py_files:
        txt = read_text_safe(p)
        # simplu: căutăm "import X" / "from X import"
        for key, hints in IMPORT_HINTS.items():
            for h in hints:
                if re.search(rf"(^|\n)\s*(import|from)\s+{re.escape(h)}\b", txt):
                    counts[key] += 1
                    files_by_hint[key].append(str(p))
                    break

    return counts, files_by_hint

def find_admin_files(py_files):
    scored = []
    for p in py_files:
        txt = read_text_safe(p).lower()
        score = 0
        name = p.name.lower()
        for h in ADMIN_HINTS:
            if h in name:
                score += 3
            if h in txt:
                score += 1
        if score > 0:
            scored.append((score, str(p)))
    scored.sort(reverse=True)
    return scored[:15]

def find_tables(py_files):
    base_tables = Counter()
    com_tables = Counter()
    table_hits = defaultdict(list)

    for p in py_files:
        txt = read_text_safe(p)
        for pat in TABLE_PATTERNS:
            for m in pat.finditer(txt):
                t = m.group(1)
                if t.startswith("base_"):
                    base_tables[t] += 1
                elif t.startswith("com_"):
                    com_tables[t] += 1
                table_hits[t].append(str(p))

    return base_tables, com_tables, table_hits

def detect_streamlit_structure():
    pages_dir = ROOT / "pages"
    has_pages = pages_dir.exists() and pages_dir.is_dir()
    main_py = (ROOT / "app.py").exists() or (ROOT / "main.py").exists() or (ROOT / "streamlit_app.py").exists()
    return has_pages, main_py

def main():
    print("=== Inspectare proiect (fără DB) ===")
    print(f"Folder proiect: {ROOT}")

    py_files = list_tree()
    print(f"Fișiere .py găsite: {len(py_files)}")

    has_pages, has_main = detect_streamlit_structure()
    print("\n--- Structură Streamlit ---")
    print(f"Folder pages/: {'DA' if has_pages else 'NU'}")
    print(f"Fișier principal (app.py/main.py/streamlit_app.py): {'DA' if has_main else 'NU'}")

    reqs = find_requirements()
    print("\n--- Fișiere dependințe ---")
    if reqs:
        for r in reqs:
            print(f"- {r}")
    else:
        print("Nu am găsit requirements.txt / pyproject.toml / Pipfile")

    counts, files_by_hint = detect_imports(py_files)
    print("\n--- Indicii biblioteci (din importuri) ---")
    for k, v in counts.most_common():
        print(f"{k}: {v} fișiere")

    if counts:
        print("\nFișiere unde apar importurile (top):")
        for k in ("streamlit", "supabase", "sqlalchemy", "psycopg2"):
            if files_by_hint.get(k):
                print(f"\n[{k}]")
                for f in files_by_hint[k][:10]:
                    print(f" - {f}")

    admin_files = find_admin_files(py_files)
    print("\n--- Fișiere candidate pentru 'Administrare' ---")
    if admin_files:
        for score, f in admin_files:
            print(f"score={score:>2}  {f}")
    else:
        print("Nu am găsit nimic clar. (Poate e într-un fișier cu alt nume.)")

    base_tables, com_tables, table_hits = find_tables(py_files)
    print("\n--- Tabele detectate în cod ---")
    print("\nbase_* (top):")
    for t, n in base_tables.most_common(20):
        print(f" - {t}  (apare de {n} ori)")

    print("\ncom_* (top):")
    for t, n in com_tables.most_common(20):
        print(f" - {t}  (apare de {n} ori)")

    print("\n--- Unde apare 'cod_identificare' ---")
    cod_files = []
    for p in py_files:
        txt = read_text_safe(p)
        if "cod_identificare" in txt:
            cod_files.append(str(p))
    for f in cod_files[:30]:
        print(f" - {f}")
    if not cod_files:
        print("Nu am găsit 'cod_identificare' în cod (poate e doar în DB).")

    print("\n=== Gata. Copiezi output-ul și mi-l trimiți aici. ===")

if __name__ == "__main__":
    main()
