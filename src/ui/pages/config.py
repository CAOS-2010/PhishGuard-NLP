from __future__ import annotations

import streamlit as st
import httpx
from config.settings import API_BASE_URL


def render() -> None:
    st.markdown(
        '<div class="pg-topbar">'
        '<div class="pg-topbar-title">PHISHGUARD <span>NLP</span> — CONFIGURACION</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns([2, 3], gap="large")

    with col_a:
        st.markdown('<div class="pg-card"><p class="pg-card-title">Estado del sistema</p>', unsafe_allow_html=True)
        try:
            data = httpx.get(f"{API_BASE_URL}/health", timeout=3.0).json()
            status_color = "#22C55E" if data.get("model_loaded") else "#EF4444"
            status_text  = "ACTIVO" if data.get("model_loaded") else "SIN MODELO"
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;padding:12px 0">'
                f'<div style="width:14px;height:14px;border-radius:50%;background:{status_color}"></div>'
                f'<div><b style="font-size:14px;color:#1A1A1A">API FastAPI</b>'
                f'<br><span style="font-size:11px;color:#888">{API_BASE_URL} — {status_text}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        except Exception:
            st.markdown(
                '<div style="display:flex;align-items:center;gap:12px;padding:12px 0">'
                '<div style="width:14px;height:14px;border-radius:50%;background:#EF4444"></div>'
                '<div><b style="font-size:14px;color:#1A1A1A">API FastAPI</b>'
                '<br><span style="font-size:11px;color:#888">No responde</span></div>'
                '</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="pg-card"><p class="pg-card-title">Informacion del proyecto</p>', unsafe_allow_html=True)
        info = [
            ("Proyecto",    "PhishGuard NLP"),
            ("Version",     "1.0.0"),
            ("Autor",       "Santiago Jojoa Echeverri"),
            ("Programa",    "Ingenieria en Software"),
            ("Institucion", "Tecnologico de Antioquia IU"),
            ("Director",    "Dario Enrique Soto Duran"),
            ("Ano",         "2026"),
        ]
        for label, val in info:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:7px 0;border-bottom:1px solid #F5F5F5">'
                f'<span style="font-size:11px;color:#AAA;font-weight:700;text-transform:uppercase;letter-spacing:0.5px">{label}</span>'
                f'<span style="font-size:12px;color:#1A1A1A;font-weight:600">{val}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="pg-card"><p class="pg-card-title">Instrucciones de ejecucion</p>', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:12px;color:#555;margin-bottom:12px">Para ejecutar el sistema completo localmente:</p>',
            unsafe_allow_html=True,
        )
        pasos = [
            ("1", "Activar entorno virtual", "python -m venv venv && venv\\Scripts\\activate"),
            ("2", "Instalar dependencias",   "pip install -r requirements.txt"),
            ("3", "Entrenar el modelo",      "python scripts/train_model.py"),
            ("4", "Iniciar la API",          "uvicorn src.api.main:app --reload --port 8000"),
            ("5", "Iniciar la interfaz",     "streamlit run src/ui/app.py"),
        ]
        for num, titulo, cmd in pasos:
            st.markdown(
                f'<div style="margin-bottom:12px">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">'
                f'<div style="background:#F5C518;border-radius:50%;width:20px;height:20px;min-width:20px;'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-size:10px;font-weight:900;color:#1A1A1A">{num}</div>'
                f'<span style="font-size:12px;font-weight:700;color:#1A1A1A">{titulo}</span>'
                f'</div>'
                f'<div style="background:#1A1A1A;border-radius:6px;padding:7px 12px;'
                f'font-family:monospace;font-size:12px;color:#F5C518;margin-left:28px">{cmd}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="pg-card"><p class="pg-card-title">Gestion del historial</p>', unsafe_allow_html=True)
        col_info, col_btn = st.columns([2, 1])
        with col_info:
            try:
                total = httpx.get(f"{API_BASE_URL}/history/", params={"limit": 1}, timeout=3.0).json()["total"]
                st.markdown(f'<p style="font-size:13px;color:#555;margin:0">Registros almacenados: <b>{total}</b></p>', unsafe_allow_html=True)
            except Exception:
                st.markdown('<p style="font-size:13px;color:#AAA;margin:0">No disponible</p>', unsafe_allow_html=True)
        with col_btn:
            if st.button("LIMPIAR", type="secondary", use_container_width=True):
                try:
                    httpx.delete(f"{API_BASE_URL}/history/", timeout=5.0)
                    st.success("Historial eliminado.")
                except Exception:
                    st.error("Error al limpiar.")
        st.markdown('</div>', unsafe_allow_html=True)
