# scripts/load_census.py
import json

import requests
import pandas as pd
import duckdb as ddb

import api

api_key = api.apiid
url = "http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
params = {
    'appId': api_key,
    'lang': 'E',
    'statsDataId': '0003445133',
    'metaGetFlg': 'Y',
    'cntGetFlg': 'N',
    'explanationGetFlg': 'Y',
    'replaceSpChars': 0
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()

    # Flatten into rows
    records = data['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE']
    df = pd.DataFrame(records)

    # See sample
    print(f"\nColumns {df.columns}\n"
          f"{len(df.values)} records.")
    for i, v in enumerate(list(df.values)):
        if i < 5:
            print(v)

    # STEP 1: Build lookup dictionaries from CLASS_INF
    class_info = data['GET_STATS_DATA']['STATISTICAL_DATA']['CLASS_INF']['CLASS_OBJ']

    # Create mapping dicts
    code_maps = {}
    for class_obj in class_info:
        print(class_obj)
        key = class_obj['@id']  # e.g. 'cat01', 'area'

        # Ensure CLASS is always treated as a list
        classes = class_obj['CLASS']
        if isinstance(classes, dict):
            classes = [classes]  # wrap single dict in list

        value_map = {c['@code']: c['@name'] for c in classes}
        code_maps[key] = value_map

    # STEP 2: Apply mapping to DataFrame
    df['Nationality'] = df['@cat01'].map(code_maps.get('cat01', {}))
    df['Sex'] = df['@cat02'].map(code_maps.get('cat02', {}))
    df['Age'] = df['@cat03'].map(code_maps.get('cat03', {}))
    df['Area'] = df['@area'].map(code_maps.get('area', {}))
    df['Year'] = df['@time'].str[:4]
    df['Population'] = pd.to_numeric(df['$'], errors='coerce').astype('Int64')

    # Connect to your DB (or create it)
    con = ddb.connect("../data/japan_population.duckdb")

    # Save fact table
    fact_df = df[['@time', '@area', '@cat01', '$']].copy()
    fact_df.columns = ['year_code', 'area_code', 'nationality_code', 'population']
    # fact_df['population'] = fact_df['population'].astype(int)
    fact_df['year'] = fact_df['year_code'].str[:4]
    print(fact_df.head())
    # con.execute("CREATE OR REPLACE TABLE population_facts AS SELECT * FROM fact_df")

    # Save dimension tables
    # Grab area metadata
    area_meta = next(obj for obj in class_info if obj['@id'] == 'area')
    area_classes = area_meta['CLASS']

    # Normalize dict to list
    if isinstance(area_classes, dict):
        area_classes = [area_classes]

    # Build DataFrame
    area_records = []
    for entry in area_classes:
        area_records.append({
            'area_code': entry['@code'],
            'region_name': entry['@name'],
            'level': int(entry.get('@level', -1)),  # level might be missing
            'parent_code': entry.get('@parentCode', None)
        })
    area_map = pd.DataFrame(area_records)
    print(area_map.head())
    # con.execute("CREATE OR REPLACE TABLE area_dim AS SELECT * FROM area_map")

    cat01_map = pd.DataFrame.from_dict(code_maps['cat01'], orient='index', columns=['nationality']).reset_index()
    cat01_map.columns = ['nationality_code', 'nationality']
    print(cat01_map.head())
    # con.execute("CREATE OR REPLACE TABLE nationality AS SELECT * FROM cat01_map")

    cat02_map = pd.DataFrame.from_dict(code_maps['cat02'], orient='index', columns=['sex']).reset_index()
    cat02_map.columns = ['sex_code', 'sex']
    print(cat02_map.head())
    # con.execute("CREATE OR REPLACE TABLE sex AS SELECT * FROM cat02_map")

    cat03_map = pd.DataFrame.from_dict(code_maps['cat03'], orient='index', columns=['age (years)']).reset_index()
    cat03_map.columns = ['age_code', 'age (years)']
    print(cat03_map)
    # con.execute("CREATE OR REPLACE TABLE age AS SELECT * FROM cat03_map")

else:
    print(f"❌ Request failed: {response.status_code}")
