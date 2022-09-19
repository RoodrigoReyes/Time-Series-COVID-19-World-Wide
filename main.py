import glob
import pandas as pd
from func.functions import *

import warnings
warnings.filterwarnings("ignore")

"""
Links de Descarga
"""
POSITIVE_URL = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

DEATHS_URL = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

RECOVER_URL = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

VACCINE_URL = 'https://github.com/govex/COVID-19/raw/master/data_tables/vaccine_data/global_data/time_series_covid19_vaccine_doses_admin_global.csv'


""" Función Principal """
def main():

    """ Descarga de archivos .csv's """
    downlad_file(POSITIVE_URL,'world covid data/positives','.csv')
    downlad_file(DEATHS_URL,'world covid data/deaths','.csv')
    downlad_file(RECOVER_URL,'world covid data/recovered','.csv')
    downlad_file(VACCINE_URL,'world covid data/vaccine','.csv')

    """ Lista de archivos (POSITIVOS - FALLECIDOS - RECUPERADOS - VACUNACIONES) """
    positive_covid_files = glob.glob("world covid data/positives/*.csv", recursive=True)
    death_covid_files = glob.glob("world covid data/deaths/*.csv", recursive=True)
    recovered_covid_files = glob.glob("world covid data/recovered/*.csv", recursive=True)
    vaccines_list = glob.glob("world covid data/vaccine/*.csv", recursive=True)
    
    """ Lectura de archivos descargados el día de hoy """
    positives = pd.read_csv(positive_covid_files[-1])
    deaths = pd.read_csv(death_covid_files[-1])
    recovered = pd.read_csv(recovered_covid_files[-1])
    vaccine_df = pd.read_csv(vaccines_list[-1])

    """ Limpieza de datos y homologación """
    positives = clean_covid(positives)
    deaths = clean_covid(deaths)
    recovered = clean_covid(recovered)
    vaccine_df = clean_vaccines(vaccine_df)

    """ Importando Data a Tabla ya creada en Base de Datos PostgreSQL """
    dataframe_import(positives, 'covid.positives')
    dataframe_import(deaths, 'covid.deaths')
    dataframe_import(recovered, 'covid.recovered')
    dataframe_import(vaccine_df,'covid.vaccines')

    """ Refrescando Vista Materializada """
    refresh_materialed_view()

#Ejecución de Script
if __name__ == '__main__':

    # NaN Values
    psycopg2.extensions.register_adapter(float, nan_to_null)

    #Ejecutando Script
    main()
