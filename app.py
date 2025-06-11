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
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    titulo = f"Escala da {nome.title()} - Maio 2025"
    titulo_seguro = titulo.encode("latin-1", "replace").decode("latin-1")
    pdf.cell(0, 10, titulo_seguro, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for _, row in df.iterrows():
        linha = f"{row['Data']} - {row['Período']} - {row['Setor']}"
        linha_segura = linha.encode("latin-1", "replace").decode("latin-1")
        pdf.cell(0, 10, linha_segura, ln=True)
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
        # Primeiras duas linhas = cabeçalho (setores e períodos)
        setores = tabela_completa[0][1:]  # ignorando primeira célula vazia (canto superior esquerdo)
        periodos = tabela_completa[1][1:]

        colunas = list(zip(setores, periodos))  # [(Setor, Período)]
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
