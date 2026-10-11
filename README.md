# Sistema Predictivo LPF

Sistema predictivo para la Liga Panamena de Futbol desarrollado como proyecto de tesis. Integra preparacion de datos, analisis exploratorio, ingenieria de caracteristicas, entrenamiento de modelos de Machine Learning y una aplicacion interactiva en Streamlit para consultar predicciones de partidos.

## Objetivo

Construir una herramienta de apoyo analitico para estimar resultados de partidos de la LPF a partir de historicos deportivos, modelos supervisados y distribuciones de goles. El sistema combina un modelo XGBoost para la clasificacion del resultado del encuentro con modelos de Poisson para estimar marcadores probables.

## Caracteristicas principales

- Consolidacion de datos historicos de partidos y equipos de la Liga Panamena de Futbol.
- Analisis exploratorio con visualizaciones de goles, resultados, temporadas y desempeno por equipo.
- Ingenieria de caracteristicas basada en forma reciente, rendimiento historico, condicion local/visitante y descanso.
- Entrenamiento y evaluacion de modelos de regresion logistica, random forest, XGBoost y Poisson.
- Validacion temporal para evaluar estabilidad del rendimiento predictivo.
- Aplicacion Streamlit con seleccion de temporada, fecha, equipo local y equipo visitante.
- Historial local de analisis mediante SQLite.

## Estructura del proyecto

```text
app/
  app.py                    # Aplicacion principal en Streamlit
  assets/                   # Estilos e imagenes de equipos
  services/                 # Servicios de datos, modelos, Poisson y prediccion
data/
  raw/                      # Datos originales
  processed/                # Datos integrados y listos para modelado
figures/                    # Graficas generadas durante el analisis
models/                     # Modelos entrenados en formato joblib
notebooks/                  # Flujo de preparacion, EDA, modelado y validacion
requirements.txt            # Dependencias del proyecto
```

## Modelos incluidos

- `models/xgboost_lpf.joblib`
- `models/xgboost_label_encoder.joblib`
- `models/poisson_local_lpf.joblib`
- `models/poisson_visitante_lpf.joblib`
- `models/random_forest_lpf.joblib`
- `models/regresion_logistica_lpf.joblib`

## Requisitos

- Python 3.11 o superior recomendado.
- Dependencias listadas en `requirements.txt`.

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecucion de la aplicacion

```bash
streamlit run app/app.py
```

La aplicacion carga los datos procesados desde `data/processed/`, los modelos desde `models/` y crea automaticamente la base SQLite local en `database/` para guardar el historial de consultas.

## Flujo analitico

Los notebooks documentan el proceso completo:

1. Preparacion de datos.
2. Analisis exploratorio.
3. Ingenieria de caracteristicas.
4. Separacion de entrenamiento, validacion y prueba.
5. Modelado con regresion logistica.
6. Modelado con random forest.
7. Modelado con XGBoost.
8. Modelado de goles con Poisson.
9. Validacion cruzada temporal.

## Seguridad y control de versiones

El repositorio ignora entornos virtuales, archivos `.env`, credenciales, caches, checkpoints de notebooks, bases SQLite locales y copias de respaldo. Los datasets y modelos entrenados se conservan dentro del proyecto porque forman parte del entregable reproducible.

## Licencia

Proyecto academico desarrollado para fines de investigacion y tesis.
