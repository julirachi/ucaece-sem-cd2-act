"""Limpieza (ETL) del Utrecht Fairness Recruitment dataset para la actividad de la Unidad 2.

Caso analizado: herramienta de reclutamiento de Amazon que penalizaba a candidatas
mujeres (Dastin, 2018). Para reproducir ese tipo de sesgo se usa solo la empresa B del
dataset, que es la que muestra la brecha de género más marcada en sus decisiones.

Uso (desde la carpeta unidad2/):
    python preparar_dataset.py

Lee data/recruitmentdataset-2022-1.3.csv y escribe data/empresa_b_limpio.csv.
"""

import pandas as pd

RUTA_CSV_CRUDO = "data/recruitmentdataset-2022-1.3.csv"
RUTA_CSV_LIMPIO = "data/empresa_b_limpio.csv"
EMPRESA_ANALIZADA = "B"
GENEROS_ANALIZADOS = ["female", "male"]
COLUMNAS_A_DESCARTAR = ["Id", "company"]
COLUMNA_OBJETIVO = "decision"


def main() -> None:
    dataframe = pd.read_csv(RUTA_CSV_CRUDO)

    # Solo la empresa B y los dos géneros con muestra suficiente ("other" tiene 19 casos).
    dataframe = dataframe[dataframe["company"] == EMPRESA_ANALIZADA]
    dataframe = dataframe[dataframe["gender"].isin(GENEROS_ANALIZADOS)]

    # Id no aporta información y company queda constante tras el filtro.
    dataframe = dataframe.drop(columns=COLUMNAS_A_DESCARTAR)

    # Las columnas booleanas de features pasan a 0/1 para el escalado numérico.
    columnas_booleanas = [
        columna
        for columna in dataframe.columns
        if dataframe[columna].dtype == bool and columna != COLUMNA_OBJETIVO
    ]
    dataframe[columnas_booleanas] = dataframe[columnas_booleanas].astype(int)

    dataframe.to_csv(RUTA_CSV_LIMPIO, index=False)
    print(f"Dataset limpio guardado en {RUTA_CSV_LIMPIO}: {dataframe.shape}")
    print("Tasa de contratación por género:")
    print(dataframe.groupby("gender")[COLUMNA_OBJETIVO].mean().round(3))


if __name__ == "__main__":
    main()
