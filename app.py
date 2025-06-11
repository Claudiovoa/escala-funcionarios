import streamlit as st
import pdfplumber
import pandas as pd
from fpdf import FPDF
import io

st.title("📅 Escala Individual por Funcionário")

uploaded_file = st.file_uploader("Faça upload do PDF da escala geral", type="pdf")
nome_funcionario = st.text_input("Nome do funcionário para filtrar")

if uploaded_file and nome_funcionario:
    with pdfplumber.open(uploaded_file) as pdf:
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text()

    # Separar as linhas e processar
    linhas = texto.split("\n")
    escalas = []
    setores = [
        "ENF B", "ENF D", "ENF E", "TRR", "UTI 1", "UTI 2", "UTI 3", "UTI 4", "UTI 5", "UTI6", 
        "PS", "UCP", "AMB", "CTQ ENF", "CTQ UTQ", "TMO", "PLETISMO"
    ]
    periodos = ["MANHÃ", "TARDE", "NOITE"]

    for linha in linhas:
        if "-mai." in linha or "-mai" in linha:
            partes = linha.split()
            if len(partes) > 1:
                data = partes[0]
                nomes = partes[1:]
                for i, nome in enumerate(nomes):
                    setor_index = i % len(setores)
                    periodo_index = (i // len(setores)) % 3
                    if nome_funcionario.lower() in nome.lower():
                        escalas.append({
                            "Data": data,
                            "Período": periodos[periodo_index],
                            "Setor": setores[setor_index]
                        })

    if escalas:
        df = pd.DataFrame(escalas)
        st.success(f"Escala de: **{nome_funcionario.title()}**")
        st.dataframe(df)

        def gerar_pdf(df, nome):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"Escala da {nome.title()} – Maio 2025", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            for _, row in df.iterrows():
                linha = f"{row['Data']} — {row['Período']} — {row['Setor']}"
                pdf.cell(0, 10, linha, ln=True)
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
        st.warning("Funcionário não encontrado na escala.")

