import streamlit as st
import pdfplumber
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="Escala de Funcionários", layout="centered")
st.title("📅 Escala Individual por Funcionário")

uploaded_file = st.file_uploader("📄 Faça upload do PDF da escala geral", type="pdf")
nome_funcionario = st.text_input("👤 Nome do funcionário para filtrar")

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
        if "-mai" in linha:  # pega linhas como "1-mai." ou "2-mai"
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
        st.success(f"📌 Escala de: **{nome_funcionario.title()}**")
        st.dataframe(df)

        # Função de geração de PDF com fpdf2
        def gerar_pdf(df, nome):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=14)
            pdf.cell(0, 10, f"Escala da {nome.title()} – Maio 2025", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", size=12)

            for _, row in df.iterrows():
                data = str(row['Data'])
                periodo = str(row['Período'])
                setor = str(row['Setor'])
                linha = f"{data} - {periodo} - {setor}"
                # Garante que não quebre o PDF com caracteres inválidos
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
