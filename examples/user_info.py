"""Query information about the currently logged-in Steam user.

Run with a Steam app ID in steam_appid.txt present in this directory.
Pass --avatar to open a window showing the user's medium avatar alongside
their basic profile info rendered as on-screen text.
"""

import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamUser, SteamFriends, SteamUtils


def _prepare_avatar_pixels(raw_rgba, width, height):
    """Convert Steam avatar bytes into Panda texture-friendly RGBA.

    Steam avatar rows are top-to-bottom for this path, while Panda expects
    bottom-to-top RAM image data. We also swap R/B channels to correct color
    ordering observed with this Steam image API output.
    """
    stride = width * 4
    if len(raw_rgba) != stride * height:
        return raw_rgba

    src = memoryview(raw_rgba)
    out = bytearray(len(raw_rgba))

    for y in range(height):
        src_row = (height - 1 - y) * stride
        dst_row = y * stride
        for x in range(0, stride, 4):
            si = src_row + x
            di = dst_row + x
            # Swap red/blue while copying row in flipped order.
            out[di] = src[si + 2]
            out[di + 1] = src[si + 1]
            out[di + 2] = src[si]
            out[di + 3] = src[si + 3]

    return bytes(out)


def _load_avatar_texture(steam_id):
    """Return a Panda3D Texture loaded from the user's medium Steam avatar,
    or None if the avatar is not available."""
    image_handle = SteamFriends.get_medium_friend_avatar(steam_id)
    if image_handle <= 0:
        return None

    ok, width, height = SteamUtils.get_image_size(image_handle)
    if not ok:
        return None

    rgba = SteamUtils.get_image_rgba(image_handle, width * height * 4)
    if rgba is None:
        return None
    rgba = _prepare_avatar_pixels(rgba, width, height)

    tex = core.Texture("steam_avatar")
    tex.setup_2d_texture(width, height, core.Texture.T_unsigned_byte, core.Texture.F_rgba8)
    tex.set_ram_image(rgba)
    tex.set_minfilter(core.SamplerState.FT_linear)
    tex.set_magfilter(core.SamplerState.FT_linear)
    return tex


def show_avatar_window(base, steam_id, persona, level):
    """Open a Panda3D window displaying the user's avatar and basic info."""

    tex = _load_avatar_texture(steam_id)
    if tex is not None:
        # Place avatar card on the left side of aspect2d
        card = core.CardMaker("avatar_card")
        # Keep the card square so avatars are not stretched.
        card.set_frame(-1.8, -0.8, -0.5, 0.5)
        node = base.aspect2d.attach_new_node(card.generate())
        node.set_texture(tex)
        node.set_transparency(core.TransparencyAttrib.M_alpha)
    else:
        print("  (avatar not available)")

    # Info text on the right
    lines = [
        persona,
        f"Level {level}",
        f"ID: {steam_id}",
    ]
    text_node = core.TextNode("info")
    text_node.set_text("\n".join(lines))
    text_node.set_align(core.TextNode.A_left)
    text_np = base.aspect2d.attach_new_node(text_node)
    text_np.set_pos(-0.7, 0, 0.2)
    text_np.set_scale(0.07)

    base.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--avatar", action="store_true",
                        help="Open a window displaying the user's avatar")
    args = parser.parse_args()

    window_type = "none" if not args.avatar else None
    base = SteamShowBase(windowType=window_type)

    steam_id = SteamUser.get_steam_id()
    persona = SteamFriends.get_persona_name()
    level = SteamUser.get_player_steam_level()

    print("Current Steam User")
    print(f"  Persona name     : {persona}")
    print(f"  Steam ID (64-bit): {steam_id}")
    print(f"  Steam level      : {level}")
    print(f"  Logged on        : {SteamUser.logged_on()}")
    print(f"  Behind NAT       : {SteamUser.is_behind_nat()}")

    # Account security flags
    print("\nAccount Security")
    print(f"  Phone verified   : {SteamUser.is_phone_verified()}")
    print(f"  Two-factor auth  : {SteamUser.is_two_factor_enabled()}")

    # Game badge info (series 1, non-foil and foil)
    badge = SteamUser.get_game_badge_level(1, False)
    badge_foil = SteamUser.get_game_badge_level(1, True)
    if badge or badge_foil:
        print(f"\nGame Badge (series 1)")
        print(f"  Regular level    : {badge}")
        print(f"  Foil level       : {badge_foil}")

    # Avatar image retrieval
    print("\nAvatar")
    image_handle = SteamFriends.get_medium_friend_avatar(steam_id)
    if image_handle > 0:
        ok, w, h = SteamUtils.get_image_size(image_handle)
        if ok:
            rgba = SteamUtils.get_image_rgba(image_handle, w * h * 4)
            loaded = rgba is not None
        else:
            loaded = False
        print(f"  Image handle     : {image_handle}")
        print(f"  Dimensions       : {w}x{h}" if ok else "  Dimensions       : unavailable")
        print(f"  RGBA data loaded : {loaded}" + (f" ({len(rgba)} bytes)" if loaded else ""))
    else:
        print("  No avatar available (handle <= 0)")

    if args.avatar:
        show_avatar_window(base, steam_id, persona, level)
    else:
        base.userExit()


if __name__ == "__main__":
    main()
