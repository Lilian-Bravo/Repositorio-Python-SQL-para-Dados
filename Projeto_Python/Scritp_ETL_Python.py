# Notebook completo: carregamento, EDA, limpeza, flags, agregação, clustering, export (rodar em Jupyter/Colab)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os

# --- caminhos dos arquivos (ajuste se necessário) ---
tx_path = "dataset-transacciones.csv"
users_path = "dataset-users.csv"

# --- 1) carregar ---
tx = pd.read_csv(tx_path)
users = pd.read_csv(users_path)
print("Loaded shapes:", tx.shape, users.shape)

# --- 2) inspeção inicial ---
print(tx.columns.tolist())
print(users.columns.tolist())
print(tx.dtypes)
print(users.dtypes)

# --- 3) normalização nomes colunas ---
tx.columns = [c.strip().lower().replace(' ', '_') for c in tx.columns]
users.columns = [c.strip().lower().replace(' ', '_') for c in users.columns]

# --- 4) parse de datas (detecta colunas com 'date'/'time') ---
for c in tx.columns:
    if 'date' in c or 'time' in c or 'timestamp' in c:
        tx[c] = pd.to_datetime(tx[c], errors='coerce')

# colunas numéricas - coerção do amount
amount_col = None
for c in tx.columns:
    if 'amount' in c:
        amount_col = c
        tx[c] = pd.to_numeric(tx[c], errors='coerce')
        break

# --- 5) deduplicação e nulos ---
tx = tx.drop_duplicates()
print("Duplicates removed, dataset length:", len(tx))
print("Missing values (transactions):")
print(tx.isna().sum().sort_values(ascending=False).head(20))
print("Missing values (users):")
print(users.isna().sum().sort_values(ascending=False).head(20))

# --- 6) identificar join key ---
join_key = None
for k in ['user_id','userid','id','customer_id','client_id']:
    if k in tx.columns and k in users.columns:
        join_key = k
        break
if not join_key:
    possible_user_keys = [c for c in users.columns if 'id' in c]
    possible_tx_keys = [c for c in tx.columns if 'id' in c]
    common = set(possible_user_keys).intersection(set(possible_tx_keys))
    if common:
        join_key = list(common)[0]

print("Join key:", join_key)

# --- 7) features por usuário (agregação) ---
if join_key:
    group = tx.groupby(join_key)
    if amount_col:
        user_agg = group[amount_col].agg(['count','sum','mean','max','min']).rename(columns={
            'count':'txn_count','sum':'total_amount','mean':'avg_amount','max':'max_amount','min':'min_amount'
        })
    else:
        user_agg = group.size().to_frame('txn_count')
    # datas
    dt_cols = [c for c in tx.columns if tx[c].dtype.kind == 'M']
    if dt_cols:
        dtcol = dt_cols[0]
        user_agg['first_tx'] = group[dtcol].min()
        user_agg['last_tx'] = group[dtcol].max()
        user_agg['active_days'] = (user_agg['last_tx'] - user_agg['first_tx']).dt.days + 1
    # merchants distintos (se existir)
    merchant_cols = [c for c in tx.columns if 'merchant' in c or 'receiver' in c or 'payee' in c]
    if merchant_cols:
        user_agg['distinct_merchants'] = group[merchant_cols[0]].nunique()

    user_agg = user_agg.reset_index()
    print(user_agg.head())

# --- 8) flags de suspeita (regras simples explicadas abaixo) ---
tx['suspicious'] = False

# regra 1: valores <= 0
if amount_col:
    tx.loc[tx[amount_col] <= 0, 'suspicious'] = True

# regra 2: outliers globais (IQR agressivo)
if amount_col:
    q1 = tx[amount_col].quantile(0.25)
    q3 = tx[amount_col].quantile(0.75)
    iqr = q3 - q1
    upper_whisker = q3 + 5 * iqr
    tx.loc[tx[amount_col] > upper_whisker, 'suspicious'] = True

# regra 3: bursts (múltiplas tx rápidas do mesmo usuário)
if join_key and dt_cols:
    dtcol = dt_cols[0]
    tx_sorted = tx.sort_values([join_key, dtcol]).copy()
    tx_sorted['prev_time'] = tx_sorted.groupby(join_key)[dtcol].shift(1)
    tx_sorted['delta_seconds'] = (tx_sorted[dtcol] - tx_sorted['prev_time']).dt.total_seconds()
    tx_sorted['quick_flag'] = tx_sorted['delta_seconds'] <= 60  # dentro de 1 minuto
    # detecta rajadas: 3+ transações rápidas num pequeno rolling window
    tx_sorted['burst_count_5'] = tx_sorted.groupby(join_key)['quick_flag'].rolling(5, min_periods=1).sum().reset_index(level=0, drop=True)
    tx_sorted['burst'] = tx_sorted['burst_count_5'] >= 3
    # aplicar ao tx original
    tx = tx.merge(tx_sorted[[tx_sorted.index.name or 'index', 'delta_seconds','burst']].reset_index(), left_index=True, right_on='index', how='left').drop(columns=['index'])
    tx['suspicious'] = tx['suspicious'] | tx['burst'].fillna(False)
    # limpar colunas auxiliares se preferir
    tx.drop(columns=['index'], errors='ignore', inplace=True)

