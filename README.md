# 📊 Dashboard Económico Argentina

Pipeline de análisis macroeconómico en tiempo real para Argentina.

🔗 **[Ver demo en vivo](https://dash-economico-ar.streamlit.app/)**

## ¿Qué muestra?

- **Inflación IPC** — datos oficiales del INDEC
- **Tipo de cambio** — oficial vs blue (Bluelytics API)
- **Salario real** — evolución del poder adquisitivo
- **Reservas BCRA**
- **Calculadora de inflación** — comparación entre gestiones presidenciales

## Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)

- **ETL automático** desde APIs públicas: INDEC, BCRA, Bluelytics
- **Deployed** en Streamlit Cloud

## Correr localmente

```bash
git clone https://github.com/FranMichelJr/argentina-dashboard
cd argentina-dashboard
pip install -r requirements.txt
streamlit run app.py
```
