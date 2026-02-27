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

import re

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
# Code generation: Python dict builder from callback struct fields
# ========================================================================

def _gen_dict_builder(lines, indent, struct_data, typedefs, enums,
                      src_var="pResult", include_io_failure=False):
    """Generate C++ code that builds a PyObject* dict from callback fields.

    Appends lines that create a local ``dict`` variable.  The caller is
    responsible for passing it to the Python callback and Py_DECREF'ing it.

    Parameters
    ----------
    src_var : str
        Name of the C++ pointer variable, e.g. ``"pResult"``.
    include_io_failure : bool
        If True, adds ``"io_failure"`` key from a ``bIOFailure`` local.
    """
    lines.append("{}PyObject *dict = PyDict_New();".format(indent))
    lines.append("{}PyObject *val;".format(indent))

    for field in struct_data.get("fields", []):
        ftype = field["fieldtype"].strip()
        fname = field["fieldname"]
        dict_key = field_to_dict_key(fname)
        src = "{}->{}".format(src_var, fname)

        py_expr = _resolve_field_py_expr(ftype, src, typedefs, enums)
        if py_expr is None:
            continue  # skip unsupported field

        lines.append("{}val = {};".format(indent, py_expr))
        lines.append('{}PyDict_SetItemString(dict, "{}", val);'.format(
            indent, dict_key))
        lines.append("{}Py_DECREF(val);".format(indent))

    if include_io_failure:
        lines.append("{}val = bIOFailure ? Py_True : Py_False;".format(indent))
        lines.append("{}Py_INCREF(val);".format(indent))
        lines.append('{}PyDict_SetItemString(dict, "io_failure", val);'.format(
            indent))
        lines.append("{}Py_DECREF(val);".format(indent))


# ========================================================================
# Code generation: steamPython.h
# ========================================================================

def generate_python_compat_header(banner):
    """Generate steamPython.h: provides PyObject for both interrogate and C++."""
    lines = [banner, ""]
    lines.append("#pragma once")
    lines.append("")
    lines.append("// Provide a PyObject declaration that works for both")
    lines.append("// interrogate (CPPPARSER) and normal C++ compilation.")
    lines.append("#ifdef CPPPARSER")
    lines.append("struct _object;")
    lines.append("typedef _object PyObject;")
    lines.append("#else")
    lines.append("#include <Python.h>")
    lines.append("#endif")
    lines.append("")
    return "\n".join(lines)


# ========================================================================
# Code generation: steamCallbackManager.h
# ========================================================================

def generate_callback_manager_header(banner):
    """Generate the steamCallbackManager.h header.

    This is a tiny header -- all heavy lifting lives in the .cpp behind
    ``#ifndef CPPPARSER``.

    Broadcast callbacks fire as Panda3D messenger events so users can
    use the familiar ``self.accept()`` / ``self.ignore()`` pattern.
    """
    lines = [banner, ""]
    lines.append("#pragma once")
    lines.append("")
    lines.append('#include "pandabase.h"')
    lines.append('#include "steamPython.h"')
    lines.append("#include <string>")
    lines.append("")
    lines.append("/" * 68)
    lines.append("//       Class : SteamCallbackManager")
    lines.append("// Description : Manages Steamworks async call-result")
    lines.append("//               dispatching and broadcast callback")
    lines.append("//               events.  Call run_callbacks() every")
    lines.append("//               frame from a Panda3D task.")
    lines.append("//")
    lines.append("//               Broadcast callbacks are delivered as")
    lines.append("//               Panda3D events via the messenger.")
    lines.append("//               Use self.accept() / self.ignore().")
    lines.append("/" * 68)
    lines.append("class EXPORT_CLASS SteamCallbackManager {")
    lines.append("PUBLISHED:")
    lines.append("  // Process pending Steam callbacks.  Call every frame.")
    lines.append("  // On the first call, broadcast listeners are")
    lines.append("  // automatically registered with Steam.")
    lines.append("  static void run_callbacks();")
    lines.append("")
    lines.append("  // Shut down all listeners and cancel pending async calls.")
    lines.append("  static void shutdown();")
    lines.append("")
    lines.append("private:")
    lines.append("  SteamCallbackManager() = delete;")
    lines.append("};")
    lines.append("")
    return "\n".join(lines)


# ========================================================================
# Code generation: steamCallbackManager.cpp
# ========================================================================

