
import os
import joblib
import streamlit as st
from analyzers.ocr_analyzer import DEFAULT_OCR_LANG, extract_text_from_image
from analyzers.pdf_analyzer import DEFAULT_PDF_OCR_LANG, extract_text_from_pdf
from analyzers.url_analyzer import analyze_url
from analyzers.text_analyzer import analyze_text
from scoring.risk_score import combine_scores
from reports.report_generator import generate_report

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(BASE_DIR, "models", "phishguard_baseline.joblib")

@st.cache_resource
def _load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


st.set_page_config(page_title="PhishGuard AI", page_icon="🛡️", layout="centered")

st.title("PhishGuard AI")
st.write("Detector educativo de phishing para URLs y texto.")

url_input = st.text_input("URL a analizar", placeholder="https://ejemplo.com")
text_input = st.text_area("Texto del mensaje o correo", height=200)
image_input = st.file_uploader("Pantallazo (png/jpg)", type=["png", "jpg", "jpeg", "webp"])
pdf_max_pages = st.number_input(
    "Maximo de paginas PDF",
    min_value=1,
    max_value=50,
    value=10,
    step=1,
)
pdf_input = st.file_uploader("PDF", type=["pdf"])

if st.button("Analizar"):
    ocr_text = ""
    ocr_error = None
    pdf_result = None

    if image_input is not None:
        ocr_text, ocr_error = extract_text_from_image(image_input, lang=DEFAULT_OCR_LANG)
        if ocr_error:
            st.error(ocr_error)

    if pdf_input is not None:
        pdf_result = extract_text_from_pdf(
            pdf_input,
            max_pages=int(pdf_max_pages),
            ocr_enabled=True,
            lang=DEFAULT_PDF_OCR_LANG,
        )
        if pdf_result.get("error"):
            st.error(pdf_result["error"])
        for warning in pdf_result.get("warnings", []):
            st.warning(warning)

    combined_text = text_input.strip()
    if ocr_text:
        combined_text = f"{combined_text}\n{ocr_text}".strip()
    if pdf_result and pdf_result.get("text"):
        combined_text = f"{combined_text}\n{pdf_result['text']}".strip()

    if not url_input.strip() and not combined_text:
        st.warning("Ingresa una URL, texto, pantallazo o PDF para analizar.")
    else:
        url_result = analyze_url(url_input) if url_input.strip() else None
        text_result = analyze_text(combined_text) if combined_text else None

        risk_result = combine_scores(url_result, text_result)
        report = generate_report(url_result, text_result, risk_result)

        st.subheader(f"Riesgo: {report['risk_level']}")
        st.metric("Puntaje total", report["total_score"])

        if report["reasons"]:
            st.markdown("**Razones detectadas**")
            for reason in report["reasons"]:
                st.write(f"- {reason}")
        else:
            st.write("No se detectaron razones.")

        model = _load_model()
        if model:
            ml_text = f"{url_input} {combined_text}".strip()
            if ml_text:
                pred = model.predict([ml_text])[0]
                phishing_prob = None
                if hasattr(model, "predict_proba"):
                    try:
                        classes = list(model.classes_)
                        proba = model.predict_proba([ml_text])[0]
                        if "phishing" in classes:
                            phishing_prob = proba[classes.index("phishing")]
                        else:
                            phishing_prob = max(proba)
                    except Exception:
                        phishing_prob = None

                st.subheader("Resultado ML (baseline)")
                st.write(f"Prediccion: {pred}")
                if phishing_prob is not None:
                    st.write(f"Probabilidad de phishing: {phishing_prob:.2f}")
            else:
                st.info("Modelo ML disponible, pero no hay texto o URL para predecir.")
        else:
            st.info("Modelo ML no encontrado. Entrena el baseline para habilitarlo.")

        if report["url"]:
            with st.expander("Detalle URL"):
                st.write(f"URL normalizada: {report['url']['normalized_url']}")
                st.write(f"Host: {report['url']['host']}")
                st.write(f"Puntaje URL: {report['url']['score']}")
                hit_signals = [s for s in report["url"]["signals"] if s.get("hit")]
                if hit_signals:
                    st.write("Senales detectadas:")
                    for s in hit_signals:
                        st.write(f"- {s['reason']} (peso {s['weight']})")

        if report["text"]:
            with st.expander("Detalle texto"):
                st.write(f"Puntaje texto: {report['text']['score']}")
                st.write(f"Longitud: {report['text']['text_length']} caracteres")
                if report["text"]["urls"]:
                    st.write("URLs encontradas:")
                    for u in report["text"]["urls"]:
                        st.write(f"- {u}")
                hit_signals = [s for s in report["text"]["signals"] if s.get("hit")]
                if hit_signals:
                    st.write("Senales detectadas:")
                    for s in hit_signals:
                        st.write(f"- {s['reason']} (peso {s['weight']})")

        if ocr_text:
            with st.expander("Texto extraido del pantallazo"):
                st.write(ocr_text)

        if pdf_result and pdf_result.get("text"):
            with st.expander("Texto extraido del PDF"):
                if pdf_result.get("pages_total"):
                    st.write(
                        f"Paginas procesadas: {pdf_result['pages_processed']} de {pdf_result['pages_total']}"
                    )
                st.write(pdf_result["text"])