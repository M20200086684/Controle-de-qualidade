import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

st.title("📊 Controle Estatístico de Processo - Gráficos X̄ e R")

uploaded_file = st.file_uploader("Carregue sua planilha Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("### 📂 Dados carregados:")
    st.dataframe(df.head(50))

    # Dados
    data = df.iloc[:, 1:].values
    means = data.mean(axis=1)
    ranges = data.max(axis=1) - data.min(axis=1)
    
    n = data.shape[1]  # tamanho do subgrupo
    k = data.shape[0]  # número de subgrupos

    # Constantes da tabela (até n=10)
    A2_table = {2:1.880, 3:1.023, 4:0.729, 5:0.577, 6:0.483, 7:0.419, 8:0.373, 9:0.337, 10:0.308}
    D3_table = {2:0, 3:0, 4:0, 5:0, 6:0.076, 7:0.136, 8:0.184, 9:0.223, 10:0.256}
    D4_table = {2:3.267, 3:2.574, 4:2.282, 5:2.115, 6:2.004, 7:1.924, 8:1.864, 9:1.816, 10:1.777}

    # Buscar constantes
    A2 = A2_table.get(n, None)
    D3 = D3_table.get(n, None)
    D4 = D4_table.get(n, None)

    if A2 is None:
        st.error(f"⚠️ Constantes de controle não disponíveis para n={n}.")
    else:
        # Calcular estatísticas
        X_double_bar = means.mean()
        R_bar = ranges.mean()
        
        LSCx = X_double_bar + A2 * R_bar
        LICx = X_double_bar - A2 * R_bar
        LCx = X_double_bar

        LSCr = D4 * R_bar
        LICr = D3 * R_bar
        LCr = R_bar

        # Exibir resultados
        st.write("### 📈 Estatísticas do processo")
        st.write(f"**Média geral (X̄̄):** {X_double_bar:.2f}")
        st.write(f"**Média das amplitudes (R̄):** {R_bar:.2f}")

        # Definir cores: vermelho se fora dos limites, azul se dentro
        colors = ['red' if (m > LSCx or m < LICx) else 'blue' for m in means]   
        # Gráfico X-barra
        fig, ax = plt.subplots(figsize=(10,5))
        ax.scatter(range(1, k+1), means, c=colors, s=80, zorder=3)  # pontos coloridos
        ax.plot(range(1, k+1), means, linestyle='-', color='gray', zorder=2)  # linha conectando pontos
        ax.axhline(LSCx, color='red', linestyle='--', label='LSC')
        ax.axhline(LCx, color='green', linestyle='--', label='LC')
        ax.axhline(LICx, color='red', linestyle='--', label='LIC')
        ax.set_title(f"Gráfico de Controle X̄ (n={n})")
        ax.set_xlabel("Subgrupo")
        ax.set_ylabel("Média")
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # eixo X com números inteiros
        ax.legend()
        st.pyplot(fig)


        # Definir cores: vermelho se fora dos limites, azul se dentro
        colors = ['red' if (m > LSCr or m < LICr) else 'blue' for m in ranges] 
        # Gráfico R
        fig, ax = plt.subplots(figsize=(10,5))
        ax.scatter(range(1, k+1), ranges, c=colors, s=80, zorder=3)  # pontos coloridos
        ax.plot(range(1, k+1), ranges, linestyle='-', color='gray', zorder=2)  # linha conectando pontos
        ax.axhline(LSCr, color='red', linestyle='--', label='LSC')
        ax.axhline(LCr, color='green', linestyle='--', label='LC')
        ax.axhline(LICr, color='red', linestyle='--', label='LIC')
        ax.set_title(f"Gráfico de Controle R (n={n})")
        ax.set_xlabel("Subgrupo")
        ax.set_ylabel("Amplitude (R)")
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # eixo X com números inteiros
        ax.legend()
        st.pyplot(fig)


        # --- Análise de Capacidade ---
        st.write("### 📊 Análise de Capacidade do Processo")

        st.write("### ⚙️ Especificação do Cliente")

        # Valor alvo da especificação (nominal)
        target = st.number_input("Especificação do cliente (valor nominal):", value=450.0)

        # Tolerâncias
        tol_inf = st.number_input("Tolerância inferior:", value=10.0)
        tol_sup = st.number_input("Tolerância superior:", value=10.0)

        # Cálculo automático dos limites
        LIC = target - tol_inf
        LSC = target + tol_sup

        
        st.write(f"**Limite Superior (LSC):** {LSC:.2f}")
        st.write(f"**Limite Inferior (LIC):** {LIC:.2f}")

        # Desvio-padrão estimado (via R-bar/d2 ou direto dos dados)
        d2_table = {2:1.128, 3:1.693, 4:2.059, 5:2.326, 6:2.534, 7:2.704, 8:2.847, 9:2.970, 10:3.078}
        d2 = d2_table.get(n, None)

        if d2 is not None:
            sigma = R_bar / d2
        else:
            sigma = data.std(ddof=1).mean()  # fallback

        Cp = (LSC - LIC) / (6 * sigma)
        Cpk = min((LSC - X_double_bar) / (3 * sigma),
                (X_double_bar - LIC) / (3 * sigma))

        st.write(f"**Desvio padrão estimado (σ):** {sigma:.3f}")
        st.write(f"**Cp:** {Cp:.3f}")
        st.write(f"**Cpk:** {Cpk:.3f}")

        # Histograma com limites
        fig, ax = plt.subplots(figsize=(10,5))
        ax.hist(data.flatten(), bins=15, color='skyblue', edgecolor='black', density=True)
        ax.axvline(LSC, color='red', linestyle='--', label='LSC')
        ax.axvline(X_double_bar, color='green', linestyle='--', label='Média')
        ax.axvline(LIC, color='red', linestyle='--', label='LIC')

        ax.set_title("Histograma com limites de especificação")
        ax.set_xlabel("Valor do processo")
        ax.set_ylabel("Frequência relativa")
        ax.legend()
        st.pyplot(fig)


        