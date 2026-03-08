"""High-level Panda3D wrappers for Steam HTML Surface.

- `SteamHTMLSurfaceTexture`: owns the Steam browser handle and updates a Panda
  texture from `Steam-HTML_NeedsPaint` callbacks.
- `SteamHtmlSurfaceRenderer`: optional scene/input wrapper that renders the
  texture on an `aspect2d` card and forwards mouse input.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Callable, Optional

from panda3d import core
from direct.showbase.DirectObject import DirectObject

from panda3d_steamworks import SteamHTMLSurface


class SteamHTMLSurfaceTexture(DirectObject):
    """
    Owns a Steam HTML browser and exposes it as a Panda3D texture.
    """

    _surface_ref_count = 0

    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        user_agent: str = "Panda3D HTML Surface",
        user_css: str = "",
        auto_allow_navigation: bool = True,
        on_ready: Optional[Callable[[int], None]] = None,
    ) -> None:
        super().__init__()
        self.width = int(width)
        self.height = int(height)
        self.auto_allow_navigation = auto_allow_navigation
        self.on_ready = on_ready

        self.browser_handle: Optional[int] = None
        self._temp_dir = Path(tempfile.mkdtemp(prefix="p3d_steam_html_"))
        self._temp_html = self._temp_dir / "index.html"

        self.texture = core.Texture("steam_html_surface")
        self._configure_texture()

        self._ensure_surface_init()

        self.accept("Steam-HTML_BrowserReady", self._on_browser_ready)
        self.accept("Steam-HTML_NeedsPaint", self._on_needs_paint)
        self.accept("Steam-HTML_StartRequest", self._on_start_request)
        self.accept("Steam-HTML_CloseBrowser", self._on_close_browser)

        SteamHTMLSurface.create_browser(user_agent, user_css, self._on_browser_ready)

    def destroy(self) -> None:
        """
        Destroy browser handle, temp files, and event hooks.
        """

        self.ignore_all()

        if self.browser_handle is not None:
            SteamHTMLSurface.remove_browser(self.browser_handle)
            self.browser_handle = None

        shutil.rmtree(self._temp_dir)
        self._release_surface_init()

    def set_browser_size(self, width: int, height: int) -> None:
        width = max(1, int(width))
        height = max(1, int(height))
        if width == self.width and height == self.height:
            return

        self.width = width
        self.height = height
        self._configure_texture()

        if self.browser_handle is not None:
            SteamHTMLSurface.set_size(self.browser_handle, self.width, self.height)

    def load_url(self, url: str, post_data: str = "") -> None:
        if self.browser_handle is not None:
            SteamHTMLSurface.load_url(self.browser_handle, url, post_data)

    def load_html(self, html: str) -> None:
        self._temp_html.write_text(html, encoding="utf-8")
        self.load_url(self._temp_html.resolve().as_uri())

    def execute_javascript(self, script: str) -> None:
        if self.browser_handle is not None:
            SteamHTMLSurface.execute_javascript(self.browser_handle, script)

    def reload(self) -> None:
        if self.browser_handle is not None:
            SteamHTMLSurface.reload(self.browser_handle)

    def _configure_texture(self) -> None:
        self.texture.setup_2d_texture(
            self.width,
            self.height,
            core.Texture.T_unsigned_byte,
            core.Texture.F_rgba8,
        )
        self.texture.set_minfilter(core.SamplerState.FT_linear)
        self.texture.set_magfilter(core.SamplerState.FT_linear)

    def _on_browser_ready(self, result) -> None:
        if not isinstance(result, dict):
            return

        handle = result.get("browser_handle")
        if handle is None:
            return

        if self.browser_handle == handle:
            return

        self.browser_handle = int(handle)
        SteamHTMLSurface.set_size(self.browser_handle, self.width, self.height)
        SteamHTMLSurface.set_key_focus(self.browser_handle, True)

        if self.on_ready is not None:
            self.on_ready(self.browser_handle)

    def _on_start_request(self, result) -> None:
        if not self.auto_allow_navigation or self.browser_handle is None:
            return

        if isinstance(result, dict) and result.get("browser_handle") == self.browser_handle:
            SteamHTMLSurface.allow_start_request(self.browser_handle, True)

    def _on_close_browser(self, result) -> None:
        if not isinstance(result, dict):
            return
        if result.get("browser_handle") == self.browser_handle:
            self.browser_handle = None

    def _on_needs_paint(self, result) -> None:
        if self.browser_handle is None or not isinstance(result, dict):
            return
        if result.get("browser_handle") != self.browser_handle:
            return

        raw = result.get("bgra", b"")
        if isinstance(raw, str):
            raw = raw.encode("latin-1", errors="ignore")
        if not isinstance(raw, (bytes, bytearray)):
            return

        expected = self.width * self.height * 4
        if len(raw) < expected:
            raw = raw + (b"\x00" * (expected - len(raw)))
        elif len(raw) > expected:
            raw = raw[:expected]

        self.texture.set_ram_image(raw)

    @classmethod
    def _ensure_surface_init(cls) -> None:
        if cls._surface_ref_count == 0:
            ok = SteamHTMLSurface.init()
            if not ok:
                raise RuntimeError("SteamHTMLSurface.init() failed")
        cls._surface_ref_count += 1

    @classmethod
    def _release_surface_init(cls) -> None:
        cls._surface_ref_count = max(0, cls._surface_ref_count - 1)
        if cls._surface_ref_count == 0:
            SteamHTMLSurface.shutdown()


class SteamHtmlSurfaceRenderer(DirectObject):
    """
    Renders `SteamHTMLSurfaceTexture` onto an `aspect2d` card.
    """

    def __init__(
        self,
        showbase,
        width: int = 1280,
        height: int = 720,
        frame: tuple[float, float, float, float] = (-1.2, 1.2, -0.7, 0.7),
        parent: Optional[core.NodePath] = None,
        user_agent: str = "Panda3D HTML Surface",
        user_css: str = "",
        auto_input: bool = True,
        auto_allow_navigation: bool = True,
        fullscreen: bool = False,
        match_window_size: bool = False,
        auto_resize_with_window: bool = False,
        on_ready: Optional[Callable[[int], None]] = None,
    ) -> None:
        super().__init__()
        self.base = showbase
        self.on_ready = on_ready

        self._fullscreen = bool(fullscreen)
        self._match_window_size = bool(match_window_size)
        self._auto_resize_with_window = bool(auto_resize_with_window)
        self._auto_input = bool(auto_input)

        left, right, bottom, top = frame
        self._left = float(left)
        self._right = float(right)
        self._bottom = float(bottom)
        self._top = float(top)

        self._card_parent = parent if parent is not None else self.base.aspect2d

        self.surface = SteamHTMLSurfaceTexture(
            width=width,
            height=height,
            user_agent=user_agent,
            user_css=user_css,
            auto_allow_navigation=auto_allow_navigation,
            on_ready=self._on_surface_ready,
        )

        self._last_mouse_px = (0, 0)
        self._rebuild_card()

        if self._fullscreen or self._match_window_size:
            self._sync_to_window()

        if self._auto_resize_with_window and (self._fullscreen or self._match_window_size):
            self.accept("window-event", self._on_window_event)

        if self._auto_input:
            self.accept("wheel_up", self._on_wheel, [60])
            self.accept("wheel_down", self._on_wheel, [-60])
            self.accept("mouse1", self._on_click)
            self.base.task_mgr.add(self._sync_mouse_task, self._task_name("mouse"))

    @property
    def browser_handle(self) -> Optional[int]:
        return self.surface.browser_handle

    @property
    def texture(self) -> core.Texture:
        return self.surface.texture

    @property
    def width(self) -> int:
        return self.surface.width

    @property
    def height(self) -> int:
        return self.surface.height

    def destroy(self) -> None:
        if self._auto_input:
            self.base.task_mgr.remove(self._task_name("mouse"))

        self.ignore_all()

        if hasattr(self, "card") and not self.card.is_empty():
            self.card.remove_node()

        self.surface.destroy()

    def set_frame(self, frame: tuple[float, float, float, float]) -> None:
        left, right, bottom, top = frame
        self._left = float(left)
        self._right = float(right)
        self._bottom = float(bottom)
        self._top = float(top)
        self._rebuild_card()

    def set_fullscreen_frame(self) -> None:
        aspect = self.base.get_aspect_ratio()
        self.set_frame((-aspect, aspect, -1.0, 1.0))

    def set_browser_size(self, width: int, height: int) -> None:
        self.surface.set_browser_size(width, height)

    def load_url(self, url: str, post_data: str = "") -> None:
        self.surface.load_url(url, post_data)

    def load_html(self, html: str) -> None:
        self.surface.load_html(html)

    def execute_javascript(self, script: str) -> None:
        self.surface.execute_javascript(script)

    def reload(self) -> None:
        self.surface.reload()

    def _on_surface_ready(self, handle: int) -> None:
        if self.on_ready is not None:
            self.on_ready(handle)

    def _rebuild_card(self) -> None:
        if hasattr(self, "card") and not self.card.is_empty():
            self.card.remove_node()

        cm = core.CardMaker("steam-html-card")
        cm.set_frame(self._left, self._right, self._bottom, self._top)
        self.card = self._card_parent.attach_new_node(cm.generate())
        self.card.set_texture(self.surface.texture)
        self.card.set_tex_scale(core.TextureStage.get_default(), 1.0, -1.0)
        self.card.set_transparency(core.TransparencyAttrib.M_alpha)

    def _sync_to_window(self) -> None:
        if not self.base.win:
            return

        props = self.base.win.get_properties()
        if not props.has_size():
            return

        w = max(1, props.get_x_size())
        h = max(1, props.get_y_size())

        if self._fullscreen:
            self.set_fullscreen_frame()

        if self._match_window_size:
            self.set_browser_size(w, h)

    def _on_window_event(self, window) -> None:
        if window is not None and window == self.base.win:
            self._sync_to_window()

    def _sync_mouse_task(self, task):
        if self.surface.browser_handle is None:
            return task.cont

        watcher = self.base.mouseWatcherNode
        if not watcher.has_mouse():
            return task.cont

        px_py = self._mouse_to_browser_px(watcher.get_mouse())
        if px_py is None:
            return task.cont

        px, py = px_py
        if (px, py) != self._last_mouse_px:
            self._last_mouse_px = (px, py)
            SteamHTMLSurface.mouse_move(self.surface.browser_handle, px, py)

        return task.cont

    def _on_wheel(self, delta: int) -> None:
        if self.surface.browser_handle is not None:
            SteamHTMLSurface.mouse_wheel(self.surface.browser_handle, int(delta))

    def _on_click(self) -> None:
        if self.surface.browser_handle is None:
            return

        x, y = self._last_mouse_px
        script = (
            "(function(){"
            f"const x={x},y={y};"
            "const el=document.elementFromPoint(x,y);"
            "if(!el){return;}"
            "for(const t of ['mousedown','mouseup','click']){"
            "el.dispatchEvent(new MouseEvent(t,{"
            "bubbles:true,cancelable:true,clientX:x,clientY:y,button:0"
            "}));"
            "}"
            "})();"
        )
        self.surface.execute_javascript(script)

    def _mouse_to_browser_px(self, mouse_pos):
        aspect_x = mouse_pos.x * self.base.get_aspect_ratio()
        aspect_y = mouse_pos.y

        if aspect_x < self._left or aspect_x > self._right:
            return None
        if aspect_y < self._bottom or aspect_y > self._top:
            return None

        u = (aspect_x - self._left) / (self._right - self._left)
        v = (self._top - aspect_y) / (self._top - self._bottom)

        px = int(u * (self.surface.width - 1))
        py = int(v * (self.surface.height - 1))
        px = max(0, min(self.surface.width - 1, px))
        py = max(0, min(self.surface.height - 1, py))
        return px, py

    def _task_name(self, suffix: str) -> str:
        return f"steam_html_surface_renderer_{suffix}_{id(self)}"
