"""UI helpers untuk COVID-19 Dashboard.

Tujuan:
- Konsisten antar halaman (HCI: hierarki, feedback sistem, pencegahan error)
- Minim HTML custom agar tampilan terasa natural (tidak 'template')
- Clean code: helper kecil, mudah diuji/dirawat
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, Optional
import inspect
import json
import base64
import zlib

import streamlit as st


def get_streamlit_theme_base(*, default: str = "light") -> str:
    """Best-effort read Streamlit's configured theme base."""
    try:
        from streamlit import config
        base = config.get_option("theme.base")
        if base:
            return str(base).lower()
    except Exception:
        pass
    return default


def kw_plotly_chart() -> dict:
    """Kwargs for st.plotly_chart (version-tolerant full width)."""
    return kw_full_width(st.plotly_chart)


def kw_full_width(fn: Callable[..., object]) -> dict:
    """Return kwargs for 'full width' rendering across Streamlit versions."""
    try:
        sig = inspect.signature(fn)
        if "width" in sig.parameters:
            return {"width": "stretch"}
        return {"use_container_width": True}
    except Exception:
        return {"use_container_width": True}


def _kw_button_type(fn: Callable[..., object], btn_type: str | None) -> dict:
    """Return kwargs for button type across Streamlit versions."""
    if btn_type is None:
        return {}
    try:
        sig = inspect.signature(fn)
        if "type" in sig.parameters:
            return {"type": btn_type}
    except Exception:
        pass
    return {}


def button(
    label: str,
    *,
    key: str,
    kind: str | None = None,
    full_width: bool = True,
    disabled: bool = False,
    help: str | None = None,
) -> bool:
    """Wrapper untuk st.button yang version-tolerant + konsisten."""
    kwargs = _kw_button_type(st.button, kind)
    if full_width:
        kwargs.update(kw_full_width(st.button))
    return st.button(label, key=key, disabled=disabled, help=help, **kwargs)


def secondary_button(
    label: str,
    *,
    key: str,
    full_width: bool = True,
    disabled: bool = False,
    help: str | None = None,
) -> bool:
    """Secondary action button (visual hierarchy)."""
    return button(
        label,
        key=key,
        kind="secondary",
        full_width=full_width,
        disabled=disabled,
        help=help,
    )


def danger_button(
    label: str,
    *,
    key: str,
    full_width: bool = True,
    disabled: bool = False,
    help: str | None = None,
) -> bool:
    """Destructive action button (error prevention)."""
    return button(
        label,
        key=key,
        kind="primary",
        full_width=full_width,
        disabled=disabled,
        help=help,
    )


def request_navigation(page_label: str, *, key: str = "app_page") -> None:
    """Minta navigasi ke halaman tertentu dengan aman."""
    st.session_state[f"_{key}_pending"] = page_label


def _json_default(obj: object) -> Any:
    """Best-effort JSON serializer for common UI state types."""
    import datetime
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    if hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes)):
        return list(obj)
    return str(obj)


def reset_state(keys: list[str]) -> None:
    """Hapus key tertentu dari session_state (untuk reset filter/view)."""
    for k in keys:
        st.session_state.pop(k, None)


def active_filters_bar(
    *,
    title: str = "Filter aktif",
    items: dict[str, object],
    reset_keys: list[str] | None = None,
    help: str | None = None,
) -> None:
    """Tampilkan ringkasan filter aktif + tombol reset yang konsisten."""
    
    def _is_empty(v: object) -> bool:
        if v is None:
            return True
        if isinstance(v, str) and v.strip() == "":
            return True
        if isinstance(v, (list, tuple)) and len(v) == 0:
            return True
        return False
    
    active = {k: v for k, v in items.items() if not _is_empty(v)}
    
    if not active:
        return
    
    with st.container():
        cols = st.columns([0.85, 0.15])
        with cols[0]:
            pills = ", ".join(f"**{k}**: {v}" for k, v in active.items())
            st.markdown(f"🔍 {title}: {pills}", help=help)
        with cols[1]:
            if reset_keys and secondary_button("Reset", key="reset_filters"):
                reset_state(reset_keys)
                st.rerun()


def section_nav(
    label: str,
    *,
    options: list[str],
    key: str,
    default: str | None = None,
) -> str:
    """Navigasi section pengganti st.tabs yang bisa dipersist/share."""
    
    if not options:
        return ""
    
    if default is None:
        default = options[0]
    
    current = st.session_state.get(key, default)
    if current not in options:
        current = default
    
    # Try segmented_control first (newer Streamlit)
    try:
        if hasattr(st, "segmented_control"):
            selected = st.segmented_control(
                label,
                options,
                default=current,
                key=key,
            )
            return selected if selected else current
    except Exception:
        pass
    
    # Fallback to radio horizontal
    idx = options.index(current) if current in options else 0
    selected = st.radio(
        label,
        options,
        index=idx,
        key=key,
        horizontal=True,
    )
    return selected if selected else current


