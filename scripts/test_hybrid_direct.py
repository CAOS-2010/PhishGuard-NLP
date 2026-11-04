"""
Test directo del scoring hibrido sin pasar por el servidor API.
Simula exactamente la logica de analysis.py con la configuracion actual.
"""
import sys
sys.path.insert(0, r"D:\SEMESTRE 10\TRABAJO DE GRADO 2\PhishGuard-NLP")

import numpy as np
from src.core.classifier import PhishingClassifier, _risk_level
from src.core.explainer import explain
from src.core.preprocessor import preprocess
from src.core.url_analyzer import analyze_urls
from config.settings import RISK_LOW, DECISION_THRESHOLD

clf = PhishingClassifier()

def _hybrid_score(ml_prob, social_score, url_count, urgency_count):
    xai_score = (
        0.40 * social_score
        + 0.35 * min(url_count / 2.0, 1.0)
        + 0.25 * min(urgency_count / 10.0, 1.0)
    )
    return round(0.35 * ml_prob + 0.65 * xai_score, 4)

def analyze_local(subject, text, sender=""):
    full_text = f"{subject} {text}".strip()
    processed = preprocess(full_text)
    result = clf.predict(processed)

    vectorizer = clf.get_vectorizer()
    fi = None
    inner = clf._pipeline.named_steps["clf"]
    if hasattr(inner, "feature_importances_"):
        fi = inner.feature_importances_

    xai = explain(full_text, preprocess(full_text), vectorizer, fi)
    url_report = analyze_urls(full_text)

    url_count = url_report.total_urls
    urgency_count = len(xai.urgency_keywords_found)

    _HIGH_VALUE_KWS = {
        "datos bancarios", "formulario adjunto", "copia de cedula", "copia de cédula",
        "numero de cuenta", "número de cuenta", "formulario con sus datos",
    }
    ml_uncertain = result.confidence < DECISION_THRESHOLD
    xai_strong = xai.social_engineering_score >= 0.5 and (url_count > 0 or urgency_count >= 4)
    urgency_alone = urgency_count >= 6 and xai.social_engineering_score >= 0.4
    url_high_risk = url_report.high_risk_urls > 0 and url_report.url_risk_score >= 0.45
    ml_suspicious_with_signals = result.confidence >= 0.55 and urgency_count >= 2
    data_harvesting = (
        result.confidence >= RISK_LOW
        and any(kw in _HIGH_VALUE_KWS for kw in xai.urgency_keywords_found)
        and urgency_count >= 2
    )

    label = result.label
    confidence = result.confidence

    if data_harvesting and not (xai_strong or urgency_alone or url_high_risk or ml_suspicious_with_signals):
        label = "phishing"
    elif ml_uncertain and (xai_strong or urgency_alone or url_high_risk or ml_suspicious_with_signals):
        hybrid = _hybrid_score(result.confidence, xai.social_engineering_score, url_count, urgency_count)
        if url_high_risk:
            hybrid = min(hybrid + url_report.url_risk_score * 0.30, 0.99)
        confidence = round(hybrid, 4)
        label = "phishing" if confidence >= RISK_LOW else "seguro"

    triggered = (
        (data_harvesting and not (xai_strong or urgency_alone or url_high_risk or ml_suspicious_with_signals))
        or (ml_uncertain and (xai_strong or urgency_alone or url_high_risk or ml_suspicious_with_signals))
    )
    return {
        "label": label,
        "confidence": confidence,
        "ml_confidence": result.confidence,
        "social_score": xai.social_engineering_score,
        "urgency_count": urgency_count,
        "urgency_words": xai.urgency_keywords_found,
        "url_count": url_count,
        "hybrid_triggered": triggered,
    }


