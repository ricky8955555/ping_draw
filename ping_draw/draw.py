"""
A module used to draw on Kioubit's canvas.
"""


import socket
import struct
from typing import Optional

from ping_draw import Color, PosOrSize, config

ICMP_ECHO = 8  # Echo request (per RFC792)


def _icmpv6_bare_request(target: str, source_address: Optional[str] = None) -> None:
    """
    Send a bare icmpv6 request.

    Args:
        - `target` (`str`): the target the packet sent to
        - `source_address` (`Optional[str]`): the source address used to send packet if set (default: `None`)
    """

    header = struct.pack("!BBHHH", ICMP_ECHO, 0, 0, 0, 0)

    with socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
        if source_address:
            sock.bind((source_address, 1))
        sock.sendto(header, (target, 1))


def _get_address(pos: PosOrSize, color: Color) -> str:
    """
    Get the address to draw specific color in specific pixel.

    Args:
        - `pos` (`PosOrSize`): the position to draw in
        - `color` (`Color`): the color used to draw

    Returns (`str`):
        The address to draw specific color in specific pixel.
    """

    x, y = pos
    assert x < config.canvas_size[0] and y < config.canvas_size[1]  # x or y is oversized
    r, g, b = color
    assert 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255  # color is invalid
    return config.target.format(
        hex(x)[2:].zfill(4),
        hex(y)[2:].zfill(4),
        hex(r)[2:].zfill(2),
        hex(g)[2:].zfill(2),
        hex(b)[2:].zfill(2),
    )


def draw(pos: PosOrSize, color: Color, source: Optional[str] = None) -> None:
    """
    Draw specific color in specific pixel on the canvas.

    Args:
        - `pos` (`PosOrSize`): the position to draw in
        - `color` (`Color`): the color used to draw
        - `address` (`str`): the source address for request
    """

    target = _get_address(pos, color)
    _icmpv6_bare_request(target, source)
