"""
Lookup de nombres de auto a partir de CarOrdinal, usando la base de
datos de la comunidad (BD/Forza_Motorsport_cars.csv).

La columna clave es 'Ordinal', que corresponde 1:1 con el campo
CarOrdinal de la telemetría UDP.
"""

import pandas as pd
import os

_CSV_PATH = os.path.join(os.path.dirname(__file__), "BD", "Forza_Motorsport_cars.csv")
_car_db = None  # cache: se carga una sola vez, no en cada consulta


def _load_db():
    global _car_db
    if _car_db is None:
        df = pd.read_csv(_CSV_PATH)
        df["Ordinal"] = pd.to_numeric(df["Ordinal"], errors="coerce")
        _car_db = df
    return _car_db


def get_car_name(car_ordinal):
    """
    Regresa un nombre legible para el auto dado su CarOrdinal.
    Si no se encuentra, regresa None (el llamador decide el fallback).
    """
    try:
        df = _load_db()
        match = df[df["Ordinal"] == car_ordinal]
        if match.empty:
            return None

        row = match.iloc[0]
        nickname = row.get("Nickname")

        # Preferimos el Nickname (más corto, ej. "Audi RS 3 '20").
        # Si no existe, armamos algo a partir de Year + Makes + Models.
        if pd.notna(nickname) and str(nickname).strip():
            return str(nickname)

        year = row.get("Year")
        make = row.get("Makes: 96")
        model = row.get("Models: 681")
        parts = [str(int(year)) if pd.notna(year) else "", str(make) if pd.notna(make) else "",
                  str(model) if pd.notna(model) else ""]
        name = " ".join(p for p in parts if p)
        return name if name else None

    except FileNotFoundError:
        return None
    except Exception:
        return None


def get_car_aspiration(car_ordinal):
    """
    Regresa el tipo de aspiración legible (ej. 'Turbo', 'Naturally Aspirated')
    para el auto dado su CarOrdinal. Regresa None si no se encuentra o
    el dato está vacío en la base -- el llamador decide el fallback.
    """
    aspiration_map = {
        "T": "Turbo",
        "TT": "TwinTurbo",
        "NA": "NatAsp",
        "S": "Supercharged",
        "PDS": "PDS",
        "E": "Electric",
    }
    try:
        df = _load_db()
        match = df[df["Ordinal"] == car_ordinal]
        if match.empty:
            return None
        value = match.iloc[0].get("Aspiration")
        if pd.isna(value):
            return None
        value = str(value).strip()
        return aspiration_map.get(value, value if value else None)
    except Exception:
        return None


if __name__ == "__main__":
    # Prueba rápida
    print(get_car_name(3454))   # esperado: Audi RS 3 '20
    print(get_car_name(999999))  # esperado: None
    print(get_car_aspiration(3454))  # esperado: Turbo
