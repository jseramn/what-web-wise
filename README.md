# 🔍 What Web Wise

**Analizador de historial de navegación + Visualizador Web**

Herramienta local para analizar tu historial de Chrome, obtener porcentajes por categorías, top dominios y conocer qué has estado viendo en la web… para reflexionar un poco.

![Banner](https://raw.githubusercontent.com/jseramn/what-web-wise/assets/banner.png)

## ✨ Características

- Análisis preciso de visitas y tiempo (desde 1 de enero 2026)
- Clasificación granular por categorías (Desarrollo, Google Services, Freelance, Bancos, etc.)
- Visualizador web interactivo con gráficos (Chart.js)
- 100% local y privado (nada sale de tu máquina)
- Preparado para identificar servicios con soporte MCP

## 📁 Estructura del proyecto

```
what-web-wise/
├── analyze_browser_history.py     # Script principal de análisis
├── navegacion_visualizer.html     # Visualizador web interactivo
├── navegacion_analisis_2026.json  # Output generado (no commitear)
├── History                        # Copia de tu archivo de Chrome (no commitear)
├── .gitignore
├── README.md
└── banner.png
```

## 🚀 Cómo usar

### 1. Preparación
- Cierra completamente Chrome.
- Copia tu archivo `History` a esta carpeta (ruta típica en Windows:  
  `C:\Users\TuUsuario\AppData\Local\Google\Chrome\User Data\Default\History`).

### 2. Ejecuta el análisis
```powershell
python analyze_browser_history.py --history-path "History"
```

### 3. Visualiza los resultados
Abre `navegacion_visualizer.html` en tu navegador. Se carga automáticamente el JSON generado.

## 📊 Qué obtienes

- Porcentajes por categoría (gráfico de barras)
- Top 30 dominios con visitas y %
- Recomendaciones para añadir conectores MCP (GitHub, Google Drive, Vercel, Grok, etc.)

## 🛠 Tecnologías

- Python + sqlite3
- HTML + CSS + JavaScript + Chart.js

## 📝 Notas

- El archivo `History` y el JSON generado están en `.gitignore` por privacidad.
- Para actualizar el análisis: vuelve a correr el script.

---

**Creado por @jseramn**  
Hecho con ❤️ para mapear patrones y potenciar automatización.