def _encode_url_state(payload: dict) -> str:
    """Encode dict -> compact URL-safe string."""
    try:
        json_bytes = json.dumps(payload, separators=(",", ":"), default=_json_default).encode()
        compressed = zlib.compress(json_bytes, level=9)
        return base64.urlsafe_b64encode(compressed).decode().rstrip("=")
    except Exception:
        return ""


def _decode_url_state(token: str) -> dict:
    """Decode URL state token."""
    try:
        padding = 4 - len(token) % 4
        if padding != 4:
            token += "=" * padding
        compressed = base64.urlsafe_b64decode(token)
        json_bytes = zlib.decompress(compressed)
        return json.loads(json_bytes)
    except Exception:
        return {}


def _get_query_params() -> dict:
    """Get query params in a version-tolerant way."""
    try:
        if hasattr(st, "query_params"):
            return dict(st.query_params)
        return st.experimental_get_query_params()
    except Exception:
        return {}


def _set_query_params(params: dict) -> None:
    """Set query params in a version-tolerant way."""
    try:
        if hasattr(st, "query_params"):
            st.query_params.update(params)
        else:
            st.experimental_set_query_params(**params)
    except Exception:
        pass


def sync_state_from_url(
    namespace: str,
    *,
    keys: list[str],
    param: str = "state",
    coercers: dict[str, Callable[[object], object]] | None = None,
) -> None:
    """Hydrate session_state from URL query param once per session."""
    
    sentinel = f"_url_synced_{namespace}"
    if st.session_state.get(sentinel):
        return
    
    st.session_state[sentinel] = True
    
    qp = _get_query_params()
    token = qp.get(param, [""])[0] if isinstance(qp.get(param), list) else qp.get(param, "")
    
    if not token:
        return
    
    payload = _decode_url_state(str(token))
    
    coercers = coercers or {}
    
    for k in keys:
        if k in payload and k not in st.session_state:
            val = payload[k]
            if k in coercers:
                try:
                    val = coercers[k](val)
                except Exception:
                    continue
            st.session_state[k] = val


def build_share_query(
    *,
    keys: list[str],
    param: str = "state",
) -> str:
    """Build shareable query string from session state."""
    payload = {k: st.session_state.get(k) for k in keys if k in st.session_state}
    token = _encode_url_state(payload)
    return f"?{param}={token}" if token else ""


def coerce_iso_date(value: object):
    """Coerce 'YYYY-MM-DD' string -> datetime.date."""
    import datetime
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value)
        except Exception:
            pass
    return None


def _index_of(options: list, value) -> int:
    """Safe index lookup."""
    try:
        return options.index(value)
    except ValueError:
        return 0


def persisted_selectbox(
    label: str,
    *,
    options: list,
    key: str,
    default=None,
    help: str | None = None,
    disabled: bool = False,
) -> Any:
    """Selectbox dengan default yang stabil + persist antar halaman."""
    
    if not options:
        return None
    
    current = st.session_state.get(key)
    
    if current in options:
        idx = _index_of(options, current)
    elif default is not None and default in options:
        idx = _index_of(options, default)
    else:
        idx = 0
    
    return st.selectbox(
        label,
        options,
        index=idx,
        key=key,
        help=help,
        disabled=disabled,
    )


def persisted_multiselect(
    label: str,
    *,
    options: list,
    key: str,
    default: list | None = None,
    help: str | None = None,
    disabled: bool = False,
) -> list:
    """Multiselect dengan default yang stabil."""
    
    if not options:
        return []
    
    current = st.session_state.get(key)
    
    if isinstance(current, list):
        valid = [v for v in current if v in options]
        if valid:
            default_val = valid
        elif default:
            default_val = [d for d in default if d in options]
        else:
            default_val = []
    elif default:
        default_val = [d for d in default if d in options]
    else:
        default_val = []
    
    return st.multiselect(
        label,
        options,
        default=default_val,
        key=key,
        help=help,
        disabled=disabled,
    )


def metric_card(
    label: str,
    value: str | int | float,
    delta: str | None = None,
    delta_color: str = "normal",
    help: str | None = None,
) -> None:
    """Display a metric using st.metric."""
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help,
    )


def info_callout(message: str, icon: str = "ℹ️") -> None:
    """Display an info callout."""
    st.info(f"{icon} {message}")


def warning_callout(message: str, icon: str = "⚠️") -> None:
    """Display a warning callout."""
    st.warning(f"{icon} {message}")


def success_callout(message: str, icon: str = "✅") -> None:
    """Display a success callout."""
    st.success(f"{icon} {message}")


def error_callout(message: str, icon: str = "❌") -> None:
    """Display an error callout."""
    st.error(f"{icon} {message}")
