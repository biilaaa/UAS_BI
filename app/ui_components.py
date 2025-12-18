import datetime
import os

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from data_governance import readable_feature_name, FEATURE_METADATA


def show_header() -> None:
    st.markdown(
        """
        <div style="text-align:center; margin-bottom: 1.5rem;">
            <h1 style="margin-bottom:0;">💖 Prediksi Penyakit Jantung</h1>
            <p style="color:#555; margin-top:4px;">
                Dashboard Machine Learning — Logistic Regression & Random Forest
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_result_card(pred_lr: int, pred_rf: int) -> None:
    label_lr = "Berisiko" if pred_lr == 1 else "Tidak Berisiko"
    label_rf = "Berisiko" if pred_rf == 1 else "Tidak Berisiko"

    bg_color = "#ffe5e5" if pred_rf == 1 else "#e7ffe9"
    border_color = "#ff4b4b" if pred_rf == 1 else "#2e7d32"
    text_color = "#b71c1c" if pred_rf == 1 else "#1b5e20"

    st.markdown(
        f"""
        <div style="
            border-radius: 14px;
            border: 1px solid {border_color};
            background: {bg_color};
            padding: 1rem 1.3rem;
            margin-top: 0.8rem;
            margin-bottom: 1.2rem;
        ">
            <h4 style="margin: 0 0 0.5rem 0; color:{text_color};">
                🧾 Ringkasan Prediksi
            </h4>
            <ul style="margin:0; padding-left: 1.2rem; color:#222;">
                <li>Logistic Regression: <b>{label_lr}</b> (kelas = {int(pred_lr)})</li>
                <li>Random Forest: <b>{label_rf}</b> (kelas = {int(pred_rf)})</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

def export_pdf(input_data, pred_lr, pred_rf, prob_rf=None):

    file_path = "laporan_prediksi_jantung.pdf"

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=1,
        textColor=colors.HexColor("#1a237e"),
        fontSize=20,
        spaceAfter=20,
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#0d47a1"),
        fontSize=14,
        spaceBefore=10,
        spaceAfter=10,
    )

    normal = styles["BodyText"]
    elements = []

    elements.append(Paragraph("💖 Laporan Prediksi Penyakit Jantung", title_style))
    elements.append(
        Paragraph(
            f"Tanggal: {datetime.datetime.now().strftime('%d %B %Y, %H:%M')}",
            normal,
        )
    )
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("📌 Data Pasien", section_style))

    table_data = [["Fitur", "Nilai"]]

    for col in input_data.columns:
        raw_val = input_data[col].iloc[0]

        human_label = readable_feature_name(col)

        # Format nilai
        if col == "gender":
            display_val = "male" if raw_val == 1 else "female"
        else:
            rules = FEATURE_METADATA.get(col)
            display_val = raw_val

            if rules and rules.get("type") == "int":
                try:
                    display_val = int(raw_val)
                except:
                    pass

            elif rules and rules.get("type") == "float":
                try:
                    f = float(raw_val)
                    display_val = str(int(f)) if f.is_integer() else f"{f:.2f}"
                except:
                    pass

        table_data.append([human_label, str(display_val)])

    table = Table(table_data, colWidths=[8 * cm, 6 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#bbdefb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("📈 Hasil Prediksi Model", section_style))

    label_lr = "Berisiko" if pred_lr == 1 else "Tidak Berisiko"
    label_rf = "Berisiko" if pred_rf == 1 else "Tidak Berisiko"

    results_text = f"""
    <b>Logistic Regression:</b> {label_lr} (kelas {pred_lr})<br/>
    <b>Random Forest:</b> {label_rf} (kelas {pred_rf})<br/>
    """

    elements.append(Paragraph(results_text, normal))
    elements.append(Spacer(1, 12))

    if prob_rf is not None:
        elements.append(
            Paragraph("🔢 Probabilitas Risiko", section_style)
        )

        prob_text = f"""
        <b>Tidak Berisiko:</b> {prob_rf[0] * 100:.1f}%<br/>
        <b>Berisiko:</b> {prob_rf[1] * 100:.1f}%<br/>
        """
        elements.append(Paragraph(prob_text, normal))
        elements.append(Spacer(1, 12))


    elements.append(Paragraph("📝 Kesimpulan", section_style))

    conclusion = (
        "Hasil prediksi menunjukkan bahwa pasien memiliki <b>RISIKO TINGGI</b> penyakit jantung."
        if pred_rf == 1
        else "Hasil prediksi menunjukkan bahwa pasien <b>TIDAK memiliki risiko signifikan</b> penyakit jantung."
    )

    elements.append(Paragraph(conclusion, normal))
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "<i>Laporan ini dihasilkan otomatis oleh sistem analisis machine learning.</i>",
            ParagraphStyle("FooterStyle", alignment=1, fontSize=9, textColor=colors.grey),
        )
    )

    doc.build(elements)

    return os.path.abspath(file_path)
