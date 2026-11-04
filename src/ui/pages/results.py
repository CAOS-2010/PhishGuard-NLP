from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st


_RISK_COLOR = {"alto": "#EF4444", "medio": "#F59E0B", "bajo": "#10B981"}
_RISK_BG    = {"alto": "#FEF2F2", "medio": "#FFFBEB", "bajo": "#ECFDF5"}
_RISK_LABEL = {"alto": "ALTO",    "medio": "MEDIO",   "bajo": "BAJO"}


def _build_explanation(label: str, confidence: float, xai: dict, urls: list, domain_mismatch: bool) -> str:
    pct = round(confidence * 100, 1)
    kws = xai.get("urgency_keywords_found", [])
    score = round(xai.get("social_engineering_score", 0) * 100)
    top_terms = [f["word"] for f in xai.get("top_phishing_features", [])[:3]]

    if label == "phishing":
        bg, border = "#FEF2F2", "#EF4444"
        partes = [
            f"El modelo clasificó este mensaje como <b>correo inseguro</b> con un nivel de confianza del <b>{pct}%</b>."
        ]
        if kws:
            muestra = ", ".join(f'<i>"{k}"</i>' for k in kws[:4])
            partes.append(
                f"Se detectaron <b>{len(kws)} palabras de presión psicológica</b> ({muestra}), "
                f"que son señales típicas de mensajes diseñados para generar urgencia en la víctima."
            )
        if score >= 50:
            partes.append(
                f"El índice de ingeniería social fue del <b>{score}%</b>, indicando un uso intensivo "
                f"de tácticas de manipulación para forzar una acción inmediata."
            )
        if urls:
            partes.append(
                f"Se encontraron <b>{len(urls)} URL{'s' if len(urls) > 1 else ''}</b> en el cuerpo del mensaje, "
                f"cuyo dominio no corresponde a ninguna entidad bancaria legítima conocida."
            )
        if domain_mismatch:
            partes.append(
                "Además, el <b>dominio del remitente no coincide</b> con el Return-Path, "
                "lo que es un indicador fuerte de suplantación de identidad."
            )
        if top_terms:
            partes.append(
                f"Los términos que más influyeron en la decisión fueron: "
                f"{', '.join(f'<i>{t}</i>' for t in top_terms)}."
            )
    else:
        bg, border = "#ECFDF5", "#10B981"
        partes = [
            f"El modelo clasificó este mensaje como <b>correo seguro</b> con una probabilidad de phishing del <b>{pct}%</b>, "
            f"por debajo del umbral de detección."
        ]
        if not kws:
            partes.append(
                "No se detectaron palabras de urgencia ni presión psicológica en el mensaje."
            )
        else:
            partes.append(
                f"Aunque se encontraron algunas palabras relacionadas ({', '.join(f'<i>{k}</i>' for k in kws[:3])}), "
                f"no fueron suficientes para superar el umbral de clasificación."
            )
        if score < 30:
            partes.append(
                f"El índice de ingeniería social fue del <b>{score}%</b>, lo que indica que el mensaje "
                f"no utiliza tácticas de manipulación psicológica típicas del phishing bancario."
            )
        if not urls:
            partes.append("No se encontraron URLs sospechosas en el cuerpo del mensaje.")
        if not domain_mismatch:
            partes.append("El dominio del remitente es coherente y no presenta señales de suplantación.")

    texto = " ".join(partes)
    return (
        f'<div style="background:{bg};border-radius:12px;padding:24px 28px;'
        f'border-left:6px solid {border};font-size:16px;color:#1A1A1A;line-height:1.9;'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',system-ui,sans-serif">'
        f'{texto}</div>'
    )


