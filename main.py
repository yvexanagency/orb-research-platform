from core.data_loader import load_data
from core.indicators import add_indicators

df = load_data("data/nq_1m.csv")
df = add_indicators(df)

print(df.columns)
print(df.head())