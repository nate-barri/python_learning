import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

df = pd.read_csv('Datasets/netflix_country_exploded.csv')

print(df.head())

print("\nDATA INFO")
df.info()

print("\nSHAPE:", df.shape)

print("\nDESCRIBE")
print(df.describe())

print("\nMISSING VALUES")
print(df.isnull().sum())

missing_percentage = (df.isnull().sum() / len(df)) * 100
print("\nMISSING PERCENTAGE")
print(missing_percentage.sort_values(ascending=False))

print("\nUnique")
print(df.nunique())

print("\nSAMPLES")  
print(df.sample(10, random_state=42))

print("\nTypes")
print(df["type"].value_counts())

print("\nTypes%")
print(df["type"].value_counts(normalize=True) * 100)