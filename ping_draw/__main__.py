import argparse
import itertools
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Optional, TypeVar

from ping_draw import Color, config, draw

_T = TypeVar("_T")


@dataclass(frozen=True)
class Argument(Generic[_T]):
    name: str
    type: type[_T]
    aliases: list[str] = field(default_factory=list)
    help: Optional[str] = None
    required: bool = False
    default: Optional[_T] = None


@dataclass(frozen=True)
class Action:
    func: Callable[..., None]
    arguments: list[Argument[Any]]
    help: Optional[str] = None


actions: dict[str, Action] = {}


def action(
    name: str, arguments: list[Argument[Any]], help: Optional[str] = None
) -> Callable[[Callable[..., None]], Callable[..., None]]:
    assert name not in actions

    def decorator(func: Callable[..., None]):
        actions[name] = Action(func, arguments, help)
        return func

    return decorator


@action(
    "fill-color",
    [
        Argument("red", int, ["-r"], "red of the color used to fill on the canvas"),
        Argument("green", int, ["-g"], "green of the color used to fill on the canvas"),
        Argument("blue", int, ["-b"], "blue of the color used to fill on the canvas"),
        Argument("sx", int, [], "x axis of the start position of the range", False, 0),
        Argument("sy", int, [], "y axis of the start position of the range", False, 0),
        Argument("ex", int, [], "x axis of the end position of the range if set, or the right of canvas set in config if not", False, 0),
        Argument("ey", int, [], "y axis of the end position of the range if set, or the bottom of canvas set in config if not", False, 0),
        Argument("source", str, ["-s"], "the source address for request", False, None),
    ],
    "Fill specific color in specific range on the canvas.",
)
def fill_canvas(
    red: int,
    green: int,
    blue: int,
    sx: int = 0,
    sy: int = 0,
    ex: Optional[int] = None,
    ey: Optional[int] = None,
    source: Optional[str] = None,
) -> None:
    if not ex:
        ex = config.canvas_size[0]
    if not ey:
        ey = config.canvas_size[1]

    assert (
        0 <= sx <= config.canvas_size[0] and 0 <= sy <= config.canvas_size[1]
    )  # start position is out of range
    assert (
        0 < ex <= config.canvas_size[0] and 0 < ey <= config.canvas_size[1]
    )  # end position is out of range
    assert ex > sx and ey > sy  # invalid range

    for x, y in itertools.product(range(sx, ex), range(sx, ex)):
        draw.draw((x, y), (red, green, blue), source)


@action(
    "draw-image",
    [
        Argument("path", str, ["-i"], "the path to the image"),
        Argument("sx", int, [], "x axis of the position to start to draw the image", False, 0),
        Argument("sy", int, [], "y axis of the position to start to draw the image", False, 0),
        Argument("width", int, ["-iw"], "the width of resized image if set, or canvas width set in config if not", False, None),
        Argument("height", int, ["-ih"], "the height of resized image if set, or canvas height set in config if not", False, None),
        Argument("source", str, ["-s"], "the source address for request", False, None),
    ],
    "Draw image on the canvas. Pillow module is REQUIRED!",
)
def draw_image(
    path: str,
    sx: int = 0,
    sy: int = 0,
    width: Optional[int] = None,
    height: Optional[int] = None,
    source: Optional[str] = None,
) -> None:
    from PIL import Image  # Pillow module is REQUIRED!

    if not width:
        width = config.canvas_size[0]
    if not height:
        height = config.canvas_size[1]

    assert 0 <= sx <= config.canvas_size[0] and 0 <= sy <= config.canvas_size[1]  # position is out of range
    assert 0 <= sx + width <= config.canvas_size[0] and 0 <= sy + height <= config.canvas_size[1]  # the result is out of range

    with Image.open(path) as image:
        resized_image = image.resize((width, height))

    for x, y in itertools.product(
        range(resized_image.width), range(resized_image.height)
    ):
        color: Color = resized_image.getpixel((x, y))[:3]
        draw.draw((sx + x, sy + y), color, source)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--action", "-a", choices=actions.keys(), help="action", required=True
    )
    args, unknown = parser.parse_known_args()

    parser.add_argument("--help", "-h", help="show this help message and exit", action="help")
    parser.add_argument("--loop", "-l", help="run in loop", action=argparse.BooleanOptionalAction, default=False)

    act = actions[args.action]
    for arg in act.arguments:
        name = ("--" + arg.name) if len(arg.name) > 2 else ("-" + arg.name)
        parser.add_argument(
            name,
            *arg.aliases,
            help=arg.help,
            type=arg.type,
            required=arg.required,
            default=arg.default
        )
    parser.description = act.help
    args = parser.parse_args()
    calling_args = dict(
        arg
        for arg in vars(args).items()
        if arg[0] in (argument.name for argument in act.arguments)
    )
    if args.loop:
        while True:
            act.func(**calling_args)
    else:
        act.func(**calling_args)
