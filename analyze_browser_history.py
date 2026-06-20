#!/usr/bin/env python3
"""
Script para analizar el historial de navegación de Chrome/Firefox desde enero 2026.
Genera porcentajes por categorías y lista de dominios/servicios usados.
Úsalo localmente para privacidad total. Luego comparte el output para mapear conectores MCP.

Instrucciones:
1. Cierra completamente tu navegador (Chrome recomendado).
2. Copia el archivo History a un lugar seguro o ejecuta con la ruta correcta.
3. Instala dependencias si hace falta: pip install pandas (opcional, para mejor output)
4. Ejecuta: python analyze_browser_history.py --history-path "/ruta/a/History" --start-date "2026-01-01"
   O edita las rutas por defecto abajo.

Rutas típicas:
- Linux: ~/.config/google-chrome/Default/History   o   ~/.mozilla/firefox/*.default-release/places.sqlite
- Windows: C:\\Users\\TUUSUARIO\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History
- Mac: ~/Library/Application Support/Google/Chrome/Default/History

El script hace copia temporal para no bloquear el archivo original.
"""

import sqlite3
import shutil
import os
import argparse
from urllib.parse import urlparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json

# Configuración por defecto - EDITA ESTO si quieres
DEFAULT_HISTORY_PATH = os.path.expanduser("C:\\Users\\jseramn\\Desktop\\www\\what-web-wise\\History")  # Linux Chrome
DEFAULT_START_DATE = "2026-01-01"
OUTPUT_FILE = "navegacion_analisis_2026.json"  # Se guarda en el mismo directorio

def chrome_time_to_datetime(chrome_timestamp):
    """Convierte timestamp de Chrome (microsegundos desde 1601-01-01) a datetime."""
    if chrome_timestamp == 0:
        return None
    epoch_start = datetime(1601, 1, 1)
    return epoch_start + timedelta(microseconds=chrome_timestamp)

