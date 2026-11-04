from __future__ import annotations

import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config.settings import API_BASE_URL


def _h2(text: str) -> str:
    return (
        f'<div style="font-size:20px;font-weight:900;color:#111111;margin:24px 0 14px;'
        f'border-bottom:2px solid #E5E5E5;padding-bottom:8px;'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif">{text}</div>'
    )


def _fetch_history(limit: int = 200) -> list[dict]:
    try:
        r = httpx.get(f"{API_BASE_URL}/history/", params={"limit": limit}, timeout=10.0)
        r.raise_for_status()
        return r.json()["records"]
    except Exception:
        return []


def _fetch_stats() -> dict | None:
    try:
        return httpx.get(f"{API_BASE_URL}/stats/", timeout=5.0).json()
    except Exception:
        return None


def render() -> None:
    st.markdown(_h2("Dashboard · Estadísticas del sistema"), unsafe_allow_html=True)

    records = _fetch_history()
    stats   = _fetch_stats()

    if not records:
        st.markdown(
            '<div style="background:#F5F5F5;border-left:5px solid #C0C0C0;border-radius:0 10px 10px 0;'
            'padding:24px 28px;font-size:14px;font-weight:600;color:#888">'
            'Analiza correos desde el Panel para ver las estadísticas.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    df = pd.DataFrame(records)
    df["analyzed_at"] = pd.to_datetime(df["analyzed_at"])
    df["date"] = df["analyzed_at"].dt.date

    total    = len(df)
    phishing = int((df["label"] == "phishing").sum())
    safe     = total - phishing
    rate     = round(phishing / total * 100, 1) if total else 0
    fb_corr  = stats["feedback_corrections"] if stats else 0
    avg_ms   = round(stats["avg_response_ms"]) if stats else 0

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6, gap="small")
    kpis = [
        (c1, "Total analizados", str(total),      "#1A1A1A", "#F5F5F5", "#C0C0C0"),
        (c2, "Phishing",         str(phishing),   "#B91C1C", "#FEF2F2", "#FECACA"),
        (c3, "Seguros",          str(safe),        "#15803D", "#F0FDF4", "#86EFAC"),
        (c4, "Tasa phishing",    f"{rate}%",       "#B91C1C", "#FEF2F2", "#FECACA"),
        (c5, "Correcciones",     str(fb_corr),     "#92400E", "#FFF9C4", "#F5C518"),
        (c6, "Tiempo promedio",  f"{avg_ms}ms",    "#1A1A1A", "#F5F5F5", "#C0C0C0"),
    ]
    for col, label, val, color, bg, border in kpis:
        with col:
            st.markdown(
                f'<div style="background:{bg};border-radius:12px;padding:16px 10px;'
                f'text-align:center;border:2px solid {border}">'
                f'<div style="font-size:9px;font-weight:700;letter-spacing:1.2px;color:#888;'
                f'text-transform:uppercase;font-family:-apple-system,sans-serif;margin-bottom:6px">'
                f'{label}</div>'
                f'<div style="font-size:28px;font-weight:900;color:{color};line-height:1;'
                f'font-family:-apple-system,sans-serif">{val}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tendencia + distribución ───────────────────────────────────────────────
    st.markdown(_h2("Tendencia de análisis por fecha"), unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:13px;color:#555;margin:-8px 0 14px">'
        'Evolución diaria de correos clasificados como phishing o seguros.</p>',
        unsafe_allow_html=True,
    )

    c_line, c_pie = st.columns([3, 2], gap="large")

    with c_line:
        tl = df.groupby(["date", "label"]).size().reset_index(name="count")
        if not tl.empty:
            fig = px.line(
                tl, x="date", y="count", color="label",
                color_discrete_map={"phishing": "#EF4444", "seguro": "#22C55E"},
                markers=True,
                labels={"date": "Fecha", "count": "Cantidad", "label": "Veredicto"},
            )
            fig.update_layout(
                height=270, margin=dict(t=10, b=10, l=0, r=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=1.12, font=dict(size=12, color="#333")),
                xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#333")),
                yaxis=dict(gridcolor="#E5E5E5", tickfont=dict(size=11, color="#333")),
            )
            fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
            st.plotly_chart(fig, use_container_width=True)

    with c_pie:
        st.markdown(
            '<div style="font-size:13px;font-weight:700;color:#555;margin-bottom:8px">'
            'Distribución por nivel de riesgo</div>',
            unsafe_allow_html=True,
        )
        counts = df["risk_level"].value_counts().reset_index()
        counts.columns = ["nivel", "cantidad"]
        colors_map = {"alto": "#EF4444", "medio": "#F5C518", "bajo": "#22C55E"}
        fig2 = go.Figure(go.Pie(
            labels=counts["nivel"], values=counts["cantidad"],
            marker_colors=[colors_map.get(n, "#888") for n in counts["nivel"]],
            hole=0.55, textfont=dict(size=12, color="#111"),
            textinfo="label+percent", showlegend=False,
        ))
        fig2.update_layout(
            height=270, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Confianza + retroalimentación ─────────────────────────────────────────
    st.markdown(_h2("Confianza del modelo y retroalimentación"), unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:13px;color:#555;margin:-8px 0 14px">'
        'Nivel de certeza promedio del modelo y datos de correcciones enviadas por usuarios.</p>',
        unsafe_allow_html=True,
    )

    c_gauge, c_fb = st.columns([1, 2], gap="large")

    with c_gauge:
        avg_conf   = round((stats["avg_confidence"] if stats else df["confidence"].mean()) * 100, 1)
        conf_color = "#EF4444" if avg_conf >= 70 else "#F5C518" if avg_conf >= 35 else "#22C55E"
        fig3 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_conf,
            number={"suffix": "%", "font": {"size": 32, "color": conf_color}},
            title={"text": "confianza media del modelo", "font": {"size": 11, "color": "#888"}},
            gauge={
                "axis": {"range": [0, 100], "visible": False},
                "bar": {"color": conf_color, "thickness": 0.28},
                "bgcolor": "#E5E5E5", "borderwidth": 0,
                "steps": [
                    {"range": [0, 35],  "color": "#C8DCC8"},
                    {"range": [35, 70], "color": "#DDD8C0"},
                    {"range": [70, 100],"color": "#DCC8C8"},
                ],
            },
        ))
        fig3.update_layout(
            height=210, margin=dict(t=30, b=0, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig3, use_container_width=True)
        conf_bg = "#FEF2F2" if avg_conf >= 70 else "#FFFBF0" if avg_conf >= 35 else "#F0FFF4"
        st.markdown(
            f'<div style="background:{conf_bg};border:2px solid {conf_color};border-radius:8px;'
            f'text-align:center;padding:10px;font-weight:900;font-size:14px;color:{conf_color};'
            f'letter-spacing:1px;font-family:-apple-system,sans-serif">'
            f'{avg_conf}% CONFIANZA MEDIA</div>',
            unsafe_allow_html=True,
        )

    with c_fb:
        if stats:
            fb_total = stats["feedback_total"]
            fb_corr2 = stats["feedback_corrections"]
            fb_ok    = fb_total - fb_corr2

            for lbl, val, color, bg in [
                ("Retroalimentaciones totales", fb_total, "#1A1A1A", "#F5F5F5"),
                ("Correcciones al modelo",      fb_corr2, "#B91C1C", "#FEF2F2"),
                ("Resultados confirmados",      fb_ok,    "#15803D", "#F0FDF4"),
            ]:
                pct = round(val / fb_total * 100) if fb_total else 0
                st.markdown(
                    f'<div style="background:{bg};border-radius:10px;padding:14px 16px;margin-bottom:10px">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
                    f'<span style="font-size:12px;font-weight:700;color:#555;text-transform:uppercase;'
                    f'letter-spacing:0.5px">{lbl}</span>'
                    f'<span style="font-size:22px;font-weight:900;color:{color}">{val}</span>'
                    f'</div>'
                    f'<div class="bar-bg"><div class="bar-fill" style="background:{color};width:{pct}%"></div></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            from src.core.retrainer import get_status
            rs = get_status()
            if rs["is_training"]:
                st.markdown(
                    '<div style="background:#1A2A1A;border-left:5px solid #22C55E;'
                    'border-radius:0 10px 10px 0;padding:14px 18px;margin-top:4px;'
                    'font-size:13px;color:#22C55E;font-weight:600">'
                    'El modelo está reentrenando en segundo plano... (~60 s)'
                    '</div>',
                    unsafe_allow_html=True,
                )
            elif rs["last_trained_at"]:
                st.markdown(
                    f'<div style="background:#F0FDF4;border-left:5px solid #22C55E;'
                    f'border-radius:0 10px 10px 0;padding:14px 18px;margin-top:4px;'
                    f'font-size:13px;color:#15803D;font-weight:600">'
                    f'Último reentrenamiento: {rs["last_trained_at"]} · '
                    f'Ejemplos agregados: {rs["examples_added"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div style="background:#F5F5F5;border-left:5px solid #C0C0C0;'
                'border-radius:0 10px 10px 0;padding:14px 18px;'
                'font-size:13px;color:#888;font-weight:600">'
                'Sin datos de retroalimentación aún.'
                '</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabla de registros ────────────────────────────────────────────────────
    st.markdown(_h2("Registros recientes"), unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:13px;color:#555;margin:-8px 0 14px">'
        'Historial de los últimos análisis realizados por el sistema.</p>',
        unsafe_allow_html=True,
    )
    display = df[["analyzed_at", "sender", "subject", "risk_level", "label", "confidence"]].copy()
    display["confidence"] = display["confidence"].apply(lambda x: f"{round(x * 100, 1)}%")
    display["label"]      = display["label"].map({"phishing": "PHISHING", "seguro": "SEGURO"})
    display["risk_level"] = display["risk_level"].map({"alto": "ALTO", "medio": "MEDIO", "bajo": "BAJO"})
    display.columns       = ["Fecha", "Remitente", "Asunto", "Riesgo", "Veredicto", "Confianza"]
    st.dataframe(display.head(50), use_container_width=True, hide_index=True)
