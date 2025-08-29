import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from io import BytesIO

# Importa a lógica dos subsistemas
from subsystem_logic import COF, AED, SIF1, evaluate_subsystem
from main_system_logic import DOP, OEA, SIF1_main, IFDH, evaluate_main_system

# =============================================================================
# CSS Personalizado para as Abas
# =============================================================================
st.markdown("""
<style>
/* Estilo para a barra de abas */
div[data-baseweb="tab-list"] {
    gap: 10px; /* Espaçamento entre as abas */
}

/* Estilo para cada aba individual */
button[data-baseweb="tab"] {
    background-color: #E0F2F7; /* Cor de fundo padrão para abas */
    color: #000000; /* Cor do texto */
    border-radius: 8px; /* Cantos arredondados */
    padding: 10px 20px; /* Preenchimento */
    font-size: 16px; /* Tamanho da fonte */
    font-weight: bold; /* Negrito */
    border: 1px solid #B0E0E6; /* Borda */
    transition: all 0.2s ease-in-out; /* Transição suave */
}

/* Estilo para a aba selecionada */
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #4CAF50; /* Cor de fundo para aba selecionada (verde) */
    color: white; /* Cor do texto para aba selecionada */
    border-color: #4CAF50;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Sombra para destacar */
}

/* Estilo para o hover da aba */
button[data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    background-color: #B0E0E6; /* Cor de fundo ao passar o mouse */
    color: #333333;
    border-color: #87CEEB;
}

/* Oculta o indicador de seleção padrão do Streamlit abaixo da aba */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
  box-shadow: none;
}
</style>
""", unsafe_allow_html=True)



# =============================================================================
# Funções de Plotagem (reorganizadas para Streamlit)
# =============================================================================
# As funções plot_mfs_subsystem() e plot_output_subsystem()
# não serão mais usadas para a aba interativa do subsistema,
# mas são mantidas aqui caso sejam usadas em outros lugares ou para referência.
def plot_mfs_subsystem_static():  # Renomeado para evitar conflito e indicar que é estático
    fig, axs = plt.subplots(2, 1, figsize=(6, 8))

    # Plot COF
    for term, mf in COF.terms.items():
        axs[0].plot(COF.universe, mf.mf, label=term)
    axs[0].set_title("COF")
    axs[0].legend()
    axs[0].grid(True)

    # Plot AED
    for term, mf in AED.terms.items():
        axs[1].plot(AED.universe, mf.mf, label=term)
    axs[1].set_title("AED")
    axs[1].legend()
    axs[1].grid(True)

    fig.tight_layout()
    return fig


def plot_output_subsystem_static():  # Renomeado para evitar conflito e indicar que é estático
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    for term, mf in SIF1.terms.items():
        ax.plot(SIF1.universe, mf.mf, label=term)
    ax.set_title("SIF1 (Saída)")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    return fig


def plot_mfs_main_system():
    fig = plt.figure(figsize=(6, 8))
    gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1])
    ax_dop = fig.add_subplot(gs[0, 0])
    ax_oea = fig.add_subplot(gs[0, 1])
    ax_sif1 = fig.add_subplot(gs[1, :])

    # Plot DOP
    for term, mf in DOP.terms.items():
        ax_dop.plot(DOP.universe, mf.mf, label=term)
    ax_dop.set_title("DOP")
    ax_dop.legend()
    ax_dop.grid(True)

    # Plot OEA
    for term, mf in OEA.terms.items():
        ax_oea.plot(OEA.universe, mf.mf, label=term)
    ax_oea.set_title("OEA")
    ax_oea.legend()
    ax_oea.grid(True)

    # Plot SIF1 (Entrada Subsistema)
    for term, mf in SIF1_main.terms.items():
        ax_sif1.plot(SIF1_main.universe, mf.mf, label=term)
    ax_sif1.set_title("SIF1 (Entrada)")
    ax_sif1.legend()
    ax_sif1.grid(True)

    fig.tight_layout()
    return fig


def plot_output_main_system():
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    for term, mf in IFDH.terms.items():
        ax.plot(IFDH.universe, mf.mf, label=term)
    ax.set_title("IFDH (Saída)")
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    return fig


def plot_dynamic_mf(variable, value):
    fig, ax = plt.subplots(figsize=(6, 4))
    for term, mf in variable.terms.items():
        ax.plot(variable.universe, mf.mf, label=term)
        y_value = np.interp(value, variable.universe, mf.mf)
        ax.plot(value, y_value, 'o', markersize=8)
    ax.axvline(x=value, color='k', linestyle='--', linewidth=1)
    ax.set_title(f"{variable.label} (x = {value:.2f})")
    ax.set_xlabel("Universo")
    ax.set_ylabel("Grau de Pertinência")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    return fig


