import streamlit as st
import pdfplumber
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="Escala de Funcionários", layout="wide")
st.title("📅 Escala Individual por Funcionário")

uploaded_file = st.file_uploader("📄 Faça upload do PDF da escala geral", type="pdf")
nome_funcionario = st.text_input("👤 Nome do funcionário para filtrar")

if uploaded_file and nome_funcionario:
    with pdfplumber.open(uploaded_file) as pdf:
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text()

    linhas = texto.split("\n")
    
    # Pegamos as 2 primeiras linhas como cabeçalho real
    linha_setores = linhas[0].strip().split()
    linha_periodos = linhas[1].strip().split()

    colunas = list(zip(linha_setores, linha_periodos))  # (setor, período) por coluna
    dados = linhas[2:]  # a partir da linha 3 são os dias com os nomes

    registros = []

    for linha in dados:
        partes = linha.strip().split()
        if len(partes) < 2:
            continue
        data = partes[0]
        nomes = partes[1:]

        for i, nome in enumerate(nomes):
            if i >= len(colunas):
                break
            setor, periodo = colunas[i]
            if nome_funcionario.lower() in nome.lower():
                registros.append({
                    "Data": data,
                    "Período": periodo.capitalize(),
                    "Setor": setor
                })

    if registros:
        df = pd.DataFrame(registros)
        st.success(f"📌 Escala de: **{nome_funcionario.title()}**")
        st.dataframe(df)

        # Gerar PDF usando fpdf2
        def gerar_pdf(df, nome):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=14)
            pdf.cell(0, 10, f"Escala da {nome.title()} – Maio 2025", ln=True, align="C")
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

        pdf_gerado = gerar_pdf(df, nome_funcionario)
        st.download_button(
            "📥 Baixar PDF da escala",
            data=pdf_gerado,
            file_name=f"escala_{nome_funcionario.lower()}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("⚠️ Funcionário não encontrado na escala.")
