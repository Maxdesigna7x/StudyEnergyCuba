import os
import json
import re
import pandas as pd
from bs4 import BeautifulSoup

RAW_DIR = "/home/randy/Game_Dev/3d/scratch/raw_cubadebate_pages"

def clean_html(html_str):
    soup = BeautifulSoup(html_str, "html.parser")
    return soup.get_text("\n")

def parse_num(s):
    if s is None:
        return None
    s = str(s).strip().replace(" ", "").replace("\xa0", "")
    s = s.rstrip(".,;:")
    if not s:
        return None
    if "." in s and len(s.split(".")[-1]) == 3:
        s = s.replace(".", "")
    elif "," in s and len(s.split(",")[-1]) == 3:
        s = s.replace(",", "")
    try:
        return float(s.replace(",", "."))
    except Exception:
        return None

def parse_post(p):
    pid = p.get("id")
    date_str = p.get("date", "")
    title = p.get("title", {}).get("rendered", "") if isinstance(p.get("title"), dict) else str(p.get("title", ""))
    url = p.get("link", "")
    html_content = p.get("content", {}).get("rendered", "") if isinstance(p.get("content"), dict) else str(p.get("content", ""))
    
    raw_text = clean_html(html_content)
    norm_text = re.sub(r"\s+", " ", raw_text)
    
    title_lower = title.lower()
    text_lower = norm_text.lower()
    
    # 1. Filter: is this an energy daily report?
    is_daily = any(k in title_lower for k in [
        "pronostica", "afectación", "afectacion", "pico", "déficit", "deficit", 
        "sen", "nota informativa", "situación del sen", "situacion del sen", 
        "servicio eléctrico", "servicio electrico", "termoeléctrica", "termoelectrica"
    ]) or any(k in text_lower for k in [
        "déficit de capacidad", "deficit de capacidad", "máxima afectación", 
        "maxima afectacion", "disponibilidad del sen", "horario de máxima demanda",
        "horario de maxima demanda", "hora pico"
    ])
    
    if not is_daily:
        return None

    if any(k in title_lower for k in ["sancionan a", "sabotaje contra", "robos de cables", "visita termoeléctrica", "asamblea nacional"]):
        if not ("máxima afectación" in text_lower or "déficit de capacidad" in text_lower or "mw" in text_lower):
            return None

    # 2. Title forecast (only if it relates to afectacion or deficit, not generation/count)
    afect_title = None
    if not any(k in title_lower for k in ["contar con", "aumenta generación", "sincroniza", "eleva su generación"]):
        m_title_mw = re.search(r"(\d[\d\s\.,]*?\d)\s*MW", title, re.IGNORECASE)
        afect_title = parse_num(m_title_mw.group(1)) if m_title_mw else None
    
    # 3. Explicit zero checks
    zero_forecast = bool(re.search(
        r"(?:no\s+se\s+(?:pronostica|prev[eé]|estima)\s+afectaci[oó]n|sin\s+afectaci[oó]n\s+por\s+d[eé]ficit|no\s+habr[aá]\s+afectaci[oó]n|todo\s+el\s+SEN\s+con\s+servicio)", 
        norm_text, re.IGNORECASE
    ))
    
    zero_yesterday = bool(re.search(
        r"(?:ayer\s+no\s+hubo\s+afectaci[oó]n|d[ií]a\s+de\s+ayer\s+no\s+se\s+afect[oó]\s+el\s+servicio|no\s+se\s+afect[oó]\s+el\s+servicio\s+por\s+d[eé]ficit\s+en\s+el\s+d[ií]a\s+de\s+ayer)", 
        norm_text, re.IGNORECASE
    ))
    
    # 4. Ayer
    max_ayer_mw = 0.0 if zero_yesterday else None
    if max_ayer_mw is None:
        m_ayer_mw = re.search(
            r"m[aá]xima\s+afectaci[oó]n[^\.\n]*?(?:fue\s+de|alcanz[oó]|de)\s+(\d[\d\s\.,]*?\d)\s*MW", 
            norm_text, re.IGNORECASE
        )
        if not m_ayer_mw:
            m_ayer_mw = re.search(r"afectaci[oó]n\s+en\s+el\s+horario\s+pico\s+de\s+ayer[^\.\n]*?(?:fue\s+de|alcanz[oó]|de)\s+(\d[\d\s\.,]*?\d)\s*MW", norm_text, re.IGNORECASE)
        max_ayer_mw = parse_num(m_ayer_mw.group(1)) if m_ayer_mw else None
    
    m_ayer_hora = re.search(r"m[aá]xima\s+afectaci[oó]n[^\.\n]*?a\s+las\s+(\d{1,2}[:\.]\d{2})\s*(?:horas|h|p\.m\.|a\.m\.)", norm_text, re.IGNORECASE)
    if not m_ayer_hora:
        m_ayer_hora = re.search(r"(\d{1,2}[:\.]\d{2})\s*(?:horas|h|p\.m\.|a\.m\.)[^\.\n]*?coincidiendo", norm_text, re.IGNORECASE)
    hora_ayer = m_ayer_hora.group(1).replace(".", ":") if m_ayer_hora else None
    
    ayer_24h = bool(re.search(r"(?:las\s+24\s+horas|durante\s+todo\s+el\s+d[ií]a)", norm_text, re.IGNORECASE))
    
    # 5. Morning
    m_manana = re.search(
        r"disponibilidad\s+(?:del\s+SEN\s+)?a\s+las\s+\d{1,2}(?:[:\.]\d{2})?\s*(?:horas|a\.m\.)\s+es\s+de\s+(\d[\d\s\.,]*?\d)\s*MW[^\.\n]*?demanda\s+(?:es\s+de\s+)?(\d[\d\s\.,]*?\d)\s*MW(?:[^\.\n]*?con\s+(\d[\d\s\.,]*?\d)\s*MW\s+afectados)?", 
        norm_text, re.IGNORECASE
    )
    disp_manana = parse_num(m_manana.group(1)) if m_manana else None
    dem_manana = parse_num(m_manana.group(2)) if m_manana else None
    afect_manana = parse_num(m_manana.group(3)) if m_manana and m_manana.group(3) else None
    
    # 6. Midday
    m_medio = re.search(
        r"(?:horario\s+de\s+la\s+media|horario\s+del\s+mediod[ií]a|al\s+mediod[ií]a|horario\s+diurno)[^\.\n]*?afectaci[oó]n\s+(?:de\s+)?(\d[\d\s\.,]*?\d)\s*MW", 
        norm_text, re.IGNORECASE
    )
    afect_mediodia = parse_num(m_medio.group(1)) if m_medio else None
    if afect_mediodia is None and bool(re.search(r"no\s+se\s+estiman?\s+afectaciones?\s+en\s+el\s+horario\s+(?:diurno|del\s+d[ií]a)", norm_text, re.IGNORECASE)):
        afect_mediodia = 0.0
    
    # 7. Solar
    m_sol_mwh = re.search(r"parques\s+solares[^\.\n]*?fue\s+de\s+(\d[\d\s\.,]*?\d)\s*MWh", norm_text, re.IGNORECASE)
    solar_mwh = parse_num(m_sol_mwh.group(1)) if m_sol_mwh else None
    m_sol_mw = re.search(r"(\d[\d\s\.,]*?\d)\s*MW\s+(?:como\s+)?m[aá]xima\s+potencia", norm_text, re.IGNORECASE)
    solar_mw = parse_num(m_sol_mw.group(1)) if m_sol_mw else None
    
    # 8. Thermal & Fuel
    m_lim = re.search(r"limitaciones\s+en\s+la\s+generaci[oó]n\s+t[eé]rmica\s+(?:son\s+de\s+|alcanzan\s+los\s+)?(\d[\d\s\.,]*?\d)\s*MW", norm_text, re.IGNORECASE)
    lim_termica = parse_num(m_lim.group(1)) if m_lim else None
    
    m_comb = re.search(r"(?:falta\s+de\s+combustible|fuera\s+por\s+combustible)[^\.\n]*?(\d[\d\s\.,]*?\d)\s*MW", norm_text, re.IGNORECASE)
    fuera_comb = parse_num(m_comb.group(1)) if m_comb else None
    
    # 9. Peak Forecast
    disp_pico, dem_pico, def_pico, afect_pico = None, None, None, None
    if zero_forecast:
        def_pico = 0.0
        afect_pico = 0.0
    else:
        m_pico_full = re.search(
            r"disponibilidad\s+(?:de\s+)?(\d[\d\s\.,]*?\d)\s*MW.*?demanda\s+(?:m[aá]xima\s+)?(?:de\s+)?(\d[\d\s\.,]*?\d)\s*MW.*?d[eé]ficit\s+(?:de\s+)?(\d[\d\s\.,]*?\d)\s*MW(?:.*?afectaci[oó]n\s+(?:de\s+)?(\d[\d\s\.,]*?\d)\s*MW)?",
            norm_text, re.IGNORECASE
        )
        if m_pico_full:
            disp_pico = parse_num(m_pico_full.group(1))
            dem_pico = parse_num(m_pico_full.group(2))
            def_pico = parse_num(m_pico_full.group(3))
            if m_pico_full.group(4):
                afect_pico = parse_num(m_pico_full.group(4))
        else:
            m_dp = re.search(r"(?:hora\s+pico|horario\s+pico|máxima\s+demanda)[^\.\n]*?disponibilidad\s+(?:de\s+)?(\d[\d\s\.,]*?\d)\s*MW", norm_text, re.IGNORECASE)
            m_dmp = re.search(r"(?:hora\s+pico|horario\s+pico|máxima\s+demanda)[^\.\n]*?demanda\s+(?:m[aá]xima\s+)?(?:de\s+)?(\d[\d\s\.,]*?\d)\s*MW", norm_text, re.IGNORECASE)
            m_dfp = re.search(r"(?:hora\s+pico|horario\s+pico|máxima\s+demanda)[^\.\n]*?d[eé]ficit\s+(?:de\s+)?(\d[\d\s\.,]*?\d)\s*MW", norm_text, re.IGNORECASE)
            m_afp = re.search(r"(?:hora\s+pico|horario\s+pico|máxima\s+demanda)[^\.\n]*?afectaci[oó]n\s+(?:de\s+)?(\d[\d\s\.,]*?\d)\s*MW", norm_text, re.IGNORECASE)
            
            disp_pico = parse_num(m_dp.group(1)) if m_dp else None
            dem_pico = parse_num(m_dmp.group(1)) if m_dmp else None
            def_pico = parse_num(m_dfp.group(1)) if m_dfp else None
            afect_pico = parse_num(m_afp.group(1)) if m_afp else None
            
        if def_pico is None and dem_pico is not None and disp_pico is not None:
            def_pico = max(0.0, dem_pico - disp_pico)
            
        if disp_pico is not None and dem_pico is not None and disp_pico >= dem_pico:
            def_pico = 0.0
            afect_pico = 0.0
            
        if afect_pico is None:
            afect_pico = afect_title or def_pico
            
        # If daytime affectation was mistakenly picked up, prefer afect_title
        if afect_title is not None and def_pico is not None and afect_pico is not None:
            if abs(afect_title - def_pico) < abs(afect_pico - def_pico):
                afect_pico = afect_title
            
        if def_pico is None:
            def_pico = afect_pico or afect_title

    # Sanity checks on affectation vs demand
    if afect_pico is not None and dem_pico is not None and dem_pico > 0:
        if afect_pico > dem_pico:
            afect_pico = max(0.0, dem_pico - (disp_pico if disp_pico is not None else 0.0))

    if all(v is None for v in [max_ayer_mw, afect_pico, def_pico, disp_pico, dem_pico, disp_manana, dem_manana]):
        return None

    return {
        "id": pid,
        "fecha": date_str[:10],
        "hora_publicacion": date_str[11:19] if len(date_str) >= 19 else "",
        "titulo": title.strip(),
        "afectacion_pico_mw": afect_pico,
        "deficit_pico_mw": def_pico,
        "disponibilidad_pico_mw": disp_pico,
        "demanda_pico_mw": dem_pico,
        "max_afectacion_ayer_mw": max_ayer_mw,
        "hora_max_ayer": hora_ayer,
        "afectacion_ayer_24h": ayer_24h,
        "afectacion_mediodia_mw": afect_mediodia,
        "disponibilidad_manana_mw": disp_manana,
        "demanda_manana_mw": dem_manana,
        "afectacion_manana_mw": afect_manana,
        "limitacion_termica_mw": lim_termica,
        "fuera_combustible_mw": fuera_comb,
        "solar_fotovoltaica_mwh": solar_mwh,
        "solar_potencia_max_mw": solar_mw,
        "url": url
    }