def render() -> None:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:24px">'
        '<div style="background:#F5C518;border-radius:10px;width:42px;height:42px;'
        'display:flex;align-items:center;justify-content:center;font-size:20px"></div>'
        '<div><h2 style="margin:0;font-size:24px;font-weight:800;color:#1C1C1E">Resultados</h2>'
        '<p style="margin:0;font-size:13px;color:#8E8E93">Analisis de phishing bancario</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    result = st.session_state.get("last_result")
    if result is None:
        st.markdown(
            '<div class="pg-card" style="text-align:center;padding:48px">'
            '<div style="font-size:48px;margin-bottom:16px"></div>'
            '<h3 style="color:#1C1C1E;margin-bottom:8px">Aun no hay resultados</h3>'
            '<p style="color:#8E8E93">Ve a <b>Inicio</b> y analiza un correo primero.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    label      = result["label"]
    risk       = result["risk_level"]
    confidence = result["confidence"]
    xai        = result.get("explainability", {})

    # Fila 1: Veredicto · Confianza · Riesgo · Ingenieria social
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        badge_cls = "badge-phishing" if label == "phishing" else "badge-safe"
        label_txt = "CORREO INSEGURO" if label == "phishing" else "CORREO SEGURO"
        st.markdown(
            f'<div class="pg-card" style="text-align:center;padding:28px 16px">'
            f'<p class="pg-card-title">Veredicto</p>'
            f'<div class="{badge_cls}">{label_txt}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with c2:
        pct = round(confidence * 100, 1)
        bar_color = _RISK_COLOR.get(risk, "#8E8E93")
        st.markdown(
            f'<div class="pg-card" style="text-align:center;padding:28px 16px">'
            f'<p class="pg-card-title">Confianza del modelo</p>'
            f'<div style="font-size:36px;font-weight:800;color:{bar_color}">{pct}%</div>'
            f'<div style="background:#F0F0F0;border-radius:999px;height:8px;margin-top:12px">'
            f'<div style="background:{bar_color};width:{pct}%;height:8px;border-radius:999px"></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    with c3:
        rc = _RISK_COLOR.get(risk, "#8E8E93")
        rb = _RISK_BG.get(risk, "#F5F5F5")
        rl = _RISK_LABEL.get(risk, risk.upper())
        st.markdown(
            f'<div class="pg-card" style="text-align:center;padding:28px 16px">'
            f'<p class="pg-card-title">Nivel de riesgo</p>'
            f'<div style="background:{rb};color:{rc};border-radius:10px;'
            f'padding:10px 18px;font-weight:800;font-size:24px;display:inline-block">'
            f'{rl}</div></div>',
            unsafe_allow_html=True,
        )

    with c4:
        score_pct = round(xai.get("social_engineering_score", 0) * 100)
        sc = "#EF4444" if score_pct >= 60 else "#F59E0B" if score_pct >= 30 else "#10B981"
        st.markdown(
            f'<div class="pg-card" style="text-align:center;padding:28px 16px">'
            f'<p class="pg-card-title">Ingenieria social</p>'
            f'<div style="font-size:36px;font-weight:800;color:{sc}">{score_pct}%</div>'
            f'<p style="font-size:12px;color:#8E8E93;margin:4px 0 0">indice de presion psicologica</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Fila 2: Gauge · Keywords · Explicacion
    col_gauge, col_xai = st.columns([2, 3], gap="large")

    with col_gauge:
        st.markdown('<div class="pg-card"><p class="pg-card-title">Probabilidad de phishing</p>', unsafe_allow_html=True)

        gauge_color = _RISK_COLOR.get(risk, "#8E8E93")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(confidence * 100, 1),
            number={"suffix": "%", "font": {"size": 40, "color": gauge_color}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#C7C7CC"},
                "bar": {"color": gauge_color, "thickness": 0.25},
                "bgcolor": "#F0F0F0",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 35],  "color": "#ECFDF5"},
                    {"range": [35, 70], "color": "#FFFBEB"},
                    {"range": [70, 100],"color": "#FEF2F2"},
                ],
                "threshold": {
                    "line": {"color": gauge_color, "width": 4},
                    "thickness": 0.8, "value": confidence * 100,
                },
            },
        ))
        fig.update_layout(
            height=240, margin=dict(t=20, b=10, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        summary = xai.get("summary", "")
        if summary:
            st.markdown(
                f'<div style="background:#FFFBEB;border-radius:10px;padding:12px 14px;'
                f'border-left:3px solid #F5C518;font-size:13px;color:#555">{summary}</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_xai:
        kws = xai.get("urgency_keywords_found", [])
        st.markdown(
            '<div class="pg-card">'
            '<p class="pg-card-title">Palabras de presion psicologica detectadas</p>',
            unsafe_allow_html=True,
        )
        if kws:
            chips = "".join(f'<span class="kw-chip">{k}</span>' for k in kws)
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.markdown(
                '<p style="color:#8E8E93;font-size:13px">No se detectaron palabras de urgencia.</p>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Explicacion en lenguaje natural
        st.markdown(
            '<div class="pg-card">'
            '<p class="pg-card-title">Por que el sistema tomo esta decision</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            _build_explanation(label, confidence, xai, result.get("urls_found", []), result.get("domain_mismatch", False)),
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Fila 3: URLs · Recomendaciones
    col_urls, col_rec = st.columns(2, gap="large")

    with col_urls:
        urls = result.get("urls_found", [])
        st.markdown(
            f'<div class="pg-card"><p class="pg-card-title">URLs encontradas ({len(urls)})</p>',
            unsafe_allow_html=True,
        )
        if result.get("domain_mismatch"):
            st.markdown(
                '<div style="background:#FEF2F2;border-radius:8px;padding:8px 12px;'
                'border-left:3px solid #EF4444;font-size:13px;margin-bottom:10px">'
                'El dominio del remitente no coincide con el Return-Path.</div>',
                unsafe_allow_html=True,
            )
        if urls:
            for url in urls[:10]:
                st.markdown(
                    f'<div style="background:#F5F5F5;border-radius:8px;padding:6px 12px;'
                    f'margin-bottom:4px;font-family:monospace;font-size:12px;'
                    f'word-break:break-all;color:#333">{url}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<p style="color:#8E8E93;font-size:13px">No se detectaron URLs.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_rec:
        st.markdown(
            '<div class="pg-card"><p class="pg-card-title">Recomendaciones de seguridad</p>',
            unsafe_allow_html=True,
        )
        if label == "phishing":
            items = [
                ("#EF4444", "#FEF2F2", "No haga clic en ningun enlace del mensaje."),
                ("#EF4444", "#FEF2F2", "No responda ni reenvie este correo."),
                ("#F59E0B", "#FFFBEB", "Reporte el correo a su entidad bancaria."),
                ("#F59E0B", "#FFFBEB", "Elimine el mensaje de su bandeja de entrada."),
                ("#F5C518", "#FFFDE7", "Cambie sus credenciales si hizo clic en algun enlace."),
            ]
        else:
            items = [
                ("#10B981", "#ECFDF5", "El mensaje no presenta indicadores claros de phishing."),
                ("#F5C518", "#FFFDE7", "Mantenga precaucion con correos que soliciten datos personales."),
                ("#F5C518", "#FFFDE7", "Verifique siempre el dominio del remitente."),
            ]
        for color, bg, text in items:
            st.markdown(
                f'<div style="background:{bg};border-radius:8px;padding:8px 12px;'
                f'margin-bottom:6px;font-size:13px;border-left:3px solid {color}">'
                f'{text}</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)
