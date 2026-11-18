from __future__ import annotations

import httpx
import streamlit as st
from config.settings import API_BASE_URL


def _headers() -> dict:
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


def _fetch_users() -> list[dict]:
    try:
        r = httpx.get(f"{API_BASE_URL}/auth/users", headers=_headers(), timeout=8.0)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def render() -> None:
    if st.session_state.get("role") != "admin":
        st.markdown(
            '<div style="text-align:center;padding:60px 0;color:#AAA;font-size:14px;font-weight:600">'
            'Acceso restringido a administradores.</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="sec-title">Gestión de usuarios</div>', unsafe_allow_html=True)

    # ── Crear usuario ─────────────────────────────────────────────────────────
    with st.expander("Crear nuevo usuario", expanded=False):
        with st.form("form_create_user", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nu_user  = st.text_input("Nombre de usuario")
                nu_pass  = st.text_input("Contraseña (mín. 8 caracteres)", type="password")
            with c2:
                nu_email = st.text_input("Correo electrónico")
                nu_role  = st.selectbox("Rol", ["user", "admin"])
            submitted = st.form_submit_button("Crear usuario", type="primary", use_container_width=True)

        if submitted:
            if not all([nu_user, nu_email, nu_pass]):
                st.error("Completa todos los campos.")
            elif len(nu_pass) < 8:
                st.error("La contraseña debe tener al menos 8 caracteres.")
            else:
                try:
                    resp = httpx.post(
                        f"{API_BASE_URL}/auth/users",
                        json={"username": nu_user, "email": nu_email,
                              "password": nu_pass, "role": nu_role},
                        headers=_headers(),
                        timeout=8.0,
                    )
                    if resp.status_code == 201:
                        st.success(f"Usuario '{nu_user}' creado correctamente.")
                        st.rerun()
                    else:
                        st.error(resp.json().get("detail", "Error al crear usuario."))
                except Exception:
                    st.error("No se pudo conectar con el servidor.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Lista de usuarios ─────────────────────────────────────────────────────
    users = _fetch_users()

    if not users:
        st.markdown(
            '<div style="text-align:center;padding:40px 0;color:#AAA;font-size:13px">'
            'No hay usuarios registrados o no se pudo conectar.</div>',
            unsafe_allow_html=True,
        )
        return

    current_username = st.session_state.get("username", "")

    # Cabecera
    st.markdown(
        f'<div style="display:grid;grid-template-columns:2fr 2fr 1fr 1.5fr 1fr 1fr;'
        f'gap:8px;padding:8px 12px;background:#C0C0C0;border-radius:6px 6px 0 0;'
        f'font-size:10px;font-weight:800;color:#666;text-transform:uppercase;letter-spacing:1px">'
        f'<span>Usuario</span><span>Correo</span><span>Rol</span>'
        f'<span>Creado</span><span>Contraseña</span><span>Eliminar</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    for u in users:
        is_self = u["username"] == current_username
        role_color = "#F5C518" if u["role"] == "admin" else "#888"
        role_bg    = "#FFF9C4" if u["role"] == "admin" else "#E5E5E5"
        created    = u["created_at"][:10] if u.get("created_at") else "—"

        col_user, col_email, col_role, col_date, col_pw, col_del = st.columns(
            [2, 2, 1, 1.5, 1, 1], gap="small"
        )

        with col_user:
            suffix = " (tú)" if is_self else ""
            st.markdown(
                f'<div style="padding:10px 4px;font-size:13px;font-weight:700;color:#1A1A1A">'
                f'{u["username"]}{suffix}</div>',
                unsafe_allow_html=True,
            )

        with col_email:
            st.markdown(
                f'<div style="padding:10px 4px;font-size:12px;color:#555;word-break:break-all">'
                f'{u["email"]}</div>',
                unsafe_allow_html=True,
            )

        with col_role:
            st.markdown(
                f'<div style="padding:10px 4px">'
                f'<span style="background:{role_bg};color:{role_color};border-radius:4px;'
                f'padding:3px 8px;font-size:11px;font-weight:800">{u["role"].upper()}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with col_date:
            st.markdown(
                f'<div style="padding:10px 4px;font-size:12px;color:#888">{created}</div>',
                unsafe_allow_html=True,
            )

        with col_pw:
            if st.button("Cambiar", key=f"pw_{u['id']}", use_container_width=True):
                st.session_state[f"_pw_modal_{u['id']}"] = True

        with col_del:
            if is_self:
                st.markdown(
                    '<div style="padding:10px 4px;font-size:11px;color:#CCC">—</div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button("Eliminar", key=f"del_{u['id']}", use_container_width=True,
                             type="secondary"):
                    st.session_state[f"_confirm_del_{u['id']}"] = True

        # ── Confirmación de eliminación inline ────────────────────────────────
        if st.session_state.get(f"_confirm_del_{u['id']}"):
            st.markdown(
                f'<div style="background:#FEF2F2;border:2px solid #FECACA;border-radius:8px;'
                f'padding:12px 16px;margin:4px 0;font-size:13px;color:#B91C1C;font-weight:700">'
                f'Confirmar eliminación de "{u["username"]}"</div>',
                unsafe_allow_html=True,
            )
            cc1, cc2, cc3 = st.columns([1, 1, 4])
            with cc1:
                if st.button("Sí, eliminar", key=f"confirm_yes_{u['id']}", type="primary"):
                    try:
                        r = httpx.delete(
                            f"{API_BASE_URL}/auth/users/{u['id']}",
                            headers=_headers(), timeout=8.0,
                        )
                        if r.status_code == 200:
                            st.session_state.pop(f"_confirm_del_{u['id']}", None)
                            st.success(f"Usuario '{u['username']}' eliminado.")
                            st.rerun()
                        else:
                            st.error(r.json().get("detail", "Error al eliminar."))
                    except Exception:
                        st.error("No se pudo conectar.")
            with cc2:
                if st.button("Cancelar", key=f"confirm_no_{u['id']}"):
                    st.session_state.pop(f"_confirm_del_{u['id']}", None)
                    st.rerun()

        # ── Modal cambio de contraseña inline ─────────────────────────────────
        if st.session_state.get(f"_pw_modal_{u['id']}"):
            with st.form(f"form_pw_{u['id']}"):
                st.markdown(
                    f'<div style="font-size:13px;font-weight:700;color:#333;margin-bottom:8px">'
                    f'Nueva contraseña para "{u["username"]}"</div>',
                    unsafe_allow_html=True,
                )
                new_pw = st.text_input("Nueva contraseña", type="password",
                                       key=f"new_pw_input_{u['id']}")
                c_ok, c_cancel = st.columns(2)
                with c_ok:
                    save = st.form_submit_button("Guardar", type="primary", use_container_width=True)
                with c_cancel:
                    cancel = st.form_submit_button("Cancelar", use_container_width=True)

            if save:
                if len(new_pw) < 8:
                    st.error("Mínimo 8 caracteres.")
                else:
                    try:
                        r = httpx.put(
                            f"{API_BASE_URL}/auth/users/{u['id']}/password",
                            json={"new_password": new_pw},
                            headers=_headers(), timeout=8.0,
                        )
                        if r.status_code == 200:
                            st.session_state.pop(f"_pw_modal_{u['id']}", None)
                            st.success("Contraseña actualizada.")
                            st.rerun()
                        else:
                            st.error(r.json().get("detail", "Error al actualizar."))
                    except Exception:
                        st.error("No se pudo conectar.")
            if cancel:
                st.session_state.pop(f"_pw_modal_{u['id']}", None)
                st.rerun()

        st.markdown('<hr style="border:none;border-top:1px solid #D0D0D0;margin:0">', unsafe_allow_html=True)

    st.markdown(
        f'<div style="font-size:11px;color:#AAA;text-align:right;margin-top:8px">'
        f'{len(users)} usuario{"s" if len(users) != 1 else ""} registrado{"s" if len(users) != 1 else ""}</div>',
        unsafe_allow_html=True,
    )
