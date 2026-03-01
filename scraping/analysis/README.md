# 📊 Análisis de Datos - Rosario Central

Scripts de análisis para evaluar la calidad y cobertura de los datos scrapeados.

## 📁 Archivos

| Script | Descripción |
|--------|-------------|
| `run_all_analysis.py` | **Script principal** - Ejecuta todos los análisis |
| `analyze_jugadores_clubes.py` | Analiza clubes por país (jugadores) |
| `analyze_tecnicos_clubes.py` | Analiza clubes por país (técnicos) |
| `analyze_goles_detallados.py` | Analiza temporadas con goles detallados |
| `analyze_tecnicos_jugadores_temporadas.py` | Analiza temporadas con datos técnicos-jugadores |
| `analyze_posiciones.py` | **NUEVO** - Analiza todas las posiciones de Transfermarkt |

## 🚀 Uso

### Ejecutar todos los análisis (Recomendado)

```bash
cd /Users/francescocamussoni/Documents/itti/carc/scraping/analysis
python3 run_all_analysis.py
```

Este script:
- Ejecuta los 4 análisis en secuencia
- Genera un resumen consolidado
- Guarda un archivo `analysis_summary.txt` con los resultados clave

### Ejecutar análisis individuales

```bash
# Análisis de jugadores por país
python3 analyze_jugadores_clubes.py

# Análisis de técnicos por país
python3 analyze_tecnicos_clubes.py

# Análisis de goles detallados
python3 analyze_goles_detallados.py

# Análisis de técnicos-jugadores
python3 analyze_tecnicos_jugadores_temporadas.py
```

## 📈 Qué analiza cada script

### 1. Jugadores - Clubes por País
- Países con más clubes representados
- Cobertura de clubes argentinos vs extranjeros
- Jugadores por país

### 2. Técnicos - Clubes por País
- Países donde dirigieron los técnicos
- Distribución geográfica de clubes dirigidos
- Cobertura Argentina vs internacional

### 3. Goles Detallados por Temporada
- Temporadas con más goles registrados
- Cobertura temporal (años con/sin datos)
- Top goleadores históricos
- Competiciones con más datos

### 4. Técnicos-Jugadores por Temporada
- Temporadas con mejor cobertura
- Técnicos con más datos disponibles
- Jugadores más dirigidos
- Brechas temporales en los datos

### 5. Posiciones de Transfermarkt ⭐ NUEVO
- Todas las posiciones únicas encontradas
- Frecuencia de cada posición
- Mapeo recomendado para formaciones
- Comparación entre archivos de datos
- Guardado en `posiciones_unicas.txt`

## 📊 Output

Cada script genera:
- **Reportes en consola** con formato visual (tablas, barras de progreso, emojis)
- **Métricas clave** para decidir qué juegos implementar
- **Recomendaciones** basadas en la calidad de datos

El script maestro además genera:
- `analysis_summary.txt` - Resumen ejecutivo de todos los análisis

## 🎯 Propósito

Estos análisis te ayudan a:
1. **Evaluar viabilidad** de diferentes juegos
2. **Identificar temporadas** con mejor cobertura
3. **Detectar brechas** en los datos
4. **Tomar decisiones** informadas sobre qué implementar

## 💡 Interpretación de Resultados

### ✅ Buena Cobertura
- **Jugadores**: >10 clubes por país, >50 jugadores con historial
- **Temporadas**: >15 jugadores o >20 goles por temporada
- **Técnicos**: >5 temporadas con datos completos

### ⚠️ Cobertura Limitada
- Pocos jugadores internacionales
- Brechas temporales grandes (>5 años sin datos)
- Técnicos con <15 jugadores registrados

### ❌ Datos Insuficientes
- <8 jugadores por formación posible
- <3 temporadas con datos
- Sin información de ciertos períodos clave

## 📝 Notas

- Los scripts leen los JSONs desde `../data/output/`
- No modifican los datos originales
- Son seguros de ejecutar múltiples veces
- El análisis completo toma ~10-30 segundos
