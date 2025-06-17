import streamlit as st
import pdfplumber
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="Escala de Funcionários", layout="wide")
st.title("📅 Escala Individual por Funcionário")

uploaded_file = st.file_uploader("📄 Faça upload do PDF da escala geral", type="pdf")
nome_funcionario = st.text_input("👤 Nome do funcionário para filtrar")

def gerar_pdf(df, nome):
    pdf = FPDF(format="A4")
    pdf.add_page()
    pdf.set_margins(left=5, top=5, right=5)
    pdf.set_auto_page_break(auto=False)

    # Definindo as larguras das colunas da tabela
    largura_data = 18
    largura_periodo = 18
    largura_setor = 18
    largura_total_tabela = largura_data + largura_periodo + largura_setor

    # Calculando a posição inicial para centralizar o título sobre a tabela
    margem_esquerda_tabela = pdf.l_margin
    pos_x_titulo = margem_esquerda_tabela

    # Posicionar o título na largura exata da tabela
    pdf.set_x(pos_x_titulo)
    pdf.set_font("Arial", style='B', size=6)
    titulo = f"Escala {nome.title()}"
    titulo_seguro = titulo.encode("latin-1", "replace").decode("latin-1")
    pdf.cell(w=largura_total_tabela, h=4, txt=titulo_seguro, border=0, ln=True, align='C')
    pdf.ln(1)

    # Cabeçalho da tabela
    pdf.set_font("Arial", style='B', size=4.5)
    pdf.set_x(pos_x_titulo)
    pdf.cell(largura_data, 3, "Data", border=1, align='C')
    pdf.cell(largura_periodo, 3, "Período", border=1, align='C')
    pdf.cell(largura_setor, 3, "Setor", border=1, align='C')
    pdf.ln(3)

    pdf.set_font("Arial", size=4.5)

    # Ordenar por data
    df["Data_ordenada"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    df_ordenado = df.sort_values(by="Data_ordenada").reset_index(drop=True)

    dia_anterior = None
    alternar_cor = False

    for _, row in df_ordenado.iterrows():
        data = str(row["Data"])
        periodo = str(row["Período"])
        setor = str(row["Setor"])

        if data != dia_anterior:
            alternar_cor = not alternar_cor
            dia_anterior = data

        if alternar_cor:
            pdf.set_fill_color(230, 230, 230)  # Cinza clarinho
            fill = True
        else:
            fill = False

        linha_data = data.encode("latin-1", "replace").decode("latin-1")
        linha_periodo = periodo.encode("latin-1", "replace").decode("latin-1")
        linha_setor = setor.encode("latin-1", "replace").decode("latin-1")

        pdf.set_x(pos_x_titulo)
        pdf.cell(largura_data, 3, linha_data, border=1, align='C', fill=fill)
        pdf.cell(largura_periodo, 3, linha_periodo, border=1, align='C', fill=fill)
        pdf.cell(largura_setor, 3, linha_setor, border=1, align='C', fill=fill)
        pdf.ln(3)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer



if uploaded_file and nome_funcionario:
    with pdfplumber.open(uploaded_file) as pdf:
        tabela_completa = []
        for page in pdf.pages:
            try:
                tabela = page.extract_table()
                if tabela:
                    tabela_completa.extend(tabela)
            except:
                pass

    if tabela_completa and len(tabela_completa) > 2:
        setores = tabela_completa[0][1:]
        periodos = tabela_completa[1][1:]

        # Preencher setores e períodos faltantes
        for i in range(len(periodos)):
            if i >= len(setores):
                setores.append("Setor Desconhecido")
            if not setores[i]:
                setores[i] = setores[i - 1] if i > 0 else "Setor Desconhecido"
            if not periodos[i]:
                periodos[i] = periodos[i - 1] if i > 0 else "Período Desconhecido"

        colunas = list(zip(setores, periodos))

        registros = []
        for linha in tabela_completa[2:]:
            if not linha or not linha[0]:
                continue
            data = linha[0]
            nomes = linha[1:]

            for i, nome in enumerate(nomes):
                if i >= len(colunas):
                    continue
                if not nome:
                    continue
                if nome_funcionario.lower() in nome.lower():
                    setor, periodo = colunas[i] if i < len(colunas) else ("Setor Desconhecido", "Período Desconhecido")
                    setor = setor or "Setor Desconhecido"
                    periodo = periodo or "Período Desconhecido"
                    registros.append({
                        "Data": data,
                        "Período": periodo,
                        "Setor": setor
                    })

        if registros:
            df_resultado = pd.DataFrame(registros)
            st.success(f"📌 Escala de: **{nome_funcionario.title()}**")
            st.dataframe(df_resultado)

            pdf_gerado = gerar_pdf(df_resultado, nome_funcionario)
            st.download_button(
                "📥 Baixar PDF da escala",
                data=pdf_gerado,
                file_name=f"escala_{nome_funcionario.lower()}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("⚠️ Funcionário não encontrado na escala.")
    else:
        st.error("❌ Não foi possível extrair a tabela do PDF. Verifique o layout.")