def plot_interactive_subsystem(cof_val, aed_val):
    """Gera gráficos interativos para as funções de pertinência do subsistema."""

    # Avalia o subsistema para obter o resultado de SIF1
    sif1_result = evaluate_subsystem(cof_val, aed_val)

    # Cria a figura para os plots
    fig = plt.figure(figsize=(8, 10))
    gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1.5])
    ax_cof = fig.add_subplot(gs[0])
    ax_aed = fig.add_subplot(gs[1])
    ax_sif1 = fig.add_subplot(gs[2])

    # Plot COF
    for term, mf in COF.terms.items():
        ax_cof.plot(COF.universe, mf.mf, label=term)
    ax_cof.set_title("COF")
    ax_cof.legend()
    ax_cof.grid(True)
    ax_cof.axvline(x=cof_val, color='k', linestyle='--', linewidth=1)

    # Plot AED
    for term, mf in AED.terms.items():
        ax_aed.plot(AED.universe, mf.mf, label=term)
    ax_aed.set_title("AED")
    ax_aed.legend()
    ax_aed.grid(True)
    ax_aed.axvline(x=aed_val, color='k', linestyle='--', linewidth=1)

    # Plot SIF1
    for term, mf in SIF1.terms.items():
        ax_sif1.plot(SIF1.universe, mf.mf, label=term)
    ax_sif1.set_title(f"SIF1 (Saída) - Valor: {sif1_result:.2f}")
    ax_sif1.legend()
    ax_sif1.grid(True)
    ax_sif1.axvline(x=sif1_result, color='k', linestyle='--', linewidth=1)

    fig.tight_layout()
    return fig


# =============================================================================
# Interface Gráfica com Streamlit
# =============================================================================
st.title("Sistema Fuzzy: Visualização & Simulação")

# Abas para organizar a visualização
tab1_simular, tab2_subsistema, tab3_principal = st.tabs(["Simulação", "Subsistema", "Sistema Principal"])

# Inicializar o estado da sessão
if 'simulacao_ativa' not in st.session_state:
    st.session_state.simulacao_ativa = False
with tab1_simular:
    st.header("Simulação Dinâmica & Processamento de Lote")

    st.markdown("### Simulação Manual")

    col1, col2 = st.columns(2)
    with col1:
        cof_val = st.slider("Coabitação Familiar:", 0.0, 80.0, 40.0, help="Varia de 0 a 80")
        dop_val = st.slider("Domicílios precários:", 0.0, 40.0, 20.0, help="Varia de 0 a 40")
    with col2:
        aed_val = st.slider("Adensamento familiar:", 0.0, 40.0, 15.0, help="Varia de 0 a 40")
        oea_val = st.slider("Ônus Excessivoo com Aluguel:", 0.0, 70.0, 35.0, help="Varia de 0 a 70")

    # Botão que ativa o modo de auto-cálculo
    if st.button("Simular"):
        st.session_state.simulacao_ativa = True

    # Esta parte do código só será executada se o botão "Simular" já tiver sido clicado
    if st.session_state.simulacao_ativa:
        sif1_result = evaluate_subsystem(cof_val, aed_val)
        ifdh_result = evaluate_main_system(dop_val, oea_val, sif1_result)

        st.markdown("---")
        st.subheader("Resultados da Simulação")

        if ifdh_result is not None:
            st.success(f"**SIF1 (Subsistema):** {sif1_result:.2f}")
            st.success(f"**IFDH (Final):** {ifdh_result:.2f}")
            st.markdown("---")
            st.subheader("Gráfico Dinâmico de SIF1")
            st.pyplot(plot_dynamic_mf(SIF1, sif1_result))
        else:
            st.error(
                "Erro no cálculo do IFDH. Os valores de entrada não ativaram nenhuma regra. Tente valores mais altos.")

    st.markdown("---")

    st.markdown("### Processamento de Arquivo XLSX")

    uploaded_file = st.file_uploader("Carregar arquivo XLSX", type=["xlsx"], key="xlsx_uploader")

    if uploaded_file:
        df = pd.read_excel(uploaded_file, header=0)
        st.success(f"Arquivo carregado: **{uploaded_file.name}**")
        st.dataframe(df)

        if st.button("Processar Lote"):
            results = []
            for idx, row in df.iterrows():
                try:
                    city = row.iloc[0]
                    cof = float(row.iloc[1])
                    aed = float(row.iloc[2])
                    dop = float(row.iloc[3])
                    oea = float(row.iloc[4])

                    sif1 = evaluate_subsystem(cof, aed)
                    ifdh = evaluate_main_system(dop, oea, sif1)

                    if ifdh is not None:
                        results.append({"Cidade": city, "SIF1": sif1, "IFDH": ifdh})
                    else:
                        results.append({"Cidade": city, "SIF1": sif1, "IFDH": "N/A"})
                except Exception as e:
                    st.error(f"Erro ao processar a linha {idx}: {str(e)}")
                    continue

            results_df = pd.DataFrame(results)
            st.subheader("Resultados Processados")
            st.dataframe(results_df)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                results_df.to_excel(writer, index=False, sheet_name='Resultados')

            st.download_button(
                label="Baixar Resultados em XLSX",
                data=output.getvalue(),
                file_name="resultados_fuzzy.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

with tab2_subsistema:
    st.header("Análise Interativa - Subsistema")

    st.markdown("### Ajuste os valores de entrada e veja o resultado no SIF1")

    # Sliders dedicados para a aba do subsistema
    col1, col2 = st.columns(2)
    with col1:
        cof_val_sub = st.slider("Coabitação Familiar:", 0.0, 80.0, 40.0, key="cof_sub", help="Varia de 0 a 80")
    with col2:
        aed_val_sub = st.slider("Adensamento familiar:", 0.0, 40.0, 15.0, key="aed_sub", help="Varia de 0 a 40")

    st.pyplot(plot_interactive_subsystem(cof_val_sub, aed_val_sub))

with tab3_principal:
    st.header("Funções de Pertinência - Sistema Principal")
    tab2_inputs, tab2_output = st.tabs(["Entradas", "Saída"])
    with tab2_inputs:
        st.pyplot(plot_mfs_main_system())
    with tab2_output:
        st.pyplot(plot_output_main_system())