def generate_callback_manager_source(async_struct_names,
                                     broadcast_struct_names,
                                     callback_struct_map,
                                     typedefs, enums, banner):
    """Generate steamCallbackManager.cpp.

    Contains:
    - ``_PendingCall_<StructName>`` handlers for each async call-result type
    - Registration functions: ``_steam_async_call_<StructName>(call, callback)``
    - ``_BroadcastHandler`` class with CCallback members
    - ``SteamCallbackManager`` implementation
    """
    lines = [banner, ""]
    lines.append('#include "steamCallbackManager.h"')
    lines.append("")
    lines.append("// Guard implementation from interrogate.")
    lines.append("#ifndef CPPPARSER")
    lines.append("")
    lines.append("#include <steam/steam_api.h>")
    lines.append("#include <steam/steam_gameserver.h>")
    lines.append("#include <Python.h>")
    lines.append("#include <vector>")
    lines.append("#include <string>")
    lines.append("")

    skip = getattr(cfg, "SKIP_CALLBACK_STRUCTS", set())

    # ---- Collect generatable structs ----
    gen_async = []  # (struct_name, struct_data)
    for struct_name in sorted(async_struct_names):
        if struct_name in skip:
            continue
        struct_data = callback_struct_map.get(struct_name)
        if struct_data is None:
            continue
        gen_async.append((struct_name, struct_data))

    gen_broadcast = []  # (struct_name, struct_data)
    for struct_name in sorted(broadcast_struct_names):
        if struct_name in skip:
            continue
        struct_data = callback_struct_map.get(struct_name)
        if struct_data is None:
            continue
        gen_broadcast.append((struct_name, struct_data))

    # ==================================================================
    # Pending async call result handlers
    # ==================================================================
    for struct_name, struct_data in gen_async:
        handler = "_PendingCall_{}".format(struct_name)

        lines.append("// " + "-" * 60)
        lines.append("// Async result handler: {}".format(struct_name))
        lines.append("// " + "-" * 60)
        lines.append("")
        lines.append("struct {} {{".format(handler))
        lines.append("  CCallResult<{}, {}> call_result;".format(
            handler, struct_name))
        lines.append("  PyObject *py_callback;")
        lines.append("  bool completed;")
        lines.append("")
        lines.append("  {}(SteamAPICall_t call, PyObject *cb)".format(handler))
        lines.append("    : py_callback(cb), completed(false) {")
        lines.append("    Py_XINCREF(py_callback);")
        lines.append("    call_result.Set(call, this, &{}::OnComplete);".format(
            handler))
        lines.append("  }")
        lines.append("")
        lines.append("  ~{}() {{".format(handler))
        lines.append("    Py_XDECREF(py_callback);")
        lines.append("  }")
        lines.append("")
        lines.append("  void OnComplete({} *pResult, bool bIOFailure) {{".format(
            struct_name))
        lines.append("    if (py_callback && py_callback != Py_None"
                     " && PyCallable_Check(py_callback)) {")

        _gen_dict_builder(lines, "      ", struct_data, typedefs, enums,
                          src_var="pResult", include_io_failure=True)

        lines.append("      PyObject *ret = PyObject_CallFunctionObjArgs("
                     "py_callback, dict, NULL);")
        lines.append("      if (!ret) PyErr_Print();")
        lines.append("      Py_XDECREF(ret);")
        lines.append("      Py_DECREF(dict);")
        lines.append("    }")
        lines.append("    completed = true;")
        lines.append("  }")
        lines.append("};")
        lines.append("")

        # Vector + registration function
        lines.append("static std::vector<{}*> _pending_{};".format(
            handler, struct_name))
        lines.append("")
        lines.append(
            "void _steam_async_call_{name}("
            "SteamAPICall_t call, PyObject *callback) {{".format(
                name=struct_name))
        lines.append("  auto *h = new {}(call, callback);".format(handler))
        lines.append("  _pending_{}.push_back(h);".format(struct_name))
        lines.append("}")
        lines.append("")

    # ==================================================================
    # Cleanup helpers
    # ==================================================================
    lines.append("static void _cleanup_completed_calls() {")
    for struct_name, _ in gen_async:
        vec = "_pending_{}".format(struct_name)
        lines.append(
            "  for (auto it = {v}.begin(); it != {v}.end(); ) {{".format(
                v=vec))
        lines.append("    if ((*it)->completed) {")
        lines.append("      delete *it;")
        lines.append("      it = {}.erase(it);".format(vec))
        lines.append("    } else {")
        lines.append("      ++it;")
        lines.append("    }")
        lines.append("  }")
    lines.append("}")
    lines.append("")

    lines.append("static void _cancel_all_pending_calls() {")
    for struct_name, _ in gen_async:
        vec = "_pending_{}".format(struct_name)
        lines.append("  for (auto *p : {}) delete p;".format(vec))
        lines.append("  {}.clear();".format(vec))
    lines.append("}")
    lines.append("")

    # ==================================================================
    # Messenger helper (sends Panda3D events from C++)
    # ==================================================================
    event_prefix = getattr(cfg, "BROADCAST_EVENT_PREFIX", "Steam-")

    if gen_broadcast:
        lines.append("// " + "=" * 60)
        lines.append("// Panda3D messenger integration")
        lines.append("// " + "=" * 60)
        lines.append("")
        lines.append("static PyObject *_py_messenger = nullptr;")
        lines.append("")
        lines.append("static void _ensure_messenger() {")
        lines.append("  if (_py_messenger) return;")
        lines.append('  PyObject *mod = PyImport_ImportModule('
                     '"direct.showbase.MessengerGlobal");')
        lines.append("  if (!mod) { PyErr_Print(); return; }")
        lines.append('  _py_messenger = PyObject_GetAttrString(mod, '
                     '"messenger");')
        lines.append("  Py_DECREF(mod);")
        lines.append("  if (!_py_messenger) PyErr_Print();")
        lines.append("}")
        lines.append("")
        lines.append("static void _send_event("
                     "const char *name, PyObject *dict) {")
        lines.append("  _ensure_messenger();")
        lines.append("  if (!_py_messenger) return;")
        lines.append("  PyObject *args_list = PyList_New(1);")
        lines.append("  Py_INCREF(dict);")
        lines.append("  PyList_SET_ITEM(args_list, 0, dict);")
        lines.append('  PyObject *ret = PyObject_CallMethod('
                     '_py_messenger, "send", "sO", name, args_list);')
        lines.append("  if (!ret) PyErr_Print();")
        lines.append("  Py_XDECREF(ret);")
        lines.append("  Py_DECREF(args_list);")
        lines.append("}")
        lines.append("")

    # ==================================================================
    # Broadcast callback handler
    # ==================================================================
    if gen_broadcast:
        lines.append("// " + "=" * 60)
        lines.append("// Broadcast callback handler")
        lines.append("// " + "=" * 60)
        lines.append("")
        lines.append("class _BroadcastHandler {")
        lines.append("public:")

        # Constructor initializer list
        init_parts = []
        for struct_name, _ in gen_broadcast:
            cb = "_cb_{}".format(struct_name)
            fn = "_On_{}".format(struct_name)
            init_parts.append(
                "    {}(this, &_BroadcastHandler::{})".format(cb, fn))

        lines.append("  _BroadcastHandler() :")
        lines.append(",\n".join(init_parts))
        lines.append("  {}")
        lines.append("")

        # Callback handlers -- build dict and send as Panda event
        for struct_name, struct_data in gen_broadcast:
            fn = "_On_{}".format(struct_name)
            event_name = "{}{}".format(event_prefix,
                                       broadcast_name(struct_name))
            lines.append("  void {}({} *pParam) {{".format(fn, struct_name))

            _gen_dict_builder(lines, "    ", struct_data, typedefs, enums,
                              src_var="pParam", include_io_failure=False)

            lines.append('    _send_event("{}", dict);'.format(event_name))
            lines.append("    Py_DECREF(dict);")
            lines.append("  }")
            lines.append("")

        # Private members -- only CCallback instances, no stored PyObject*
        lines.append("private:")
        for struct_name, _ in gen_broadcast:
            cb = "_cb_{}".format(struct_name)
            lines.append(
                "  CCallback<_BroadcastHandler, {}, false> {};".format(
                    struct_name, cb))
        lines.append("};")
        lines.append("")
        lines.append(
            "static _BroadcastHandler *_g_broadcast_handler = nullptr;")
        lines.append("")

    # ==================================================================
    # SteamCallbackManager implementation
    # ==================================================================
    lines.append("// " + "=" * 60)
    lines.append("// SteamCallbackManager implementation")
    lines.append("// " + "=" * 60)
    lines.append("")

    # run_callbacks -- auto-inits broadcast handler on first call
    lines.append("void SteamCallbackManager::run_callbacks() {")
    if gen_broadcast:
        lines.append("  if (!_g_broadcast_handler) {")
        lines.append("    _g_broadcast_handler = new _BroadcastHandler();")
        lines.append("  }")
    lines.append("  SteamAPI_RunCallbacks();")
    lines.append("  _cleanup_completed_calls();")
    lines.append("}")
    lines.append("")

    # shutdown
    lines.append("void SteamCallbackManager::shutdown() {")
    if gen_broadcast:
        lines.append("  delete _g_broadcast_handler;")
        lines.append("  _g_broadcast_handler = nullptr;")
        lines.append("  Py_XDECREF(_py_messenger);")
        lines.append("  _py_messenger = nullptr;")
    lines.append("  _cancel_all_pending_calls();")
    lines.append("}")
    lines.append("")

    lines.append("#endif  // CPPPARSER")
    lines.append("")
    return "\n".join(lines)