tests = [
    # --- Phishing ---
    ("ESTAFA FINANCIERA", "Transferencia de herencia pendiente",
     "Estimado beneficiario, le informamos que ha sido seleccionado para recibir CINCO MILLONES DE DOLARES como parte de la herencia del difunto empresario fallecido. Para procesar la transferencia necesitamos sus datos bancarios completos incluyendo numero de cuenta y clave de acceso. Responda urgentemente antes de que el plazo venza manana.",
     "phishing"),
    ("SUPLANTACION DIAN", "URGENTE: Inconsistencias en declaracion de renta",
     "DIRECCION DE IMPUESTOS Y ADUANAS NACIONALES DIAN. Su empresa figura con inconsistencias en la declaracion de renta del ano gravable 2023. Se ha iniciado proceso de fiscalizacion que puede resultar en sancion de 12500000 pesos. Para evitar sanciones debe actualizar su RUT e ingresar clave tributaria en dian.gov.co.verificacion-urgente.net urgentemente.",
     "phishing"),
    ("INGENIERIA SOCIAL TRABAJO", "Oferta laboral - Analista de Datos - Salario 8.5M",
     "Estimado candidato, tras revisar su perfil en LinkedIn hemos decidido contactarle para ofrecerle vacante como Analista de Datos con salario de 8500000 pesos mensuales mas beneficios. Para continuar el proceso de seleccion necesitamos que complete el formulario adjunto con sus datos bancarios y suba copia de su cedula de ciudadania.",
     "phishing"),
    ("BANCARIO CLASICO", "URGENTE: Cuenta bloqueada - Verificacion requerida",
     "Estimado cliente Bancolombia, su cuenta ha sido temporalmente bloqueada por seguridad. Para restablecer el acceso ingrese AHORA a bancolombia-seguro.co y confirme su clave de acceso. Si no verifica en 24 horas perdera acceso permanentemente a su cuenta.",
     "phishing"),
    ("SOPORTE TECNICO FALSO", "MICROSOFT SUPPORT ALERT",
     "MICROSOFT TECHNICAL SUPPORT ALERT. Your Windows license has expired and your computer is at risk of serious damage. Call our toll-free number immediately 1-800-555-0199 to renew your license and remove detected viruses. Do not turn off your computer.",
     "phishing"),
    ("ROBO CREDENCIALES TDEA", "Cuenta comprometida - Verificacion urgente",
     "Estimado estudiante su cuenta de correo institucional del TDEA ha sido comprometida. Debe verificar su identidad AHORA MISMO haciendo clic en el enlace adjunto e ingresando su usuario y contrasena institucional. Si no verifica en 2 horas su cuenta sera eliminada permanentemente del sistema.",
     "phishing"),
    ("SUPLANTACION MICROSOFT", "URGENT: Account suspended",
     "URGENT NOTICE: Your Microsoft account access.verify-microsoft-login.net has been suspended due to suspicious activity. Click here immediately to verify your identity and restore access to your Office 365. Failure to act within 24 hours will result in permanent account deletion.",
     "phishing"),
    # --- Seguros ---
    ("CORREO SEGURO BANCO", "Su extracto bancario esta disponible",
     "Estimado cliente, le informamos que su extracto bancario del mes de octubre esta disponible en la sucursal virtual. Para consultarlo acceda a nuestra pagina oficial con sus credenciales habituales. Comuniquese al 018000912345 si tiene dudas.",
     "seguro"),
    ("CORREO SEGURO TDEA PAGO MATRICULA", "Orden de Matricula - Pago inmediato",
     "Cordial saludo. Te informamos que tu Orden de Matricula ha sido actualizada en el Sistema Campus con fecha de pago inmediato. El plazo se ha agotado y las clases ya inician, por lo que le solicitamos realizar el pago de inmediato a traves de su plataforma Campus para evitar la anulacion de su liquidacion. Ingresa al Sistema Campus con tu usuario y contrasena. Haz clic en el icono de la impresora para descargar la orden. Medios de pago: PSE, Tarjeta de Credito Visa o MasterCard, Banco Popular o Davivienda. No se aceptan transferencias directas a cuentas del TdeA.",
     "seguro"),
    ("CORREO SEGURO INST", "Inicio periodo de matriculas 2025-1",
     "Estimado estudiante, le recordamos que el periodo de matriculas para el semestre 2025-1 inicia el 15 de enero. Consulte el calendario academico en el portal estudiantil con su usuario y contrasena institucional. Comuniquese con la oficina de registro si tiene inquietudes.",
     "seguro"),
    ("CORREO SEGURO MICROSOFT REAL", "Microsoft 365 subscription renewed",
     "Dear user, your Microsoft 365 subscription has been renewed successfully. Your next billing date is December 1 2024. To manage your subscription visit account.microsoft.com. Contact our support team if you have any questions about your account.",
     "seguro"),
]

print("Resultados - scoring hibrido con deteccion contextual:")
print("-" * 95)
ok_count = 0
for name, subject, text, expected in tests:
    r = analyze_local(subject, text)
    label = r["label"]
    conf = r["confidence"]
    is_ok = (label == expected)
    ok_count += is_ok
    status = "OK  " if is_ok else "FALLO"
    hybrid_mark = "[HYB]" if r["hybrid_triggered"] else "     "
    print(f"{status} {hybrid_mark} {name:<35} {label:<10} {conf:.1%}  ML:{r['ml_confidence']:.1%} social:{r['social_score']:.2f} urg:{r['urgency_count']}")
    if not is_ok:
        print(f"       urgency_words: {r['urgency_words']}")

print(f"\nTotal: {ok_count}/{len(tests)} correctos ({ok_count/len(tests):.0%})")