def categorize_domain(domain):
    domain = domain.lower()
    
    # Subdominios Google específicos (primero para prioridad)
    if 'drive.google.com' in domain:
        return "Google Drive"
    if 'docs.google.com' in domain or 'sheets.google.com' in domain:
        return "Google Docs / Sheets"
    if 'mail.google.com' in domain or 'gmail.com' in domain:
        return "Gmail"
    if 'calendar.google.com' in domain:
        return "Google Calendar"
    if 'console.cloud.google.com' in domain:
        return "Google Cloud Console"
    if 'myaccount.google.com' in domain or 'accounts.google.com' in domain:
        return "Google Account"
    if 'youtube.com' in domain:
        return "YouTube"
    
    # Google genérico (búsquedas)
    if 'google.com' in domain:
        return "Google Search / General"
    
    # Otros específicos
    if 'grok.com' in domain or 'x.ai' in domain:
        return "Grok / xAI"
    if 'github.com' in domain:
        return "GitHub"
    if 'vercel.com' in domain:
        return "Vercel"
    
    # Resto (mantengo lógica anterior)
    if any(kw in domain for kw in ['upwork', 'computrabajo', 'linkedin']):
        return "Freelance & Trabajo"
    if any(kw in domain for kw in ['rappi', 'mercadolibre']):
        return "Apps & Delivery"
    if any(kw in domain for kw in ['bancolombia', 'nu.com', 'bbva']):
        return "Bancos"
    if any(kw in domain for kw in ['nextjs', 'tailwind', 'aws', 'azure', 'supabase', 'anthropic', 'openai']):
        return "Desarrollo & AI / MCP"
    
    return "Otros / Misc"
    
    # Desarrollo & Coding (TagMe, Next.js, GitHub, Vercel, etc.)
    dev_keywords = [
        'github.com', 'gitlab.com', 'stackoverflow.com', 'stackexchange.com',
        'vercel.com', 'netlify.com', 'nextjs.org', 'tailwindcss.com',
        'react.dev', 'python.org', 'nodejs.org', 'npmjs.com',
        'aws.amazon', 'azure.microsoft', 'cloud.google', 'digitalocean',
        'heroku.com', 'supabase.com', 'firebase.google', 'vercel.app',
        'localhost', '127.0.0.1', 'codepen.io', 'jsfiddle.net',
        'modelcontextprotocol', 'mcp', 'anthropic.com', 'openai.com', 'x.ai',
        'grok.x.ai', 'cursor.com', 'windsurf.ai', 'kilocode.ai', 'cognition.ai'
    ]
    if any(kw in domain for kw in dev_keywords):
        return "Desarrollo & Tech / AI / MCP"
    
    # Google Ecosystem (Gmail, Drive, Calendar, Search, YouTube)
    google_keywords = [
        'gmail.com', 'google.com', 'drive.google.com', 'calendar.google.com',
        'docs.google.com', 'sheets.google.com', 'meet.google.com',
        'youtube.com', 'myaccount.google.com', 'accounts.google.com',
        'console.cloud.google.com', 'admin.google.com'
    ]
    if any(kw in domain for kw in google_keywords):
        return "Google Productivity & Ecosystem"
    
    # Social & Professional
    social_keywords = [
        'x.com', 'twitter.com', 'reddit.com', 'linkedin.com', 'instagram.com',
        'facebook.com', 'tiktok.com', 'threads.net'
    ]
    if any(kw in domain for kw in social_keywords):
        return "Social & Networking Profesional"
    
    # Freelance & Trabajo
    work_keywords = [
        'upwork.com', 'computrabajo.com', 'linkedin.com/jobs', 'indeed.com',
        'fiverr.com', 'freelancer.com', 'getonboard.com', 'bumeran.com.co'
    ]
    if any(kw in domain for kw in work_keywords):
        return "Freelance & Búsqueda de Trabajo"
    
    # Aprendizaje & Educación
    learning_keywords = [
        'platzi.com', 'coursera.org', 'udemy.com', 'edx.org', 'skillshare.com',
        'linkedin.com/learning', 'youtube.com/watch'  # si es educativo
    ]
    if any(kw in domain for kw in learning_keywords):
        return "Aprendizaje & Cursos"
    
    # Finanzas & Bancos (de tus etiquetas)
    finance_keywords = [
        'bancolombia.com', 'nu.com.co', 'bbva.com.co', 'davivienda.com',
        'bancoagrario.com.co', 'mercadopago.com', 'wompi.co', 'dian.gov.co',
        'supremecapitalfunding', 'ictex.gov.co'
    ]
    if any(kw in domain for kw in finance_keywords):
        return "Bancos & Finanzas"
    
    # Apps & Delivery (Rappi, etc.)
    apps_keywords = [
        'rappi.com', 'uber.com', 'ifood.com', 'mercadolibre.com.co',
        'amazon.com', 'mercadolibre.com'
    ]
    if any(kw in domain for kw in apps_keywords):
        return "Apps & Delivery / E-commerce"
    
    # Gobierno & Oficial Colombia
    gov_keywords = [
        'gov.co', 'gob.co', 'mintic.gov.co', 'sena.edu.co', 'icfes.gov.co',
        'cancilleria.gov.co', 'migracioncolombia.gov.co', 'dian.gov.co'
    ]
    if any(kw in domain for kw in gov_keywords):
        return "Gobierno & Trámites Colombia"
    
    # Noticias & Entretenimiento
    news_keywords = [
        'eltiempo.com', 'elespectador.com', 'semana.com', 'bluradio.com.co',
        'netflix.com', 'spotify.com', 'disneyplus.com'
    ]
    if any(kw in domain for kw in news_keywords):
        return "Noticias & Entretenimiento"
    
    # Otros / Misceláneo
    return "Otros / Misc"

