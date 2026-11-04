from __future__ import annotations

import httpx
import plotly.graph_objects as go
import streamlit as st

from config.settings import API_BASE_URL

_RC = {"alto": "#EF4444", "medio": "#F59E0B", "bajo": "#22C55E"}


def _fetch_stats() -> dict | None:
    try:
        return httpx.get(f"{API_BASE_URL}/stats/", timeout=5.0).json()
    except Exception:
        return None


def _kpi(label: str, value: str, sub: str = "", color: str = "#1A1A1A") -> str:
    return (
        f'<div style="background:#CACACA;border-radius:12px;padding:20px 24px;text-align:center">'
        f'<div style="font-size:11px;font-weight:700;letter-spacing:1.5px;color:#888;'
        f'text-transform:uppercase;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif">{label}</div>'
        f'<div style="font-size:34px;font-weight:900;color:{color};margin:6px 0 2px;'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif">{value}</div>'
        f'<div style="font-size:11px;color:#999;font-weight:600">{sub}</div>'
        f'</div>'
    )


def render() -> None:
    st.markdown('<div class="sec-title">Dashboard</div>', unsafe_allow_html=True)

    stats = _fetch_stats()

    if not stats:
        st.warning("No se pudo conectar con la API.")
        return

    total = stats["total"]

    if total == 0:
        st.markdown(
            '<div style="text-align:center;padding:60px 0;color:#AAA;font-size:14px;font-weight:600">'
            'Aún no hay análisis registrados. Analiza un correo para ver estadísticas.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    ph = stats["phishing_count"]
    sg = stats["safe_count"]
    ph_pct = round(ph / total * 100, 1) if total else 0
    fb_corr = stats["feedback_corrections"]
    avg_ms = stats["avg_response_ms"]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        st.markdown(_kpi("Total analizados", str(total), "correos"), unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi("Phishing detectados", str(ph), f"{ph_pct}% del total", "#EF4444"), unsafe_allow_html=True)
    with c3:
        st.markdown(_kpi("Correcciones al modelo", str(fb_corr), "vía retroalimentación", "#F5C518"), unsafe_allow_html=True)
    with c4:
        st.markdown(_kpi("Tiempo promedio", f"{round(avg_ms)}ms", "por análisis", "#22C55E"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Fila: tendencia diaria + distribución riesgo ───────────────────────────
    c_trend, c_dist = st.columns([2, 1], gap="large")

    with c_trend:
        st.markdown('<div class="sec-sub">Tendencia de análisis (últimos 30 días)</div>', unsafe_allow_html=True)
        daily = stats.get("daily_trend", [])
        if daily:
            days   = [r["day"] for r in daily]
            ph_day = [r["phishing"] for r in daily]
            sg_day = [r["safe"] for r in daily]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Phishing", x=days, y=ph_day,
                marker_color="#EF4444", opacity=0.85,
            ))
            fig.add_trace(go.Bar(
                name="Seguro", x=days, y=sg_day,
                marker_color="#22C55E", opacity=0.85,
            ))
            fig.update_layout(
                barmode="stack",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=0, r=0),
                height=240,
                legend=dict(orientation="h", y=1.1, font=dict(size=11)),
                xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                yaxis=dict(showgrid=True, gridcolor="#C8C8C8", tickfont=dict(size=10)),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<p style="color:#AAA;font-size:12px">Sin datos de los últimos 30 días.</p>', unsafe_allow_html=True)

    with c_dist:
        st.markdown('<div class="sec-sub">Distribución por nivel de riesgo</div>', unsafe_allow_html=True)
        rd = stats["risk_distribution"]
        labels = ["Alto", "Medio", "Bajo"]
        values = [rd["alto"], rd["medio"], rd["bajo"]]
        colors = ["#EF4444", "#F59E0B", "#22C55E"]

        fig2 = go.Figure(go.Pie(
            labels=labels, values=values,
            marker=dict(colors=colors),
            hole=0.55,
            textfont=dict(size=11),
            showlegend=True,
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=0, r=0),
            height=240,
            legend=dict(orientation="h", y=-0.05, font=dict(size=11)),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Fila: gauge confianza + resumen feedback ───────────────────────────────
    c_gauge, c_fb = st.columns([1, 2], gap="large")

    with c_gauge:
        st.markdown('<div class="sec-sub">Confianza promedio del modelo</div>', unsafe_allow_html=True)
        avg_conf = round(stats["avg_confidence"] * 100, 1)
        fig3 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_conf,
            number={"suffix": "%", "font": {"size": 32, "color": "#1A1A1A"}},
            title={"text": "confianza media", "font": {"size": 10, "color": "#AAA"}},
            gauge={
                "axis": {"range": [0, 100], "visible": False},
                "bar": {"color": "#F5C518", "thickness": 0.28},
                "bgcolor": "#D0D0D0", "borderwidth": 0,
                "steps": [
                    {"range": [0, 35],  "color": "#C8DCC8"},
                    {"range": [35, 70], "color": "#DDD8C0"},
                    {"range": [70, 100],"color": "#DCC8C8"},
                ],
            },
        ))
        fig3.update_layout(
            height=200,
            margin=dict(t=30, b=0, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig3, use_container_width=True)

    with c_fb:
        st.markdown('<div class="sec-sub">Retroalimentación acumulada</div>', unsafe_allow_html=True)
        fb_total = stats["feedback_total"]
        fb_corr  = stats["feedback_corrections"]
        fb_ok    = fb_total - fb_corr

        for lbl, val, color in [
            ("Retroalimentaciones enviadas", fb_total, "#1A1A1A"),
            ("Correcciones al modelo",       fb_corr,  "#EF4444"),
            ("Resultados confirmados",       fb_ok,    "#22C55E"),
        ]:
            pct = round(val / fb_total * 100) if fb_total else 0
            st.markdown(
                f'<div style="margin-bottom:12px">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:4px">'
                f'<span class="slbl">{lbl}</span>'
                f'<span style="font-size:13px;font-weight:900;color:{color}">{val}</span>'
                f'</div>'
                f'<div class="bar-bg"><div class="bar-fill" style="background:{color};width:{pct}%"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        from src.core.retrainer import get_status
        rs = get_status()
        if rs["last_trained_at"]:
            st.markdown(
                f'<div style="margin-top:12px;font-size:11px;color:#22C55E;font-weight:600">'
                f'Último reentrenamiento: {rs["last_trained_at"]}'
                f'&nbsp;·&nbsp;Ejemplos agregados: {rs["examples_added"]}'
                f'</div>',
                unsafe_allow_html=True,
            )
        elif rs["is_training"]:
            st.markdown(
                '<div style="margin-top:12px;font-size:11px;color:#F5C518;font-weight:600">'
                'Modelo reentrenando en segundo plano...'
                '</div>',
                unsafe_allow_html=True,
            )
