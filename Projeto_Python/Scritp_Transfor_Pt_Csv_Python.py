import pandas as pd

# Caminhos dos arquivos parquet
file_transactions = "dataset-transacciones.parquet"
file_users = "dataset-users.parquet"

# Lê os arquivos parquet (funciona com pyarrow ou fastparquet, qualquer um dos dois precisa estar instalado)
df_transactions = pd.read_parquet(file_transactions)
df_users = pd.read_parquet(file_users)

# Salva em CSV
df_transactions.to_csv("dataset-transacciones.csv", index=False)
df_users.to_csv("dataset-users.csv", index=False)

print("Arquivos convertidos com sucesso para CSV!")
