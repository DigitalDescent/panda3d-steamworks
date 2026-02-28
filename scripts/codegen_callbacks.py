"""
Callback and async method code generation support (Python callable approach).

Extends the base code generator with:
- Async methods that accept a Python callable (PyObject *callback)
- CCallResult handlers that invoke the callable with a Python dict
- Broadcast callback listeners that dispatch to registered Python callables
- SteamCallbackManager class for callback processing and registration

Python usage:

    # Async method - pass a callback function directly
    def on_lobby_list(result):
        print(f"Found {result['lobbies_matching']} lobbies")
    SteamMatchmaking.request_lobby_list(on_lobby_list)

    # Broadcast callback - listen via Panda3D messenger
    def on_overlay(data):
        print(f"Overlay {'opened' if data['active'] else 'closed'}")
    self.accept("Steam-GameOverlayActivated", on_overlay)

After modifying this file, re-run the code generator:
    ppython scripts/codegen.py
"""

from __future__ import print_function

import os
import re

import jinja2

import codegen_config as cfg


# ========================================================================
# Steam type -> PyObject* conversion map
# ========================================================================
# {src} is replaced with the C++ source expression,
# e.g. "pResult->m_nLobbiesMatching".

_FIELD_TO_PY = {
    "bool":      "PyBool_FromLong((long)({src}))",
    "int":       "PyLong_FromLong((long)({src}))",
    "int32":     "PyLong_FromLong((long)({src}))",
    "uint32":    "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "uint64":    "PyLong_FromUnsignedLongLong((unsigned long long)({src}))",
    "int64":     "PyLong_FromLongLong((long long)({src}))",
    "uint16":    "PyLong_FromLong((long)({src}))",
    "uint8":     "PyLong_FromLong((long)({src}))",
    "float":     "PyFloat_FromDouble((double)({src}))",
    "double":    "PyFloat_FromDouble((double)({src}))",
    "CSteamID":  "PyLong_FromUnsignedLongLong(({src}).ConvertToUint64())",
    "const char *": "PyUnicode_FromString(({src}) ? ({src}) : \"\")",
    "EResult":   "PyLong_FromLong((long)({src}))",
    "AppId_t":   "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "DepotId_t": "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "PublishedFileId_t": "PyLong_FromUnsignedLongLong((unsigned long long)({src}))",
    "SteamLeaderboard_t": "PyLong_FromUnsignedLongLong((unsigned long long)({src}))",
    "SteamLeaderboardEntries_t": "PyLong_FromUnsignedLongLong((unsigned long long)({src}))",
    "UGCHandle_t": "PyLong_FromUnsignedLongLong((unsigned long long)({src}))",
    "UGCQueryHandle_t": "PyLong_FromUnsignedLongLong((unsigned long long)({src}))",
    "SteamInventoryResult_t": "PyLong_FromLong((long)({src}))",
    "ScreenshotHandle": "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "AccountID_t": "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "RTime32":   "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "HAuthTicket": "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "HTTPRequestHandle": "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "HHTMLBrowser": "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "InputHandle_t": "PyLong_FromUnsignedLongLong((unsigned long long)({src}))",
    "PartyBeaconID_t": "PyLong_FromUnsignedLongLong((unsigned long long)({src}))",
    "SteamAPICall_t": "PyLong_FromUnsignedLongLong((unsigned long long)({src}))",
    "RemotePlaySessionID_t": "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "SNetSocket_t": "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "SNetListenSocket_t": "PyLong_FromUnsignedLong((unsigned long)({src}))",
    "HSteamNetConnection": "PyLong_FromUnsignedLong((unsigned long)({src}))",
}


# ========================================================================
# Naming helpers
# ========================================================================

