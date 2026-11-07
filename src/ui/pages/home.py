from __future__ import annotations
from pathlib import Path
import httpx
import plotly.graph_objects as go
import streamlit as st
from config.settings import API_BASE_URL

_RC = {"alto":"#EF4444","medio":"#F59E0B","bajo":"#22C55E"}
_RB = {"alto":"#FEF2F2","medio":"#FFFBEB","bajo":"#F0FDF4"}


def render() -> None:
    # ── Estado: ejecutar llamada a API (pantalla de carga activa) ─────────────
    if st.session_state.get("_loading"):
        _show_loading()
        _execute_api()
        return

    result = st.session_state.get("last_result")

    # ── Entrada centrada ───────────────────────────────────────────────────────
    _, c_entrada, _ = st.columns([0.8, 2.4, 0.8], gap="small")

    with c_entrada:
        st.markdown('<div class="sec-title">Entrada</div>', unsafe_allow_html=True)

        tab_t, tab_f = st.tabs(["  TEXTO  ", "  ARCHIVO  "])

        with tab_t:
            st.markdown("<br>", unsafe_allow_html=True)
            sender  = st.text_input("Remitente", placeholder="banco@ejemplo.com", key="inp_sender")
            subject = st.text_input("Asunto", placeholder="Alerta: cuenta bloqueada", key="inp_subject")
            body    = st.text_area("Cuerpo del correo", height=200,
                                   placeholder="Pegue aquí el correo sospechoso...", key="inp_body")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("ANALIZAR", type="primary", use_container_width=True, key="btn_txt"):
                if body.strip():
                    st.session_state["_pending"] = {"text": body, "subject": subject, "sender": sender}
                    st.session_state["_loading"] = True
                    st.session_state["last_result"] = None
                    st.session_state["last_analyzed_text"] = f"{subject} {body}".strip()
                    st.rerun()
                else:
                    st.warning("Ingresa el cuerpo del correo.")

        with tab_f:
            st.markdown("<br>", unsafe_allow_html=True)
            uploads = st.file_uploader(
                "Archivos .eml o .msg", type=["eml", "msg"],
                label_visibility="collapsed", accept_multiple_files=True,
            )

            files_data: list = []
            if uploads:
                from src.data.parser import parse_file
                for up in uploads:
                    tmp = Path("data/raw") / up.name
                    tmp.parent.mkdir(parents=True, exist_ok=True)
                    tmp.write_bytes(up.read())
                    try:
                        parsed = parse_file(tmp)
                    except Exception:
                        continue
                    files_data.append((up.name, parsed))
                    st.markdown(
                        f'<div style="background:#D0D0D0;border-radius:6px;padding:8px 12px;'
                        f'border-left:3px solid #F5C518;font-size:12px;margin:6px 0;'
                        f'display:flex;justify-content:space-between;align-items:center">'
                        f'<b>{up.name}</b>'
                        f'<span style="color:#888;font-size:11px">{parsed.sender or "Sin remitente"}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            if files_data:
                st.markdown("<br>", unsafe_allow_html=True)
                n = len(files_data)
                btn_lbl = f"ANALIZAR {n} ARCHIVO{'S' if n > 1 else ''}"
                if st.button(btn_lbl, type="primary", use_container_width=True, key="btn_arch"):
                    new_batch: list = []
                    prog = st.progress(0, text="Procesando archivos...")
                    for idx, (fname, pf) in enumerate(files_data):
                        try:
                            r = httpx.post(
                                f"{API_BASE_URL}/analyze/",
                                json={
                                    "text": pf.body,
                                    "subject": pf.subject or "",
                                    "sender": pf.sender or "",
                                },
                                timeout=30.0,
                            )
                            r.raise_for_status()
                            new_batch.append({
                                "filename": fname,
                                "subject": pf.subject or "",
                                "sender": pf.sender or "",
                                "analyzed_text": f"{pf.subject or ''} {pf.body}".strip(),
                                "result": r.json(),
                            })
                        except Exception as exc:
                            new_batch.append({
                                "filename": fname,
                                "subject": pf.subject or "",
                                "sender": pf.sender or "",
                                "analyzed_text": "",
                                "result": None,
                                "error": str(exc),
                            })
                        prog.progress((idx + 1) / len(files_data), text=f"{fname}...")
                    st.session_state["batch_results"] = new_batch
                    st.session_state["last_result"] = None
                    st.rerun()

            # ── Lista de resultados por archivo ────────────────────────────
            batch = st.session_state.get("batch_results") or []
            if batch:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="sec-title">Resultados del análisis</div>', unsafe_allow_html=True)
                for i, item in enumerate(batch):
                    res = item.get("result")
                    if res is None:
                        st.markdown(
                            f'<div style="background:#EBEBEB;border-radius:8px;padding:12px 16px;'
                            f'border-left:5px solid #EF4444;margin:6px 0">'
                            f'<span style="font-size:13px;font-weight:700;color:#111">'
                            f'{item["filename"]}</span>'
                            f'<span style="font-size:12px;color:#888;margin-left:10px">'
                            f'Error al analizar</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        continue

                    is_ph_i     = res["label"] == "phishing"
                    conf_i      = res["confidence"]
                    risk_i      = res["risk_level"]
                    rc_i        = _RC.get(risk_i, "#888")
                    badge_bg    = "#FEF2F2" if is_ph_i else "#F0FDF4"
                    badge_color = "#B91C1C" if is_ph_i else "#15803D"
                    badge_text  = "PHISHING" if is_ph_i else "SEGURO"

                    col_info, col_badge, col_btn = st.columns([4, 2, 2], gap="small")
                    with col_info:
                        st.markdown(
                            f'<div style="padding:10px 0">'
                            f'<div style="font-size:13px;font-weight:700;color:#111">'
                            f'{item["filename"]}</div>'
                            f'<div style="font-size:12px;color:#666;margin-top:2px">'
                            f'{item["sender"] or "Sin remitente"}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    with col_badge:
                        st.markdown(
                            f'<div style="padding:10px 0;text-align:center">'
                            f'<div style="background:{badge_bg};color:{badge_color};'
                            f'border:2px solid {rc_i};border-radius:8px;padding:8px;'
                            f'font-size:12px;font-weight:800;letter-spacing:1px">'
                            f'{badge_text}</div>'
                            f'<div style="font-size:11px;color:#888;margin-top:4px">'
                            f'{round(conf_i*100,1)}% confianza</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    with col_btn:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(
                            "Ver análisis completo",
                            type="primary",
                            use_container_width=True,
                            key=f"btn_view_batch_{i}",
                        ):
                            st.session_state["last_result"] = res
                            st.session_state["last_analyzed_text"] = item.get("analyzed_text", "")
                            _dialog_results()

                    st.markdown(
                        '<hr style="border:none;border-top:1px solid #C8C8C8;margin:4px 0">',
                        unsafe_allow_html=True,
                    )

        st.markdown('<div class="sec-sub">Historial reciente</div>', unsafe_allow_html=True)
        try:
            hist = httpx.get(f"{API_BASE_URL}/history/", params={"limit":5}, timeout=4.0).json()["records"]
            if hist:
                for r in hist:
                    is_ph = r["label"] == "phishing"
                    st.markdown(
                        f'<div class="hrow">'
                        f'<span class="hlbl">{r["subject"] or "Sin asunto"}</span>'
                        f'<span class="hbadge {"hph" if is_ph else "hsg"}">{"PHISH" if is_ph else "OK"}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<p style="font-size:11px;color:#AAA;margin:4px 0">Sin registros aún.</p>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<p style="font-size:11px;color:#AAA;margin:4px 0">API no disponible.</p>', unsafe_allow_html=True)

    # ── Botón re-abrir para análisis de texto (no para lote) ─────────────────
    if result and not st.session_state.get("batch_results"):
        _, c_btn, _ = st.columns([0.8, 2.4, 0.8])
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Ver análisis completo", type="primary", use_container_width=True):
                st.session_state["_open_dialog"] = True
                st.rerun()

    if st.session_state.pop("_open_dialog", False):
        _dialog_results()


def _show_loading() -> None:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            '<div style="text-align:center;padding:100px 0 80px">'
            '<div class="pg-spinner"></div>'
            '<div style="font-size:22px;font-weight:800;color:#1A1A1A;letter-spacing:1px;'
            'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',system-ui,sans-serif">'
            'Analizando...</div>'
            '<div style="font-size:13px;color:#AAAAAA;margin-top:10px;font-weight:500">'
            'El modelo está procesando el correo</div>'
            '</div>',
            unsafe_allow_html=True,
        )


def _execute_api() -> None:
    pending = st.session_state.pop("_pending", {})
    st.session_state["_loading"] = False
    try:
        r = httpx.post(
            f"{API_BASE_URL}/analyze/",
            json={"text": pending.get("text",""), "subject": pending.get("subject",""), "sender": pending.get("sender","")},
            timeout=30.0,
        )
        r.raise_for_status()
        st.session_state["last_result"] = r.json()
        st.session_state["_open_dialog"] = True
    except httpx.ConnectError:
        st.session_state["last_result"] = None
        st.error("No se pudo conectar con la API.")
    except httpx.HTTPStatusError as exc:
        st.session_state["last_result"] = None
        st.error(f"Error {exc.response.status_code}")
    st.rerun()


@st.dialog("Resultado del análisis", width="large")
def _dialog_results() -> None:
    result = st.session_state.get("last_result")
    if result:
        _show_results(result)


def _check_retrain_banner() -> None:
    if not st.session_state.get("_retraining"):
        return
    try:
        status = httpx.get(f"{API_BASE_URL}/feedback/retrain-status", timeout=3.0).json()
        if status.get("is_training"):
            st.markdown(
                '<div style="background:#1A2A1A;border-left:5px solid #22C55E;border-radius:0 8px 8px 0;'
                'padding:12px 18px;margin-bottom:16px;font-size:13px;color:#22C55E;font-weight:600">'
                'El modelo esta aprendiendo de tu correccion... (~60s)'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.session_state["_retraining"] = False
            if status.get("last_trained_at"):
                st.success(f"Modelo actualizado correctamente.")
    except Exception:
        pass


def _h2(text: str) -> str:
    return (
        f'<div style="font-size:20px;font-weight:900;color:#111111;margin:24px 0 12px;'
        f'border-bottom:2px solid #E5E5E5;padding-bottom:8px;'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif">{text}</div>'
    )


def _show_decision_process(result: dict, final_conf: float, is_ph: bool) -> None:
    df = result.get("decision_factors", {})
    if not df:
        return

    ml_conf    = round(df.get("ml_confidence", final_conf) * 100, 1)
    hybrid     = df.get("hybrid_triggered", False)
    harvesting = df.get("data_harvesting_triggered", False)
    social     = round(df.get("xai_social_score", 0) * 100)
    urg_count  = df.get("urgency_count", 0)
    url_count  = df.get("url_count", 0)

    xai        = result.get("explainability", {})
    kws        = xai.get("urgency_keywords_found", [])
    features   = xai.get("top_phishing_features", [])
    top_words  = [f["word"] for f in features[:5]] if features else []
    url_risk   = round(df.get("url_risk_score", 0) * 100)

    kws_str   = ", ".join(f'"{k}"' for k in kws[:5]) if kws else None
    words_str = ", ".join(f'"{w}"' for w in top_words) if top_words else None

    if hybrid:
        route_color = "#D97706"
        parts = [
            f"El modelo de inteligencia artificial analizó el contenido del correo y obtuvo una probabilidad inicial de {ml_conf}% de ser phishing, "
            f"un valor que se encuentra en zona de incertidumbre (entre 35% y 70%) y no era suficiente para tomar una decisión definitiva por sí solo."
        ]
        if words_str:
            parts.append(f"Las palabras que más activaron las alertas del modelo fueron: {words_str}.")
        if kws_str:
            parts.append(f"Además, se identificaron {urg_count} palabra{'s' if urg_count != 1 else ''} de presión psicológica: {kws_str}, que son términos frecuentemente usados para generar urgencia y manipular al lector.")
        if social > 0:
            parts.append(f"El análisis de manipulación social detectó un {social}% de patrones de ingeniería social, lo que indica que el correo intenta influir en el comportamiento del usuario.")
        if url_count > 0:
            parts.append(f"Se encontraron {url_count} enlace{'s' if url_count != 1 else ''} en el correo con un nivel de riesgo combinado del {url_risk}%.")
        parts.append(
            f"Al combinar todos estos factores mediante el sistema de scoring híbrido, la confianza final se elevó a {round(final_conf*100,1)}%, "
            f"lo que lleva al sistema a clasificar este correo como {'phishing' if is_ph else 'seguro'}."
        )
        route_desc = " ".join(parts)

    elif harvesting:
        route_color = "#DC2626"
        parts = [
            f"El modelo detectó una probabilidad de {ml_conf}% de phishing en el texto del correo."
        ]
        if words_str:
            parts.append(f"Entre las palabras con mayor peso en la decisión se encuentran: {words_str}.")
        parts.append(
            "Sin embargo, lo que determinó la clasificación final fue que el correo contiene solicitudes explícitas de información altamente sensible: "
            "datos bancarios, formularios con información personal o copia de cédula de ciudadanía."
        )
        parts.append(
            "Este tipo de solicitud directa de datos críticos es un patrón casi exclusivo de correos fraudulentos. "
            "Los bancos y entidades legítimas nunca solicitan este tipo de información por correo electrónico. "
            "Por esta razón, el sistema lo clasifica como phishing independientemente del porcentaje inicial del modelo."
        )
        route_desc = " ".join(parts)

    else:
        route_color = "#15803D" if not is_ph else "#DC2626"
        parts = [
            f"El modelo de inteligencia artificial analizó el texto completo del correo y determinó con {'alta' if final_conf >= 0.7 else 'moderada'} certeza "
            f"({ml_conf}%) que se trata de un correo {'fraudulento' if is_ph else 'legítimo'}."
        ]
        if words_str and is_ph:
            parts.append(f"Las palabras que más contribuyeron a esta clasificación fueron: {words_str}, términos que el modelo aprendió a asociar con patrones de phishing durante su entrenamiento.")
        elif words_str and not is_ph:
            parts.append(f"Aunque el correo contiene términos como {words_str}, el contexto en que aparecen es consistente con comunicaciones institucionales legítimas.")
        if kws_str and is_ph:
            parts.append(f"Se detectaron {urg_count} palabra{'s' if urg_count != 1 else ''} de presión: {kws_str}, usadas para generar urgencia artificial.")
        elif urg_count == 0 and not is_ph:
            parts.append("No se detectaron palabras de presión psicológica ni intentos de manipulación emocional.")
        if url_count == 0 and not is_ph:
            parts.append("No se encontraron enlaces sospechosos en el correo.")
        elif url_count > 0 and is_ph:
            parts.append(f"Se detectaron {url_count} enlace{'s' if url_count != 1 else ''} con un nivel de riesgo del {url_risk}%.")
        if not is_ph:
            parts.append("El análisis fue concluyente y no requirió combinar con señales adicionales.")
        else:
            parts.append("El resultado es concluyente y no requirió ajuste mediante el sistema híbrido.")
        route_desc = " ".join(parts)

    ml_color  = "#DC2626" if ml_conf >= 70 else ("#D97706" if ml_conf >= 35 else "#15803D")
    xai_color = "#D97706" if (social > 0 or urg_count > 0 or url_count > 0) else "#6B7280"
    fin_color = "#DC2626" if is_ph else "#15803D"

    # ── Sección 1: Proceso de decisión ────────────────────────────────────────
    st.markdown(_h2("1. ¿Cómo llegó el sistema a esta decisión?"), unsafe_allow_html=True)

    c1, ca1, c2, ca2, c3 = st.columns([5, 1, 5, 1, 5], gap="small")
    _card_style = "border-radius:12px;padding:18px 14px;text-align:center;border:2px solid {bc};background:{bg}"

    with c1:
        st.markdown(
            f'<div style="{_card_style.format(bc=ml_color, bg="#FFF8F8" if ml_conf>=70 else "#FFFBF0" if ml_conf>=35 else "#F0FFF4")}">'
            f'<div style="font-size:12px;font-weight:700;color:#555;margin-bottom:8px">PASO 1 · Análisis del texto</div>'
            f'<div style="font-size:32px;font-weight:900;color:{ml_color};line-height:1">{ml_conf}%</div>'
            f'<div style="font-size:12px;color:#666;margin-top:8px;line-height:1.4">'
            f'Probabilidad inicial basada en el texto del correo</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with ca1:
        st.markdown('<div style="text-align:center;font-size:28px;color:#999;padding-top:30px">→</div>', unsafe_allow_html=True)
    with c2:
        bg2 = "#FFFBF0" if (social > 0 or urg_count > 0 or url_count > 0) else "#F5F5F5"
        st.markdown(
            f'<div style="{_card_style.format(bc=xai_color, bg=bg2)}">'
            f'<div style="font-size:12px;font-weight:700;color:#555;margin-bottom:10px">PASO 2 · Señales de alerta</div>'
            f'<div style="display:flex;justify-content:center;gap:16px">'
            f'<div style="text-align:center">'
            f'<div style="font-size:26px;font-weight:900;color:{xai_color}">{urg_count}</div>'
            f'<div style="font-size:11px;color:#666;margin-top:4px">Palabras de<br>presión</div>'
            f'</div>'
            f'<div style="text-align:center">'
            f'<div style="font-size:26px;font-weight:900;color:{xai_color}">{social}%</div>'
            f'<div style="font-size:11px;color:#666;margin-top:4px">Manipulación<br>psicológica</div>'
            f'</div>'
            f'<div style="text-align:center">'
            f'<div style="font-size:26px;font-weight:900;color:{xai_color}">{url_count}</div>'
            f'<div style="font-size:11px;color:#666;margin-top:4px">Enlaces<br>detectados</div>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with ca2:
        st.markdown('<div style="text-align:center;font-size:28px;color:#999;padding-top:30px">→</div>', unsafe_allow_html=True)
    with c3:
        bg3 = "#FFF8F8" if is_ph else "#F0FFF4"
        st.markdown(
            f'<div style="{_card_style.format(bc=fin_color, bg=bg3)}">'
            f'<div style="font-size:12px;font-weight:700;color:#555;margin-bottom:8px">PASO 3 · Decisión final</div>'
            f'<div style="font-size:32px;font-weight:900;color:{fin_color};line-height:1">{round(final_conf*100,1)}%</div>'
            f'<div style="font-size:12px;color:#666;margin-top:8px;line-height:1.4">'
            f'Confianza final del sistema</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div style="background:#FAFAFA;border-left:5px solid {route_color};border-radius:0 10px 10px 0;'
        f'padding:14px 20px;margin:14px 0 8px;font-size:13px;color:#333;line-height:1.7">'
        f'<b style="color:{route_color};font-size:13px">Explicación:</b> {route_desc}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Sección 2: Peso de palabras ────────────────────────────────────────────
    features = result.get("explainability", {}).get("top_phishing_features", [])
    if features:
        st.markdown(_h2("2. Palabras que más influyeron en la clasificación"), unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:13px;color:#555;margin-bottom:12px">'
            'Las barras muestran cuánto peso tuvo cada palabra para determinar que el correo es phishing. '
            'A mayor barra, más determinante fue esa palabra.</p>',
            unsafe_allow_html=True,
        )
        words   = [f["word"] for f in features[:8]][::-1]
        weights = [round(f["weight"] * 100, 1) for f in features[:8]][::-1]
        colors  = ["#DC2626" if w > 25 else "#D97706" if w > 15 else "#4B5563" for w in weights]

        fig = go.Figure(go.Bar(
            x=weights, y=words, orientation="h",
            marker_color=colors,
            text=[f"{w}%" for w in weights],
            textposition="outside",
            textfont=dict(size=14, color="#111111", family="Arial Black"),
        ))
        fig.update_layout(
            height=280, margin=dict(t=10, b=10, l=10, r=70),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False, range=[0, max(weights) * 1.25]),
            yaxis=dict(tickfont=dict(size=14, color="#111111", family="Arial"), showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            '<p style="font-size:13px;color:#555;margin-top:-8px">'
            '<b style="color:#DC2626">■</b> Peso alto &nbsp;·&nbsp;'
            '<b style="color:#D97706">■</b> Peso medio &nbsp;·&nbsp;'
            '<b style="color:#4B5563">■</b> Peso bajo</p>',
            unsafe_allow_html=True,
        )


def _show_results(result: dict) -> None:
    _check_retrain_banner()
    label_val = result["label"]
    risk      = result["risk_level"]
    conf      = result["confidence"]
    is_ph     = label_val == "phishing"
    rc        = _RC.get(risk, "#888")
    rb        = _RB.get(risk, "#F5F5F5")
    xai       = result.get("explainability", {})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Aviso de incertidumbre ────────────────────────────────────────────────
    if conf < 0.55:
        st.markdown(
            '<div style="background:#2D2D00;border-left:5px solid #F5C518;border-radius:0 8px 8px 0;'
            'padding:14px 18px;margin-bottom:16px;font-size:13px;color:#F5C518;font-weight:600">'
            'El sistema no pudo determinar con certeza el tipo de este correo. '
            'Se recomienda precaucion independientemente del veredicto.'
            '</div>',
            unsafe_allow_html=True,
        )
    elif conf < 0.85:
        st.markdown(
            '<div style="background:#2D1F00;border-left:5px solid #F59E0B;border-radius:0 8px 8px 0;'
            'padding:14px 18px;margin-bottom:16px;font-size:13px;color:#F59E0B;font-weight:600">'
            'El sistema no esta completamente seguro de este resultado. '
            'Revisa el correo manualmente antes de interactuar con el.'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Veredicto grande centrado ─────────────────────────────────────────────
    verdict_bg     = "#FEF2F2" if is_ph else "#F0FDF4"
    verdict_color  = "#B91C1C" if is_ph else "#15803D"
    verdict_border = "#FECACA" if is_ph else "#86EFAC"
    verdict_text   = "CORREO INSEGURO" if is_ph else "CORREO SEGURO"
    verdict_icon   = ""

    st.markdown(
        f'<div style="background:{verdict_bg};border:3px solid {verdict_border};border-radius:14px;'
        f'text-align:center;padding:24px 0 18px;margin-bottom:24px">'
        f'<div style="font-size:38px;font-weight:900;color:{verdict_color};letter-spacing:2px;'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',system-ui,sans-serif">'
        f'{verdict_icon} {verdict_text}</div>'
        f'<div style="font-size:13px;color:{verdict_color};opacity:0.75;margin-top:8px;font-weight:600">'
        f'Confianza: {round(conf*100,1)}% &nbsp;·&nbsp; Riesgo: {risk.upper()}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Fila: metricas + gauge ────────────────────────────────────────────────
    c_metricas, c_gauge = st.columns([1, 1], gap="large")

    with c_metricas:
        st.markdown('<div class="sec-sub">Resumen del análisis</div>', unsafe_allow_html=True)
        ph_pct = round(conf*100,1) if is_ph else round((1-conf)*100,1)
        sg_pct = round((1-conf)*100,1) if is_ph else round(conf*100,1)
        for lbl, val, color in [
            ("Probabilidad phishing", ph_pct, "#EF4444" if is_ph else "#C0C0C0"),
            ("Probabilidad seguro",   sg_pct, "#22C55E" if not is_ph else "#C0C0C0"),
        ]:
            st.markdown(
                f'<div style="margin-bottom:10px">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:4px">'
                f'<span class="slbl">{lbl}</span>'
                f'<span style="font-size:13px;font-weight:900;color:{color}">{val}%</span>'
                f'</div>'
                f'<div class="bar-bg"><div class="bar-fill" style="background:{color};width:{val}%"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        kws = xai.get("urgency_keywords_found", [])
        if kws:
            st.markdown('<div class="sec-sub" style="margin-top:12px">Palabras de presión detectadas</div>', unsafe_allow_html=True)
            st.markdown("".join(f'<span class="tag tag-y">{k}</span>' for k in kws), unsafe_allow_html=True)

    with c_gauge:
        st.markdown('<div class="sec-sub">Nivel de riesgo</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(conf*100,1),
            number={"suffix":"%","font":{"size":36,"color":rc}},
            title={"text":"probabilidad de phishing","font":{"size":11,"color":"#AAA"}},
            gauge={
                "axis":{"range":[0,100],"visible":False},
                "bar":{"color":rc,"thickness":0.28},
                "bgcolor":"#D0D0D0","borderwidth":0,
                "steps":[
                    {"range":[0,35],"color":"#C8DCC8"},
                    {"range":[35,70],"color":"#DDD8C0"},
                    {"range":[70,100],"color":"#DCC8C8"},
                ],
            },
        ))
        fig.update_layout(height=210, margin=dict(t=30,b=0,l=10,r=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            f'<div style="background:{rb};border:2px solid {rc};border-radius:8px;'
            f'text-align:center;padding:10px;font-weight:900;font-size:14px;'
            f'color:{rc};letter-spacing:1.5px;'
            f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',system-ui,sans-serif">'
            f'RIESGO {risk.upper()}</div>',
            unsafe_allow_html=True,
        )

    # ── Recomendaciones ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Recomendaciones</div>', unsafe_allow_html=True)
    recs = [
        ("#EF4444", "No haga clic en ningun enlace del correo."),
        ("#EF4444", "No responda ni reenvie este correo."),
        ("#F59E0B", "Reportelo a su entidad bancaria de inmediato."),
        ("#F59E0B", "No ingrese datos personales ni bancarios."),
    ] if is_ph else [
        ("#22C55E", "Sin indicadores claros de phishing."),
        ("#22C55E", "El remitente parece legitimo."),
        ("#F5C518", "Mantenga precaucion con correos bancarios."),
    ]
    cols = st.columns(len(recs), gap="small")
    for col, (color, text) in zip(cols, recs):
        with col:
            st.markdown(
                f'<div style="border-left:5px solid {color};padding:13px 14px;'
                f'font-size:13px;font-weight:600;color:#2A2A2A;'
                f'background:#CACACA;border-radius:0 8px 8px 0;line-height:1.4;height:100%">'
                f'{text}</div>',
                unsafe_allow_html=True,
            )

    # ── Detalles del veredicto (expander) ─────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Ver detalles del veredicto"):
        _show_decision_process(result, conf, is_ph)

        ua = result.get("url_analysis", {})
        url_list = ua.get("urls", [])
        if url_list:
            st.markdown(_h2("3. Análisis de enlaces detectados"), unsafe_allow_html=True)
            st.markdown(
                '<p style="font-size:13px;color:#555;margin-bottom:12px">'
                'Se revisó cada enlace del correo buscando señales de suplantación o engaño.</p>',
                unsafe_allow_html=True,
            )
            _IND = {
                "uses_http":           "Conexión no cifrada (HTTP sin seguridad)",
                "is_ip_based":         "Usa dirección IP en vez de nombre de dominio",
                "is_shortener":        "Enlace acortado que oculta el destino real",
                "suspicious_tld":      "Extensión de dominio inusual (.xyz, .top, .info…)",
                "excessive_subdomains":"Demasiados subdominios para ocultar el dominio real",
            }
            _COLOR = {"alto": "#EF4444", "medio": "#F59E0B", "bajo": "#22C55E"}
            _LABEL = {"alto": "ALTO RIESGO", "medio": "RIESGO MEDIO", "bajo": "BAJO RIESGO"}
            for u in url_list:
                nivel  = u.get("risk_level", "bajo")
                color  = _COLOR[nivel]
                badge  = _LABEL[nivel]
                indicadores = []
                for key, desc in _IND.items():
                    if u.get(key):
                        indicadores.append(desc)
                if u.get("brand_spoofing"):
                    indicadores.append("Imita la marca: " + ", ".join(u["brand_spoofing"]))
                if u.get("suspicious_keywords"):
                    indicadores.append("Contiene palabras sospechosas: " + ", ".join(u["suspicious_keywords"][:3]))
                bg_url = {"alto": "#FFF8F8", "medio": "#FFFBF0", "bajo": "#F0FFF4"}.get(nivel, "#F5F5F5")
                ind_html = (
                    "".join(
                        f'<div style="font-size:14px;color:#222;padding:6px 0;border-bottom:1px solid #E5E5E5;font-weight:500">'
                        f'▸ {i}</div>'
                        for i in indicadores
                    )
                    if indicadores else
                    '<div style="font-size:14px;color:#666;padding:4px 0">Sin indicadores de riesgo detectados</div>'
                )
                st.markdown(
                    f'<div style="border-left:6px solid {color};background:{bg_url};border-radius:0 10px 10px 0;'
                    f'padding:16px 20px;margin-bottom:14px">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">'
                    f'<span style="font-size:13px;color:#222;font-family:monospace;word-break:break-all;font-weight:600">{u["url"]}</span>'
                    f'<span style="background:{color};color:#FFF;border-radius:6px;padding:4px 14px;'
                    f'font-size:12px;font-weight:800;white-space:nowrap;margin-left:14px">{badge}</span>'
                    f'</div>'
                    f'{ind_html}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:12px;color:#888;text-align:center;padding:8px">'
                'No se detectaron enlaces en este correo.</div>',
                unsafe_allow_html=True,
            )

    # ── Retroalimentacion ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="border-top:1px solid #3A3A3A;padding-top:16px;margin-top:4px">'
        '<span style="font-size:12px;color:#888">El resultado fue incorrecto?</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("Reportar error", type="secondary", use_container_width=True):
            st.session_state["_show_feedback"] = True
            # No st.rerun() — el botón ya dispara el re-render del diálogo

    if st.session_state.get("_show_feedback"):
        st.markdown("<br>", unsafe_allow_html=True)
        correcto = st.radio(
            "El correo era en realidad:",
            ["phishing", "seguro"],
            index=0 if label_val == "seguro" else 1,
            horizontal=True,
        )
        comentario = st.text_input("Comentario opcional (que fallo al detectar?)")
        c_env, c_can = st.columns([1, 1])
        with c_env:
            if st.button("Enviar retroalimentacion", type="primary", use_container_width=True):
                try:
                    import httpx as _httpx
                    snippet = result.get("explainability", {}).get("summary", "")[:200]
                    full_text = st.session_state.get("last_analyzed_text", "")
                    resp = _httpx.post(
                        f"{API_BASE_URL}/feedback/",
                        json={
                            "text_snippet": snippet,
                            "full_text": full_text,
                            "predicted_label": label_val,
                            "correct_label": correcto,
                            "confidence": conf,
                            "comment": comentario,
                        },
                        timeout=5.0,
                    ).json()
                    st.session_state["_show_feedback"] = False
                    if resp.get("retraining_started"):
                        st.session_state["_retraining"] = True
                    else:
                        st.success("Gracias. Tu correccion fue registrada.")
                except Exception:
                    st.error("No se pudo enviar la retroalimentacion.")
        with c_can:
            if st.button("Cancelar", use_container_width=True):
                st.session_state["_show_feedback"] = False
                # No st.rerun() — el botón ya actualiza el estado
