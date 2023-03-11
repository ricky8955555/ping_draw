# ping_draw

A draw implement for Kioubit's IPv6 canvas service.

## Supported Actions

- fill-color: Fill specific color in specific range on the canvas.
- draw-image: Draw image on the canvas. (`Pillow` module is **REQUIRED**!)

## Usage

Run `python3 -m ping_draw -a <action> -h` to see the usage of selected action.

**ATTENTION:** Probably root permission is needed.

## Example

1. Fill `(10, 10)` to `(30, 30)` with black.

    ```bash
    python3 -m ping_draw -a fill-color -sx 10 -sy 10 -ex 30 -ey 30 -r 0 -g 0 -b 0
    ```

2. Draw image `/pathto/image.png` in loop, and request via source address `fd10:1234:5678:90ab:114:514:1919:810`.

    ```bash
    python3 -m ping_draw -a draw-image -i "/pathto/image.png" -s "fd10:1234:5678:90ab:114:514:1919:810" -l
    ```