def _camel_to_snake(name):
    """PascalCase/camelCase to snake_case."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower()


def _strip_field_prefix(field_name):
    """Strip m_ prefix and Hungarian notation from a callback field name."""
    name = field_name
    if name.startswith("m_"):
        name = name[2:]

    prefixes = [
        "ppch", "ppsz",
        "pch", "psz", "pfn", "pfl", "pun", "pub", "pvec",
        "rgb", "rgf", "rg",
        "pp", "pb", "pn", "pi", "pf",
        "fl", "un", "ul",
        "cb", "cch", "cub",
        "sz", "ch", "fn",
        "p", "n", "b", "e", "i", "c", "f",
        "h",
    ]
    for pfx in prefixes:
        if (name.startswith(pfx)
                and len(name) > len(pfx)
                and name[len(pfx)].isupper()):
            return name[len(pfx):]
    return name


def field_to_dict_key(field_name):
    """Convert a callback field name to a Python dict key.

    m_nLobbiesMatching -> lobbies_matching
    m_ulSteamIDLobby   -> steam_id_lobby
    """
    return _camel_to_snake(_strip_field_prefix(field_name))


def broadcast_name(struct_name):
    """Return the registration name for a broadcast callback.

    GameOverlayActivated_t -> GameOverlayActivated
    """
    if struct_name.endswith("_t"):
        return struct_name[:-2]
    return struct_name


# ========================================================================
# Field type resolution
# ========================================================================

def _resolve_field_py_expr(ftype, src, typedefs, enums):
    """Resolve a field type + C++ source expression to a PyObject* conversion.

    Returns a C expression string that evaluates to a new-reference PyObject*,
    or None if the field type is not supported.
    """
    # char arrays: "char [256]" etc.
    if re.match(r"char\s*\[\d+\]", ftype):
        return "PyUnicode_FromString({})".format(src)

    # Direct lookup
    if ftype in _FIELD_TO_PY:
        return _FIELD_TO_PY[ftype].format(src=src)

    # Typedef resolution (one level)
    if ftype in typedefs and typedefs[ftype] in _FIELD_TO_PY:
        return _FIELD_TO_PY[typedefs[ftype]].format(src=src)

    # Enum -> int
    if ftype in enums:
        return "PyLong_FromLong((long)({src}))".format(src=src)

    # Config overrides (extensibility hook)
    overrides = getattr(cfg, "PY_FIELD_OVERRIDES", {})
    if ftype in overrides:
        return overrides[ftype].format(src=src)

    return None  # unsupported


# ========================================================================
# Callback struct helpers
# ========================================================================

def build_callback_struct_map(api_data):
    """Build {struct_name: struct_data} from callback_structs in the API JSON."""
    result = {}
    for cs in api_data.get("callback_structs", []):
        result[cs["struct"]] = cs
    return result


def collect_callresult_structs(api_data):
    """Collect all callback struct names referenced as callresults by async methods."""
    skip = getattr(cfg, "SKIP_CALLBACK_STRUCTS", set())
    result = set()
    for iface in api_data.get("interfaces", []):
        for method in iface.get("methods", []):
            if method["returntype"] == "SteamAPICall_t":
                cr = method.get("callresult", "")
                if cr and cr not in skip:
                    result.add(cr)
    return result


def collect_broadcast_structs():
    """Return the set of callback struct names configured for broadcast listening."""
    skip = getattr(cfg, "SKIP_CALLBACK_STRUCTS", set())
    return {
        name for name in getattr(cfg, "BROADCAST_CALLBACKS", [])
        if name not in skip
    }


# ========================================================================
# Jinja2 template environment
# ========================================================================

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_TEMPLATES_DIR = os.path.join(_SCRIPT_DIR, "templates")

_jinja_env = None


def _get_jinja_env():
    """Return (and cache) a Jinja2 Environment pointing at scripts/templates/."""
    global _jinja_env
    if _jinja_env is None:
        _jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(_TEMPLATES_DIR),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
    return _jinja_env


# ========================================================================
# Dict entry preparation (for templates)
# ========================================================================

def _prepare_dict_entries(struct_data, typedefs, enums, src_var="pResult"):
    """Build a list of {key, py_expr} dicts for template rendering.

    Each entry represents one field of a callback struct that should be
    added to a Python dict.  Unsupported field types are skipped.
    """
    entries = []
    for field in struct_data.get("fields", []):
        ftype = field["fieldtype"].strip()
        fname = field["fieldname"]
        dict_key = field_to_dict_key(fname)
        src = "{}->{}".format(src_var, fname)

        py_expr = _resolve_field_py_expr(ftype, src, typedefs, enums)
        if py_expr is None:
            continue

        entries.append({"key": dict_key, "py_expr": py_expr})
    return entries


# ========================================================================
# Code generation: steamPython.h
# ========================================================================

def generate_python_compat_header(banner):
    """Generate steamPython_bindings.h via Jinja2 template."""
    env = _get_jinja_env()
    tmpl = env.get_template("python_compat_header.h.j2")
    return tmpl.render(banner=banner)


# ========================================================================
# Code generation: steamCallbackManager.h
# ========================================================================

def generate_callback_manager_header(banner):
    """Generate steamCallbackManager_bindings.h via Jinja2 template."""
    env = _get_jinja_env()
    tmpl = env.get_template("callback_manager_header.h.j2")
    return tmpl.render(banner=banner)


# ========================================================================
# Code generation: steamCallbackManager.cpp
# ========================================================================

def generate_callback_manager_source(async_struct_names,
                                     broadcast_struct_names,
                                     callback_struct_map,
                                     typedefs, enums, banner):
    """Generate steamCallbackManager_bindings.cpp via Jinja2 template."""
    env = _get_jinja_env()
    tmpl = env.get_template("callback_manager_source.cpp.j2")

    skip = getattr(cfg, "SKIP_CALLBACK_STRUCTS", set())
    event_prefix = getattr(cfg, "BROADCAST_EVENT_PREFIX", "Steam-")

    # Prepare async struct contexts
    async_structs = []
    for struct_name in sorted(async_struct_names):
        if struct_name in skip:
            continue
        struct_data = callback_struct_map.get(struct_name)
        if struct_data is None:
            continue
        async_structs.append({
            "name": struct_name,
            "handler_name": "_PendingCall_{}".format(struct_name),
            "dict_entries": _prepare_dict_entries(
                struct_data, typedefs, enums, src_var="pResult"),
        })

    # Prepare broadcast struct contexts
    broadcast_structs = []
    for struct_name in sorted(broadcast_struct_names):
        if struct_name in skip:
            continue
        struct_data = callback_struct_map.get(struct_name)
        if struct_data is None:
            continue
        broadcast_structs.append({
            "name": struct_name,
            "handler_fn": "_On_{}".format(struct_name),
            "cb_member": "_cb_{}".format(struct_name),
            "event_name": "{}{}".format(event_prefix,
                                        broadcast_name(struct_name)),
            "dict_entries": _prepare_dict_entries(
                struct_data, typedefs, enums, src_var="pParam"),
        })

    return tmpl.render(
        banner=banner,
        async_structs=async_structs,
        broadcast_structs=broadcast_structs,
    )
