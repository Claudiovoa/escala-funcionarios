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

    linhas = texto.strip().split("\n")

    # Linhas 1 e 2 são cabeçalhos: setores e períodos
    setores = linhas[0].strip().split()
    periodos = linhas[1].strip().split()
    colunas = list(zip(setores, periodos))  # [(Setor, Período), ...]

    dados = []

    # A partir da linha 3 são os dias + escalas
    for linha in linhas[2:]:
        partes = linha.strip().split()
        if len(partes) < 2:
            continue
        data = partes[0]
        nomes = partes[1:]

        for i, nome in enumerate(nomes):
            if i >= len(colunas):
                break
            setor, periodo = colunas[i]
            dados.append({
                "Data": data,
                "Período": periodo,
                "Setor": setor,
                "Nome": nome
            })

    df_total = pd.DataFrame(dados)

    # Filtra o nome desejado
    df_filtrado = df_total[df_total["Nome"].str.lower().str.contains(nome_funcionario.lower())]

    if not df_filtrado.empty:
        df_resultado = df_filtrado[["Data", "Período", "Setor"]].sort_values(by="Data")
        st.success(f"📌 Escala de: **{nome_funcionario.title()}**")
        st.dataframe(df_resultado)

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

        pdf_gerado = gerar_pdf(df_resultado, nome_funcionario)
        st.download_button(
            "📥 Baixar PDF da escala",
            data=pdf_gerado,
            file_name=f"escala_{nome_funcionario.lower()}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("⚠️ Funcionário não encontrado na escala.")