def analyze_history(history_path, start_date_str):
    if not os.path.exists(history_path):
        print(f"❌ No se encontró el archivo de historial en: {history_path}")
        print("Edita la ruta en el script o pasa --history-path")
        return None
    
    print(f"📖 Analizando historial desde {start_date_str}...")
    print(f"   Archivo: {history_path}")
    
    # Copia temporal para no bloquear (Chrome bloquea el archivo mientras está abierto)
    temp_db = "/tmp/chrome_history_analyze_temp.db"
    try:
        shutil.copy2(history_path, temp_db)
    except Exception as e:
        print(f"⚠️ Error copiando (puede estar bloqueado): {e}")
        print("Cierra Chrome completamente e intenta de nuevo.")
        return None
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    # Convertir fecha de inicio a timestamp de Chrome
    epoch = datetime(1601, 1, 1)
    start_dt = datetime.fromisoformat(start_date_str)
    chrome_start_ts = int((start_dt - epoch).total_seconds() * 1_000_000)
    
    # Query principal - visitas desde la fecha
    query = """
    SELECT 
        urls.url,
        urls.title,
        visits.visit_time,
        visits.visit_duration
    FROM visits
    JOIN urls ON visits.url = urls.id
    WHERE visits.visit_time >= ?
    ORDER BY visits.visit_time DESC
    LIMIT 50000;  -- Límite de seguridad
    """
    
    cursor.execute(query, (chrome_start_ts,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("⚠️ No se encontraron visitas en el período. ¿Fecha correcta? ¿Navegador usado?")
        return None
    
    print(f"✅ Encontradas {len(rows)} visitas desde {start_date_str}")
    
    domain_counter = Counter()
    category_counter = Counter()
    domain_details = defaultdict(lambda: {"visits": 0, "total_duration_micros": 0, "titles": []})
    total_visits = 0
    total_duration_micros = 0
    
    for url, title, visit_time, duration in rows:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
            if not domain:
                continue
                
            domain_counter[domain] += 1
            total_visits += 1
            
            cat = categorize_domain(domain)
            category_counter[cat] += 1
            
            # Detalles
            domain_details[domain]["visits"] += 1
            if duration:
                domain_details[domain]["total_duration_micros"] += duration
                total_duration_micros += duration
            if title and len(domain_details[domain]["titles"]) < 3:
                domain_details[domain]["titles"].append(title[:80])
                
        except Exception:
            continue
    
    # Calcular porcentajes
    domain_percentages = {d: round((c / total_visits) * 100, 2) for d, c in domain_counter.most_common()}
    category_percentages = {c: round((cnt / total_visits) * 100, 2) for c, cnt in category_counter.most_common()}
    
    # Top dominios
    top_domains = domain_counter.most_common(30)
    
    # Tiempo total aproximado (si hay duración)
    total_hours = total_duration_micros / (1_000_000 * 3600) if total_duration_micros > 0 else 0
    
    # Preparar output estructurado
    analysis = {
        "periodo": f"Desde {start_date_str} hasta hoy",
        "total_visitas_analizadas": total_visits,
        "tiempo_total_horas_aprox": round(total_hours, 2) if total_hours > 0 else "No disponible (duración no registrada en todas las visitas)",
        "categorias_porcentaje": dict(sorted(category_percentages.items(), key=lambda x: -x[1])),
        "top_30_dominios": [
            {
                "dominio": d,
                "visitas": c,
                "porcentaje": domain_percentages.get(d, 0),
                "categoria": categorize_domain(d),
                "ejemplos_titulos": domain_details[d]["titles"][:2]
            }
            for d, c in top_domains
        ],
        "todos_dominios_unicos_ordenados": sorted(domain_counter.items(), key=lambda x: -x[1]),
        "recomendacion_mcp": "Comparte esta lista de dominios top con Vesper para mapear qué servicios tienen servidores MCP disponibles (GitHub, Google Drive, Vercel, etc.) y añadir conectores a tu automatización."
    }
    
    # Guardar JSON para fácil parseo posterior
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    # Imprimir reporte bonito en consola
    print("\n" + "="*70)
    print("🚀 ANÁLISIS DE NAVEGACIÓN - RASE | DESDE ENERO 2026")
    print("="*70)
    print(f"Total visitas analizadas: {total_visits}")
    if total_hours > 0:
        print(f"Tiempo total aproximado en sitios: {total_hours:.1f} horas")
    print("\n📊 PORCENTAJES POR CATEGORÍA:")
    for cat, pct in sorted(category_percentages.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {pct}%")
    
    print("\n🔥 TOP 15 DOMINIOS MÁS VISITADOS:")
    for i, (domain, count) in enumerate(top_domains[:15], 1):
        pct = domain_percentages.get(domain, 0)
        cat = categorize_domain(domain)
        print(f"  {i:2}. {domain:<35} | {count:5} visitas ({pct:5.2f}%) | {cat}")
    
    print(f"\n💾 Reporte completo guardado en: {OUTPUT_FILE}")
    print("   (JSON con todos los datos para compartir fácilmente con Vesper)")
    print("\nPróximo paso: Comparte el contenido de este JSON o los top dominios")
    print("para que mapeemos conectores MCP y los añadamos a tu Galaxia Central.")
    print("="*70 + "\n")
    
    return analysis

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analiza historial de navegación Chrome para patrones y MCP readiness.")
    parser.add_argument("--history-path", default=DEFAULT_HISTORY_PATH, help="Ruta al archivo History de Chrome")
    parser.add_argument("--start-date", default=DEFAULT_START_DATE, help="Fecha inicio en formato YYYY-MM-DD")
    args = parser.parse_args()
    
    analyze_history(args.history_path, args.start_date)