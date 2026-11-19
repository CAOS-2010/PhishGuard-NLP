from __future__ import annotations
import streamlit as st

st.set_page_config(page_title="PhishGuard NLP", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
/* Ocultar sidebar y su toggle */
section[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"],
[data-testid="stSidebarNav"] { display:none !important; }

/* Ocultar menú hamburger, footer y botón deploy de Streamlit */
#MainMenu { visibility:hidden !important; }
footer { visibility:hidden !important; }
header { visibility:hidden !important; }
[data-testid="stToolbar"] { display:none !important; }
.stDeployButton { display:none !important; }
[data-testid="stStatusWidget"] { display:none !important; }

/* Base */
.stApp { background:#D8D8D8; }
.block-container { padding:28px 36px 36px 36px !important; max-width:100% !important; }

/* ── Spinner de carga ────────────────────────────────── */
@keyframes pg-spin {
    0%   { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.pg-spinner {
    width:70px; height:70px;
    border:6px solid #C0C0C0;
    border-top:6px solid #F5C518;
    border-radius:50%;
    animation: pg-spin 0.75s linear infinite;
    margin: 0 auto 28px auto;
}

/* ── TABS — contenedor (PANEL/DATOS y TEXTO/ARCHIVO) ─── */
[role="tablist"] {
    background:#C4C4C4 !important;
    border-radius:999px !important;
    padding:5px !important;
    gap:4px !important;
    width:fit-content !important;
}

/* Cada tab: forma pill + clip del SelectionIndicator */
[data-testid="stTab"] {
    border-radius:999px !important;
    overflow:hidden !important;
    position:relative !important;
    border:none !important;
    background:transparent !important;
    cursor:pointer !important;
}

/* Ocultar el subrayado default de React-ARIA */
[data-testid="stTab"] .react-aria-SelectionIndicator {
    display:none !important;
}

/* Fondo amarillo pill en el tab activo */
[data-testid="stTab"][aria-selected="true"] {
    background:#F5C518 !important;
    box-shadow:0 2px 12px rgba(245,197,24,0.4) !important;
}

/* Texto de los tabs PANEL / DATOS (outer) — mismo tamaño que inner */
[data-testid="stTabs"] > div > [role="tablist"] [data-testid="stTab"] p {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
    font-weight:900 !important;
    font-size:11px !important;
    text-transform:uppercase !important;
    letter-spacing:1.8px !important;
    color:#777 !important;
    margin:0 !important;
    padding:7px 34px !important;
    position:relative !important;
    z-index:1 !important;
    transition:color 0.2s ease !important;
}
[data-testid="stTabs"] > div > [role="tablist"] [data-testid="stTab"][aria-selected="true"] p {
    color:#1A1A1A !important;
}

/* ── TABS TEXTO / ARCHIVO (inner — menor padding) ─────── */
[data-testid="stTabs"] [data-testid="stTabs"] > div > [role="tablist"] {
    background:#CCCCCC !important;
}
[data-testid="stTabs"] [data-testid="stTabs"] > div > [role="tablist"] [data-testid="stTab"] p {
    font-size:11px !important;
    letter-spacing:1.8px !important;
    padding:7px 34px !important;
}

/* ── Botones ─────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background:#F5C518 !important; color:#1A1A1A !important;
    border:none !important; font-weight:900 !important; border-radius:999px !important;
    font-size:12px !important; letter-spacing:1px !important; text-transform:uppercase !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
    transition: background 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover { background:#D4A800 !important; }
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"] p,
[data-testid="stBaseButton-primary"] span,
[data-testid="stBaseButton-primary"] div {
    font-weight:900 !important;
    border-radius:999px !important;
}
.stButton > button[kind="secondary"] {
    background:#E0E0E0 !important; border:2px solid #C8C8C8 !important;
    color:#1A1A1A !important; border-radius:8px !important; font-weight:700 !important;
    font-size:12px !important; text-transform:uppercase !important; letter-spacing:0.5px !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
}
.stButton > button[kind="secondary"]:hover { border-color:#F5C518 !important; background:#FFFDE7 !important; }

/* ── Inputs ──────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea {
    border-radius:8px !important; border:1.5px solid #C8C8C8 !important;
    background:#E8E8E8 !important; font-size:13px !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color:#F5C518 !important; box-shadow:0 0 0 3px rgba(245,197,24,0.15) !important;
    background:#F5F5F5 !important;
}
.stTextInput > label, .stTextArea > label {
    font-size:10px !important; font-weight:700 !important;
    text-transform:uppercase !important; letter-spacing:1px !important; color:#AAA !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
}

/* ── Tags ────────────────────────────────────────────── */
.tag { display:inline-block; border-radius:4px; padding:3px 10px; font-size:11px; font-weight:700; margin:2px; }
.tag-y { background:#FFF9C4; color:#92400E; border:1px solid #F5C518; }
.tag-g { background:#D5D5D5; color:#555; border:1px solid #C0C0C0; }
.tag-r { background:#FEF2F2; color:#B91C1C; border:1px solid #FECACA; }

/* ── Barras de progreso ──────────────────────────────── */
.bar-bg   { background:#C8C8C8; border-radius:999px; height:6px; margin-top:5px; }
.bar-fill { height:6px; border-radius:999px; }

/* ── Stat rows ───────────────────────────────────────── */
.srow { display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #C8C8C8; }
.slbl { font-size:11px; color:#999; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; }
.sval { font-size:14px; color:#1A1A1A; font-weight:900; }

/* ── Seccion headers ─────────────────────────────────── */
.sec-title {
    font-size:13px; font-weight:800; letter-spacing:2px; color:#1A1A1A;
    text-transform:uppercase; margin-bottom:16px; margin-top:4px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    padding-bottom:10px; border-bottom:2px solid #C0C0C0;
}
.sec-sub {
    font-size:9px; font-weight:700; letter-spacing:1.2px; color:#AAAAAA;
    text-transform:uppercase; margin:16px 0 8px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

/* ── Historial ───────────────────────────────────────── */
.hrow { display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #C8C8C8; }
.hlbl { font-size:11px; color:#555; max-width:140px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.hbadge { font-size:9px; font-weight:800; padding:2px 7px; border-radius:4px; }
.hph { background:#FEF2F2; color:#B91C1C; }
.hsg { background:#F0FDF4; color:#15803D; }

/* ── Veredicto ───────────────────────────────────────── */
.vbox { border-radius:8px; padding:10px 16px; text-align:center; font-size:13px; font-weight:900;
        letter-spacing:1px; text-transform:uppercase; margin-bottom:10px; }
.vph { background:#FEF2F2; color:#B91C1C; border:2px solid #FECACA; }
.vsg { background:#F0FDF4; color:#15803D; border:2px solid #86EFAC; }

/* ── File uploader ───────────────────────────────────── */
[data-testid="stFileUploader"] section {
    border:2px dashed #BBBBBB !important; border-radius:8px !important; background:#D5D5D5 !important;
}
[data-testid="stFileUploader"] section:hover { border-color:#F5C518 !important; }

/* ── Dataframe ───────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius:8px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)

import httpx
from config.settings import API_BASE_URL


# ── Pantalla de Login / Registro ──────────────────────────────────────────────

def _auth_page() -> None:
    st.markdown("""
    <style>
    .stButton > button[kind="primary"] {
        background:#1A1A1A !important; color:#F5C518 !important;
    }
    .stButton > button[kind="primary"]:hover { background:#333333 !important; }
    </style>
    <div style="max-width:420px;margin:40px auto 0 auto;text-align:center">
      <div style="background:#F5C518;border-radius:18px;width:72px;height:72px;
                  display:flex;flex-direction:column;align-items:center;justify-content:center;
                  font-size:24px;font-weight:900;color:#1A1A1A;margin:0 auto 20px auto;
                  box-shadow:0 4px 18px rgba(245,197,24,0.45)">
        PG<span style="font-size:9px;font-weight:700;opacity:0.65">NLP</span>
      </div>
      <div style="font-size:28px;font-weight:900;color:#1A1A1A;margin-bottom:4px">PhishGuard NLP</div>
      <div style="font-size:13px;color:#AAAAAA;font-weight:600;margin-bottom:32px">
        Detección de phishing bancario
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([3, 2, 3])
    with col_c:
        mode = st.radio("Modo", ["Iniciar sesión", "Registrarse"], horizontal=True, label_visibility="collapsed")

        if mode == "Iniciar sesión":
            with st.form("login_form"):
                username = st.text_input("Usuario")
                password = st.text_input("Contraseña", type="password")
                submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Completa todos los campos.")
                else:
                    try:
                        resp = httpx.post(
                            f"{API_BASE_URL}/auth/login",
                            data={"username": username, "password": password},
                            timeout=10.0,
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state["token"]    = data["access_token"]
                            st.session_state["username"] = data["username"]
                            st.session_state["role"]     = data["role"]
                            st.rerun()
                        else:
                            st.error("Usuario o contraseña incorrectos.")
                    except Exception:
                        st.error("No se pudo conectar con el servidor.")

        else:
            with st.form("register_form"):
                new_user  = st.text_input("Nombre de usuario")
                new_email = st.text_input("Correo electrónico")
                new_pass  = st.text_input("Contraseña (mín. 8 caracteres)", type="password")
                new_pass2 = st.text_input("Confirmar contraseña", type="password")
                submitted = st.form_submit_button("Crear cuenta", type="primary", use_container_width=True)

            if submitted:
                if not all([new_user, new_email, new_pass, new_pass2]):
                    st.error("Completa todos los campos.")
                elif new_pass != new_pass2:
                    st.error("Las contraseñas no coinciden.")
                elif len(new_pass) < 8:
                    st.error("La contraseña debe tener al menos 8 caracteres.")
                else:
                    try:
                        resp = httpx.post(
                            f"{API_BASE_URL}/auth/register",
                            json={"username": new_user, "email": new_email, "password": new_pass},
                            timeout=10.0,
                        )
                        if resp.status_code == 201:
                            st.success("Cuenta creada. Inicia sesión.")
                        else:
                            detail = resp.json().get("detail", "Error al registrar.")
                            st.error(detail)
                    except Exception:
                        st.error("No se pudo conectar con el servidor.")


# ── Verificar sesión ──────────────────────────────────────────────────────────

if "token" not in st.session_state:
    _auth_page()
    st.stop()

# ── Logo + header ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:28px">
  <div style="display:flex;align-items:center;gap:18px">
    <div style="background:#F5C518;border-radius:14px;width:58px;height:58px;
                display:flex;flex-direction:column;align-items:center;justify-content:center;
                font-size:20px;font-weight:900;color:#1A1A1A;letter-spacing:1px;line-height:1.05;
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
                box-shadow:0 3px 14px rgba(245,197,24,0.45)">
      PG<span style="font-size:8px;font-weight:700;opacity:0.65;letter-spacing:0.5px">NLP</span>
    </div>
    <div>
      <div style="font-size:26px;font-weight:900;color:#1A1A1A;letter-spacing:0.3px;
                  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;line-height:1.1">
        PhishGuard NLP
      </div>
      <div style="font-size:13px;color:#AAAAAA;font-weight:600;margin-top:2px;
                  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif">
        Detección de phishing
      </div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:12px">
    <span style="font-size:12px;color:#AAAAAA;font-weight:700;letter-spacing:1px;
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif">
      {st.session_state.get("username","").upper()}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# Botón de cerrar sesión
col_sp, col_logout = st.columns([10, 1])
with col_logout:
    if st.button("Salir", key="logout_btn"):
        for k in ("token", "username", "role"):
            st.session_state.pop(k, None)
        st.rerun()

# ── Navegacion como tabs ──────────────────────────────────────────────────────
_is_admin = st.session_state.get("role") == "admin"
_tab_labels = ["  PANEL  ", "  DATOS  "] + (["  ADMIN  "] if _is_admin else [])
_tabs = st.tabs(_tab_labels)

with _tabs[0]:
    from src.ui.pages.home import render
    render()

with _tabs[1]:
    from src.ui.pages.trends import render as render_trends
    render_trends()

if _is_admin:
    with _tabs[2]:
        from src.ui.pages.admin import render as render_admin
        render_admin()