def process_all():
    files = sorted([f for f in os.listdir(RAW_DIR) if f.endswith(".json")])
    all_posts = []
    for f in files:
        with open(os.path.join(RAW_DIR, f), "r", encoding="utf-8") as fp:
            data = json.load(fp)
            all_posts.extend(data)
            
    parsed = []
    for p in all_posts:
        rec = parse_post(p)
        if rec:
            parsed.append(rec)
            
    df = pd.DataFrame(parsed)
    df["fecha_dt"] = pd.to_datetime(df["fecha"])
    df = df.sort_values(by=["fecha_dt", "hora_publicacion"]).reset_index(drop=True)
    
    # Deduplicate
    df["non_null_count"] = df.notnull().sum(axis=1)
    df = df.sort_values(by=["fecha", "non_null_count"], ascending=[True, False])
    df = df.drop_duplicates(subset=["fecha"], keep="first").reset_index(drop=True)
    df = df.drop(columns=["fecha_dt", "non_null_count"])
    df = df.sort_values(by="fecha").reset_index(drop=True)
    
    out_csv = "/home/randy/Game_Dev/3d/cuba_energia_deficit_diario_une_2021_2026.csv"
    out_json = "/home/randy/Game_Dev/3d/cuba_energia_deficit_diario_une_2021_2026.json"
    
    df.to_csv(out_csv, index=False, encoding="utf-8")
    df.to_json(out_json, orient="records", date_format="iso", indent=2, force_ascii=False)
    
    print("==========================================")
    print("DATASET EXPORT SUMMARY (V3 Clean)")
    print("==========================================")
    print(f"Total Unique Days: {len(df)}")
    print(f"Date Range:        {df['fecha'].min()}  -->  {df['fecha'].max()}")
    print("\nTop 5 Max Peak Deficits:")
    print(df.sort_values(by='afectacion_pico_mw', ascending=False)[['fecha', 'afectacion_pico_mw', 'deficit_pico_mw', 'disponibilidad_pico_mw', 'demanda_pico_mw']].head(5))

if __name__ == "__main__":
    process_all()
