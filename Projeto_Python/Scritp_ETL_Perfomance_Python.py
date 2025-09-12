import pandas as pd
import numpy as np

# =========================
# 1. Carregar os datasets
# =========================
transactions = pd.read_csv("dataset-transacciones.csv")
users = pd.read_csv("dataset-users.csv")

# =========================
# 2. Tratamento de datas
# =========================
transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"], errors="coerce")
users["data_nascimento"] = pd.to_datetime(users["data_nascimento"], errors="coerce")
users["data_ativacao"] = pd.to_datetime(users["data_ativacao"], errors="coerce")

# =========================
# 3. Remover duplicados
# =========================
transactions.drop_duplicates(inplace=True)
users.drop_duplicates(inplace=True)

# =========================
# 4. Padronização de colunas categóricas
# =========================
for col in ["estado", "ocupacao", "nivel_educacional", "estado_civil", "genero"]:
    if col in users.columns:
        users[col] = users[col].astype(str).str.strip().str.title()

transactions["product_category"] = transactions["product_category"].astype(str).str.strip().str.title()
transactions["payment_method"] = transactions["payment_method"].astype(str).str.strip().str.title()

# =========================
# 5. Criar métricas derivadas
# =========================
transactions["net_revenue"] = (
    transactions["product_amount"]
    - transactions["transaction_fee"]
    + transactions["cashback"]
)

transactions["cashback_rate"] = np.where(
    transactions["product_amount"] > 0,
    transactions["cashback"] / transactions["product_amount"],
    0
)

# =========================
# 6. Enriquecer com dados do usuário
# =========================
df = transactions.merge(users, on="user_id", how="left")

# Tempo de conta ativa
df["dias_conta_ativa"] = (pd.Timestamp.today() - df["data_ativacao"]).dt.days

# Ticket médio por usuário
ticket_medio = df.groupby("user_id")["product_amount"].mean().rename("ticket_medio_usuario")
df = df.merge(ticket_medio, on="user_id", how="left")

# =========================
# 7. Criar dataset agregado (performático para Tableau)
# =========================
df["ano_mes"] = df["transaction_date"].dt.to_period("M").astype(str)

agg = df.groupby(["ano_mes", "estado", "product_category"], as_index=False).agg({
    "transaction_id": "count",
    "product_amount": "sum",
    "transaction_fee": "sum",
    "cashback": "sum",
    "net_revenue": "sum",
    "loyalty_points": "sum",
    "user_id": "nunique"
}).rename(columns={
    "transaction_id": "qtd_transacoes",
    "product_amount": "valor_total",
    "transaction_fee": "taxas_totais",
    "cashback": "cashback_total",
    "net_revenue": "receita_liquida_total",
    "loyalty_points": "pontos_totais",
    "user_id": "usuarios_unicos"
})

# =========================
# 8. Exportar datasets
# =========================
df.to_csv("dados_detalhados.csv", index=False)
agg.to_csv("dados_agregados.csv", index=False)

print("✅ Arquivos exportados:")
print(" - dados_detalhados.csv (nível transação + usuário)")
print(" - dados_agregados.csv (agregado por mês/estado/categoria)")
