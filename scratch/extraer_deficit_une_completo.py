import os
import sys
import json
import time
import re
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

RAW_DIR = "/home/randy/Game_Dev/3d/scratch/raw_cubadebate_pages"
os.makedirs(RAW_DIR, exist_ok=True)

def fetch_page(page, per_page=50, max_retries=3):
    cache_path = os.path.join(RAW_DIR, f"page_{page:03d}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return page, data
        except Exception:
            pass

    url = f"http://www.cubadebate.cu/wp-json/wp/v2/posts?tags=111979&per_page={per_page}&page={page}&_fields=id,date,link,title,content"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                return page, data
        except Exception as e:
            if attempt == max_retries:
                print(f"[!] Error fetching page {page} after {max_retries} attempts: {e}", file=sys.stderr)
                return page, []
            time.sleep(2 * attempt)
    return page, []

def clean_html(html_str):
    soup = BeautifulSoup(html_str, "html.parser")
    return soup.get_text("\n")

def parse_num(s):
    if not s:
        return None
    s = str(s).strip().replace(" ", "").replace("\xa0", "")
    # Handle thousands separator (Cuban/Spanish style 2.130 or 2 130)
    if "." in s and len(s.split(".")[-1]) == 3:
        s = s.replace(".", "")
    elif "," in s and len(s.split(",")[-1]) == 3:
        s = s.replace(",", "")
    try:
        val = float(s.replace(",", "."))
        return val
    except Exception:
        return None

def parse_une_report(p):
    pid = p.get("id")
    date_str = p.get("date", "")
    title = p.get("title", {}).get("rendered", "") if isinstance(p.get("title"), dict) else str(p.get("title", ""))
    url = p.get("link", "")
    html_content = p.get("content", {}).get("rendered", "") if isinstance(p.get("content"), dict) else str(p.get("content", ""))
    
    raw_text = clean_html(html_content)
    text = re.sub(r"[ \t]+", " ", raw_text)
    
    # Filter: is this an electrical situation / daily note report?
    title_lower = title.lower()
    text_lower = text.lower()
    
    is_daily = any(k in title_lower for k in [
        "pronostica", "afectación", "afectacion", "pico", "déficit", "deficit", 
        "sen", "nota informativa", "situación del sen", "situacion del sen", 
        "servicio eléctrico", "servicio electrico"
    ]) or any(k in text_lower for k in [
        "déficit de capacidad", "deficit de capacidad", "máxima afectación", 
        "maxima afectacion", "disponibilidad del sen", "horario de máxima demanda"
    ])
    
    if not is_daily:
        return None
        
    # Exclude obvious non-reports like general political speeches or accidents unless they contain parts
    if any(k in title_lower for k in ["sancionan a", "sabotaje contra", "robos de cables", "visita termoeléctrica"]):
        if not ("máxima afectación" in text_lower or "déficit de capacidad" in text_lower):
            return None

    # Title forecast
    m_title_mw = re.search(r"(\d[\d\s\.,]*)\s*MW", title, re.IGNORECASE)
    afect_title = parse_num(m_title_mw.group(1)) if m_title_mw else None
    
    # Check if explicitly 0 deficit announced
    is_zero = bool(re.search(r"no\s+se\s+(?:pronostica|prev[eé]|estima)\s+afectaci[oó]n", text, re.IGNORECASE))
    
    # Ayer (previous day actuals)
    m_ayer_mw = re.search(r"m[aá]xima\s+afectaci[oó]n(?:[^\.\n]*?fue\s+de\s+|[^\.\n]*?de\s+)?(\d[\d\s\.,]*)\s*MW", text, re.IGNORECASE)
    max_ayer_mw = parse_num(m_ayer_mw.group(1)) if m_ayer_mw else None
    
    m_ayer_hora = re.search(r"m[aá]xima\s+afectaci[oó]n[^\.\n]*?a\s+las\s+(\d{1,2}[:\.]\d{2})\s*horas", text, re.IGNORECASE)
    hora_ayer = m_ayer_hora.group(1).replace(".", ":") if m_ayer_hora else None
    
    # 24 horas continuous blackout
    ayer_24h = bool(re.search(r"las\s+24\s+horas", text, re.IGNORECASE))
    
    # Morning status (06:00 / 07:00)
    m_manana = re.search(
        r"disponibilidad\s+del\s+SEN\s+a\s+las\s+\d{1,2}[:\.]\d{2}\s*horas\s+es\s+de\s+(\d[\d\s\.,]*)\s*MW[^\.\n]*?demanda\s+(?:es\s+de\s+)?(\d[\d\s\.,]*)\s*MW(?:[^\.\n]*?con\s+(\d[\d\s\.,]*)\s*MW\s+afectados)?", 
        text, re.IGNORECASE
    )
    disp_manana = parse_num(m_manana.group(1)) if m_manana else None
    dem_manana = parse_num(m_manana.group(2)) if m_manana else None
    afect_manana = parse_num(m_manana.group(3)) if m_manana and m_manana.group(3) else None
    
    # Midday forecast
    m_medio = re.search(r"(?:horario\s+de\s+la\s+media|horario\s+del\s+mediod[ií]a|al\s+mediod[ií]a)[^\.\n]*?afectaci[oó]n\s+(?:de\s+)?(\d[\d\s\.,]*)\s*MW", text, re.IGNORECASE)
    afect_mediodia = parse_num(m_medio.group(1)) if m_medio else None
    
    # Solar photovoltaic contribution
    m_sol_mwh = re.search(r"parques\s+solares[^\.\n]*?fue\s+de\s+(\d[\d\s\.,]*)\s*MWh", text, re.IGNORECASE)
    solar_mwh = parse_num(m_sol_mwh.group(1)) if m_sol_mwh else None
    m_sol_mw = re.search(r"(\d[\d\s\.,]*)\s*MW\s+(?:como\s+)?m[aá]xima\s+potencia", text, re.IGNORECASE)
    solar_mw = parse_num(m_sol_mw.group(1)) if m_sol_mw else None
    
    # Thermal limits
    m_lim = re.search(r"limitaciones\s+en\s+la\s+generaci[oó]n\s+t[eé]rmica\s+(?:son\s+de\s+|alcanzan\s+los\s+)?(\d[\d\s\.,]*)\s*MW", text, re.IGNORECASE)
    lim_termica = parse_num(m_lim.group(1)) if m_lim else None
    
    # Fuel shortage
    m_comb = re.search(r"(?:falta\s+de\s+combustible|fuera\s+por\s+combustible)[^\.\n]*?(\d[\d\s\.,]*)\s*MW", text, re.IGNORECASE)
    fuera_comb = parse_num(m_comb.group(1)) if m_comb else None
    
    # Units in maintenance / breakdown counts
    unidades_averia = len(re.findall(r"unidad\s+\d+.*?CTE|unidad.*?CTE", text[text.find("avería"):text.find("mantenimiento")] if "avería" in text and "mantenimiento" in text else ""))
    
    # Peak forecast section
    disp_pico, dem_pico, def_pico, afect_pico = None, None, None, None
    if is_zero:
        def_pico, afect_pico = 0.0, 0.0
    else:
        paragraphs = text.split("\n")
        pico_text = ""
        for p_line in reversed(paragraphs):
            if any(k in p_line.lower() for k in ["máxima demanda", "maxima demanda", "horario pico", "para el pico"]):
                pico_text = p_line + " " + pico_text
                if len(pico_text) > 350:
                    break
        if not pico_text:
            pico_text = text[-900:]
            
        m_dp = re.search(r"disponibilidad\s+(?:de\s+)?(\d[\d\s\.,]*)\s*MW", pico_text, re.IGNORECASE)
        m_dmp = re.search(r"demanda\s+(?:m[aá]xima\s+)?(?:de\s+)?(\d[\d\s\.,]*)\s*MW", pico_text, re.IGNORECASE)
        m_dfp = re.search(r"d[eé]ficit\s+(?:de\s+)?(\d[\d\s\.,]*)\s*MW", pico_text, re.IGNORECASE)
        m_afp = re.search(r"afectaci[oó]n\s+(?:de\s+)?(\d[\d\s\.,]*)\s*MW", pico_text, re.IGNORECASE)
        
        disp_pico = parse_num(m_dp.group(1)) if m_dp else None
        dem_pico = parse_num(m_dmp.group(1)) if m_dmp else None
        def_pico = parse_num(m_dfp.group(1)) if m_dfp else None
        afect_pico = parse_num(m_afp.group(1)) if m_afp else afect_title
        
        # Cross-calculation if deficit omitted
        if def_pico is None and dem_pico is not None and disp_pico is not None:
            def_pico = max(0.0, dem_pico - disp_pico)
            
        if afect_pico is None:
            afect_pico = afect_title or def_pico

    # Basic plausibility: discard if no numerical electrical data extracted at all
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

def main():
    total_pages = 41
    print(f"[*] Starting extraction across {total_pages} pages...")
    
    all_posts = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_page, p): p for p in range(1, total_pages + 1)}
        for future in as_completed(futures):
            p_num, data = future.result()
            print(f"  [+] Page {p_num:02d}/{total_pages} loaded ({len(data)} posts)")
            all_posts.extend(data)
            
    print(f"[*] Total raw posts fetched: {len(all_posts)}")
    
    parsed_records = []
    for p in all_posts:
        rec = parse_une_report(p)
        if rec:
            parsed_records.append(rec)
            
    print(f"[*] Total valid UNE daily reports parsed: {len(parsed_records)}")
    
    df = pd.DataFrame(parsed_records)
    # Sort chronologically
    df["fecha_dt"] = pd.to_datetime(df["fecha"])
    df = df.sort_values(by=["fecha_dt", "hora_publicacion"]).reset_index(drop=True)
    
    # Deduplicate: if multiple posts on same date, keep the one with most complete data (highest deficit_pico_mw or non-nulls)
    df["non_null_count"] = df.notnull().sum(axis=1)
    df = df.sort_values(by=["fecha", "non_null_count"], ascending=[True, False])
    df = df.drop_duplicates(subset=["fecha"], keep="first").reset_index(drop=True)
    df = df.drop(columns=["fecha_dt", "non_null_count"])
    
    out_csv = "/home/randy/Game_Dev/3d/cuba_energia_deficit_diario_une_2021_2026.csv"
    out_json = "/home/randy/Game_Dev/3d/cuba_energia_deficit_diario_une_2021_2026.json"
    
    df.to_csv(out_csv, index=False, encoding="utf-8")
    df.to_json(out_json, orient="records", date_format="iso", indent=2, force_ascii=False)
    
    print(f"\n[SUCCESS] Datasets exported successfully:")
    print(f"  - CSV:  {out_csv} ({len(df)} records)")
    print(f"  - JSON: {out_json}")
    print(f"  - Date Range: {df['fecha'].min()} to {df['fecha'].max()}")
    print("\nSummary Statistics:")
    print(df[["afectacion_pico_mw", "deficit_pico_mw", "max_afectacion_ayer_mw", "disponibilidad_pico_mw", "demanda_pico_mw"]].describe())

if __name__ == "__main__":
    main()
