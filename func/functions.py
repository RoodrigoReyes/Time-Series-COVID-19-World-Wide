import time
import pandas as pd
import numpy as np
import requests
import datetime
import psycopg2
import psycopg2.extras
from credentials.connections import configuration

drop_countrys = ['China', 'Canada', 'United Kingdom', 'France',
                 'Australia', 'Netherlands', 'Denmark', 'New Zealand']

""" Fecha del día de hoy """
CURRENT_DATE = datetime.date.today().strftime('%Y%d%m')

""" Descarga de archivos con data covid de la fecha de hoy """
def downlad_file(url, path, extension):

    name = url.split('/')[-1].split('.')[0]
    file = name+CURRENT_DATE+extension

    r = requests.get(url, allow_redirects=True)
    open(f'{path}/{file}', 'wb').write(r.content)

    return r.close()


""" Insertar dataframe a tabla en el PostgreSQL """
def dataframe_import(df, table, size=None):
    conn = psycopg2.connect(**configuration)
    cur = conn.cursor()
    if len(df) > 0:
        print(f"Insertando data a la tabla {table}")
        df_columns = list(df)

        columns = ",".join(df_columns)
        values = "VALUES ( {} )".format(",".join(["%s" for _ in df_columns]))

        insert_stmt = "INSERT INTO {} ( {} ) {}".format(table, columns, values)
        cur.execute("truncate " + table + ";")
        cur = conn.cursor()
        if size != None:
            psycopg2.extras.execute_batch(
                cur, insert_stmt, df.values, page_size=size)
        else:
            psycopg2.extras.execute_batch(cur, insert_stmt, df.values)
    conn.commit()

    return


""" Funcion para la importacion de con valores NULL a la respectiva tabla """
def nan_to_null(f, _NULL=psycopg2.extensions.AsIs('NULL'), _Float=psycopg2.extensions.Float):
    if not np.isnan(f):
        return _Float(f)

    return _NULL


""" Limpieza de datos Covid (Positivos - Recuperados - Negativos)"""
def clean_covid(df):

    # df.rename(columns={'Country/Region': 'Country'}, inplace=True)
    # df.drop(columns=['Province/State','Lat','Long'], inplace=True)
    df = df.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'],
                 var_name='Fecha',
                 value_name='Total')
    df.columns = [col.lower() for col in df.columns]

    df['lat'].loc[df['country/region'] == 'Canada'] = 39.916668
    df['long'].loc[df['country/region'] == 'Canada'] = 79.3832
    df['lat'].loc[df['country/region'] == 'China'] = 39.916668
    df['long'].loc[df['country/region'] == 'China'] = 116.383331

    df['fecha'] = df['fecha'].apply(
        lambda x: '/'.join(('0' if len(x) < 2 else '')+x for x in x.split('/')))

    df['fecha'] = pd.to_datetime(df['fecha'])
    df = df.sort_values(by=['country/region', 'fecha'],
                        ascending=[True, True]).reset_index(drop=True)

    df['day_total'] = df.groupby(['country/region'])['total'].diff().fillna(0)
    # df['day_total'] = df.groupby(['country/region','province/state'])['total'].diff().fillna(0)
    # df['day_total'] = df['total'] - df['shift']
    df.drop(columns=['province/state'], inplace=True)

    df.rename(columns={'country/region': 'country'}, inplace=True)
    # df = df.groupby(['country','lat','long','fecha'])['total'].sum().reset_index()
    df = df[~df['country'].isin(drop_countrys)].reset_index(drop=True)
    return df


""" Limpieza de datos Vacunas """
def clean_vaccines(df):

    df.drop(columns=['UID', 'iso2', 'iso3', 'code3', 'FIPS',
            'Admin2', 'Province_State', 'Combined_Key'], inplace=True)
    df = df[df['Population'].notna()]

    df = df.melt(id_vars=['Country_Region', 'Lat', 'Long_', 'Population'],
                 var_name='Fecha',
                 value_name='Total')

    df = df.sort_values(by=['Country_Region', 'Fecha']).reset_index(drop=True)
    df.columns = [col.lower() for col in df.columns]

    df = df.groupby(['country_region', 'fecha', 'lat',
                    'long_']).sum().reset_index()

    df = df.drop_duplicates(subset=['country_region', 'fecha'], keep='first')
    df['fecha'] = pd.to_datetime(df['fecha'])

    df.rename(columns={'country_region': 'country',
              'long_': 'long'}, inplace=True)
    df['day_total'] = df.groupby(['country'])['total'].diff().fillna(0)
    df = df[~df['country'].isin(drop_countrys)].reset_index(drop=True)

    df.loc[df['day_total'] < 0, 'day_total'] = 0

    return df

""" Actualizando Vista Materializada 'covid.view_hd_covid' """
def refresh_materialed_view():
    conn = psycopg2.connect(**configuration)
    cur = conn.cursor()

    cur.execute('refresh materialized view covid.view_hd_covid;')
    conn.commit()
    print('Vista actualizada')
    time.sleep(3)
