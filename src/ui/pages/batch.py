from __future__ import annotations

import io
import time
from pathlib import Path

import httpx
import pandas as pd
import streamlit as st

from config.settings import API_BASE_URL

_RC = {"alto": "#EF4444", "medio": "#F59E0B", "bajo": "#22C55E"}
_RL = {"alto": "ALTO", "medio": "MEDIO", "bajo": "BAJO"}


def _analyze(subject: str, text: str, sender: str = "") -> dict | None:
    try:
        r = httpx.post(
            f"{API_BASE_URL}/analyze/",
            json={"text": text, "subject": subject, "sender": sender},
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def render() -> None:
    st.markdown('<div class="sec-title">Análisis por Lote</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:12px;color:#888;margin-top:-8px;margin-bottom:20px">'
        'Sube varios archivos .eml a la vez y obtén un resumen de resultados en tabla.'
        '</p>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Archivos de correo (.eml)",
        type=["eml"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if not uploaded:
        st.markdown(
            '<div style="text-align:center;padding:50px 0;color:#AAA;font-size:13px;font-weight:600;'
            'border:2px dashed #BBBBBB;border-radius:12px;background:#D5D5D5">'
            'Arrastra aquí uno o varios archivos .eml para analizar en lote'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<p style="font-size:12px;color:#555;font-weight:700;margin-bottom:16px">'
        f'{len(uploaded)} archivo{"s" if len(uploaded) > 1 else ""} seleccionado{"s" if len(uploaded) > 1 else ""}'
        f'</p>',
        unsafe_allow_html=True,
    )

    if not st.button("ANALIZAR LOTE", type="primary", use_container_width=False):
        return

    from src.data.parser import parse_file

    results = []
    progress = st.progress(0, text="Iniciando análisis...")
    tmp_dir = Path("data/raw/tmp_batch")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for i, up in enumerate(uploaded):
        progress.progress((i) / len(uploaded), text=f"Analizando {up.name}...")
        tmp = tmp_dir / up.name
        tmp.write_bytes(up.read())
        try:
            parsed = parse_file(tmp)
            res = _analyze(parsed.subject or "", parsed.body, parsed.sender or "")
            if res:
                results.append({
                    "archivo": up.name,
                    "asunto": (parsed.subject or "Sin asunto")[:50],
                    "remitente": (parsed.sender or "Desconocido")[:40],
                    "veredicto": res["label"],
                    "confianza": res["confidence"],
                    "riesgo": res["risk_level"],
                    "urls": res["url_analysis"]["total_urls"],
                })
            else:
                results.append({
                    "archivo": up.name,
                    "asunto": "Error al analizar",
                    "remitente": "",
                    "veredicto": "error",
                    "confianza": 0.0,
                    "riesgo": "bajo",
                    "urls": 0,
                })
        except Exception:
            results.append({
                "archivo": up.name,
                "asunto": "Error al parsear",
                "remitente": "",
                "veredicto": "error",
                "confianza": 0.0,
                "riesgo": "bajo",
                "urls": 0,
            })
        finally:
            try:
                tmp.unlink()
            except Exception:
                pass

    progress.progress(1.0, text="Análisis completado.")
    time.sleep(0.4)
    progress.empty()

    if not results:
        st.warning("No se pudo analizar ningún archivo.")
        return

    # ── Resumen KPIs ──────────────────────────────────────────────────────────
    ph_count  = sum(1 for r in results if r["veredicto"] == "phishing")
    sg_count  = sum(1 for r in results if r["veredicto"] == "seguro")
    err_count = sum(1 for r in results if r["veredicto"] == "error")
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="small")
    for col, lbl, val, color in [
        (c1, "Phishing detectados", ph_count, "#EF4444"),
        (c2, "Correos seguros",     sg_count, "#22C55E"),
        (c3, "Errores de lectura",  err_count,"#888888"),
    ]:
        with col:
            st.markdown(
                f'<div style="background:#CACACA;border-radius:10px;padding:16px;text-align:center">'
                f'<div style="font-size:10px;font-weight:700;letter-spacing:1.2px;color:#888;text-transform:uppercase">{lbl}</div>'
                f'<div style="font-size:30px;font-weight:900;color:{color};margin-top:4px">{val}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Resultados detallados</div>', unsafe_allow_html=True)

    # ── Tabla de resultados ────────────────────────────────────────────────────
    for r in results:
        is_ph = r["veredicto"] == "phishing"
        is_err = r["veredicto"] == "error"
        color  = "#EF4444" if is_ph else ("#888" if is_err else "#22C55E")
        badge  = "PHISHING" if is_ph else ("ERROR" if is_err else "SEGURO")
        bg     = "#2A1A1A" if is_ph else ("#2A2A2A" if is_err else "#1A2A1A")
        conf_pct = f"{round(r['confianza']*100, 1)}%" if not is_err else "—"
        risk_color = _RC.get(r["riesgo"], "#888")

        st.markdown(
            f'<div style="background:{bg};border-left:5px solid {color};border-radius:0 8px 8px 0;'
            f'padding:12px 16px;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between">'
            f'<div style="flex:1;min-width:0">'
            f'<div style="font-size:12px;font-weight:700;color:#EEE;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'
            f'{r["asunto"]}</div>'
            f'<div style="font-size:10px;color:#888;margin-top:2px">{r["remitente"]} · {r["archivo"]}</div>'
            f'</div>'
            f'<div style="display:flex;align-items:center;gap:12px;margin-left:16px;white-space:nowrap">'
            f'<span style="font-size:11px;color:{risk_color};font-weight:700">Riesgo {_RL.get(r["riesgo"],"")}</span>'
            f'<span style="font-size:11px;color:#AAA">Conf. {conf_pct}</span>'
            f'<span style="font-size:10px;color:#AAA">URLs: {r["urls"]}</span>'
            f'<span style="background:{color};color:#FFF;border-radius:4px;padding:3px 10px;'
            f'font-size:10px;font-weight:800">{badge}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Exportar CSV ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    df_export = pd.DataFrame(results)
    df_export["confianza"] = df_export["confianza"].apply(lambda x: f"{round(x*100,1)}%")
    csv_bytes = df_export.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Descargar resultados CSV",
        data=csv_bytes,
        file_name="phishguard_lote.csv",
        mime="text/csv",
        use_container_width=False,
    )