# --- 9) clustering por usuário (KMeans) ---
if join_key and 'user_agg' in locals():
    features = ['txn_count']
    if 'total_amount' in user_agg.columns:
        features += ['total_amount','avg_amount','max_amount']
    if 'distinct_merchants' in user_agg.columns:
        features += ['distinct_merchants']
    if 'active_days' in user_agg.columns:
        features += ['active_days']

    u = user_agg[features].fillna(0).copy()
    # reduzir skew: log1p onde fizer sentido
    for col in ['txn_count','total_amount','avg_amount','max_amount']:
        if col in u.columns:
            u[col+'_log'] = np.log1p(u[col])
    cluster_cols = [c for c in u.columns if c.endswith('_log') or c in ['distinct_merchants','active_days']]
    X = u[cluster_cols].values
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    # heurística para k: teste 2..6 e escolha (aqui deixamos 3 por default)
    k = 3
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(Xs)
    user_agg['cluster'] = labels
    print("Cluster counts:\n", user_agg['cluster'].value_counts())

# --- 10) preparar tabelas finais para Tableau ---
# transactions: manter colunas úteis e converter dt para string/ISO
tx_for_tableau = tx.copy()
dt_cols = [c for c in tx_for_tableau.columns if tx_for_tableau[c].dtype.kind == 'M']
if dt_cols:
    dtcol = dt_cols[0]
    tx_for_tableau['tx_datetime'] = tx_for_tableau[dtcol]
    tx_for_tableau['tx_date'] = tx_for_tableau['tx_datetime'].dt.date
    tx_for_tableau['tx_hour'] = tx_for_tableau['tx_datetime'].dt.hour

keep = []
if join_key: keep.append(join_key)
if amount_col: keep.append(amount_col)
if 'tx_datetime' in tx_for_tableau.columns: keep += ['tx_datetime','tx_date','tx_hour']
for col in ['suspicious','burst','delta_seconds']:
    if col in tx_for_tableau.columns: keep.append(col)
keep = [c for c in keep if c in tx_for_tableau.columns]
tx_for_tableau = tx_for_tableau[keep]

# unir cluster aos registros de transação (se houver)
if join_key and 'user_agg' in locals():
    cluster_map = user_agg.set_index(join_key)['cluster'].to_dict()
    tx_for_tableau['user_cluster'] = tx_for_tableau[join_key].map(cluster_map)

# users preparados
if join_key and 'user_agg' in locals():
    users_for_tableau = users.merge(user_agg[[join_key,'cluster','txn_count','total_amount','avg_amount','max_amount','distinct_merchants','active_days']], on=join_key, how='left')
else:
    users_for_tableau = users.copy()

# --- 11) salvar CSVs prontos para Tableau ---
out_tx = "transactions_for_tableau.csv"
out_users = "users_for_tableau.csv"
tx_for_tableau.to_csv(out_tx, index=False)
users_for_tableau.to_csv(out_users, index=False)
print("Saved:", out_tx, out_users)

# --- 12) plots rápidos (matplotlib; um plot por figura) ---
if 'tx_date' in tx_for_tableau.columns:
    tx_counts = tx_for_tableau.groupby('tx_date').size()
    plt.figure(figsize=(10,4))
    plt.plot(tx_counts.index, tx_counts.values)
    plt.title("Transactions per day")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()

if amount_col and amount_col in tx_for_tableau.columns:
    plt.figure(figsize=(8,4))
    plt.hist(tx_for_tableau[amount_col].dropna(), bins=50)
    plt.title("Amount distribution")
    plt.xlabel("Amount")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()

if 'user_agg' in locals():
    cluster_summary = user_agg.groupby('cluster').agg({'txn_count':'mean','total_amount':'mean','distinct_merchants':'mean'}).reset_index()
    print(cluster_summary)
    plt.figure(figsize=(8,4))
    plt.bar(cluster_summary['cluster'].astype(str), cluster_summary['total_amount'])
    plt.title("Average total_amount by cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Average total_amount")
    plt.tight_layout()
    plt.show()
