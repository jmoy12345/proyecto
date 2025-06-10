# Proyecto de Extracción, Transformación y Visualización de Datos de UFC

Este proyecto consiste en un sistema completo de web scraping, transformación, almacenamiento y visualización de datos sobre luchadores, peleas y eventos de la UFC, extraídos del sitio [ufcstats.com].
Está desarrollado en Python con uso de librerías como BeautifulSoup, Pandas, SQLAlchemy, y herramientas de visualización como Plotly y Dash.

---

## Contenido

- [Descripción del problema](#descripción-del-problema)
- [Objetivos](#objetivos)
- [Fase 1: Extracción de Datos (Web Scraping)](#fase-1-extracción-de-datos-web-scraping)
- [Fase 2: Transformación de los Datos](#fase-2-transformación-de-los-datos)
- [Fase 3: Carga en la Base de Datos](#fase-3-carga-en-la-base-de-datos)
- [Visualización](#visualización)
- [Resultado Esperado](#resultado-esperado)

---

## Descripción del problema

El objetivo de este proyecto es llevar a cabo un proceso de web scraping utilizando Python para extraer información detallada sobre las peleas y los luchadores de la UFC desde el sitio web ufcstats.com. El proceso incluye:

- Extracción de datos
- Transformación de los datos
- Carga en una base de datos MySQL
- Visualización interactiva con dashboards

---

## Objetivos

- Analizar cómo influyen los datos demográficos (edad, altura, peso) en el rendimiento de los luchadores.
- Estudiar la relación entre experiencia (número de peleas) y resultados (victorias/derrotas).
- Evaluar diferencias estadísticas entre clases de peso.
- Determinar la frecuencia de métodos de victoria por clase de peso.
- Identificar países con mayor número de eventos organizados.

---

## Fase 1: Extracción de Datos (Web Scraping)

Se realizó web scraping a [ufcstats.com](http://www.ufcstats.com/statistics/events/completed?page=all) usando `BeautifulSoup` y `requests` para extraer:

- **Eventos:** nombre, fecha y ubicación.
- **Luchas:** clase de peso, método de victoria, rondas, tiempo.
- **Luchadores:** edad, altura, peso, alcance, precisión de golpes y derribos.

### Estructura de URLs utilizada:

- Eventos: `http://www.ufcstats.com/event-details/ID`
- Peleas: `http://www.ufcstats.com/fight-details/ID`
- Luchadores: `http://www.ufcstats.com/fighter-details/ID`

Los datos se guardaron en múltiples archivos `.csv` para evitar pérdidas por fallos durante la ejecución.

---

## Fase 2: Transformación de los Datos

Se usó la librería `pandas` para:

- Eliminar valores nulos
- Corregir formatos inconsistentes (fechas, números, símbolos como `%`)
- Rellenar valores con promedios
- Generar estadísticas derivadas para análisis

Se utilizó un entorno interactivo de iPython para registrar los pasos de limpieza mediante `%history -f`.

---

## Fase 3: Carga en la Base de Datos

Los datos fueron cargados en una base de datos relacional **MySQL** mediante `SQLAlchemy` (ORM). Se diseñó un modelo relacional con 10 tablas:

- `fighters`
- `fights`
- `events`
- `fight_stats`
- `weight_classes`
- `stances`
- `cities`
- `states`
- `countries`
- `method`

Los IDs fueron derivados de los fragmentos finales de las URLs para mantener relaciones entre entidades.

---

## Visualización

Se desarrollaron **8 dashboards interactivos** usando Dash y Plotly:

1. **Distribución de luchadores por clase de peso** (gráfico de pastel).
2. **Relación edad-victorias por año** (gráfico de burbujas).
3. **Distribución de victorias/derrotas por clase de peso**.
4. **Método de victoria por clase de peso**.
5. **Altura y peso de luchadores con rendimiento (victorias/derrotas)**.
6. **Probabilidad de victoria basada en número de peleas**.
7. **Cantidad de peleas por país**.
8. **Número de peleas por año**.

Cada gráfico permite interacción y visualización detallada al pasar el cursor sobre los datos.

---

## Resultado Esperado

El sistema desarrollado permite:

- Consultar y analizar de forma interactiva los datos históricos de UFC.
- Obtener insights sobre factores que influyen en el desempeño de los luchadores.
- Construir una base sólida para modelos predictivos y analítica deportiva avanzada.

---

### Equipo de trabajo

- Castañón Cueto Josué Moisés  
- Antonio Rodríguez Alejandro  
- López Villalobos Juan Pablo  
- Muñoz Torres Jesús Heriberto  
- Solis Leyva Luis Angel  

**Profesor:** Josué Miguel Flores Parra  
**Universidad Autónoma de Baja California – FCA**  
**Grupo:** 951 y 952  
**Fecha:** 10 de junio de 2025
