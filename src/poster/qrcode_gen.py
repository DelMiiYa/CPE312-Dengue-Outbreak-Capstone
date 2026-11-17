"""
QR Code Generator for Capstone Poster (Standalone, Zero New Dependencies).
Generates standard Version 4/5 QR codes in byte mode with Level L error correction.
Saves PNG images via PIL/numpy.
"""

from pathlib import Path
import numpy as np
from PIL import Image

# Galois Field GF(256) tables for Reed-Solomon encoding
_EXP = [0] * 512
_LOG = [0] * 256
_x = 1
for _i in range(255):
    _EXP[_i] = _x
    _EXP[_i + 255] = _x
    _LOG[_x] = _i
    _x <<= 1
    if _x & 256:
        _x ^= 0x11D


def _gf_mul(x: int, y: int) -> int:
    if x == 0 or y == 0:
        return 0
    return _EXP[_LOG[x] + _LOG[y]]


def _rs_encode(data: list[int], nsym: int) -> list[int]:
    """Compute Reed-Solomon error correction codewords."""
    g = [1]
    for i in range(nsym):
        alpha = _EXP[i]
        new_g = [0] * (len(g) + 1)
        for j in range(len(g)):
            new_g[j] ^= g[j]
            new_g[j + 1] ^= _gf_mul(g[j], alpha)
        g = new_g

    msg = list(data) + [0] * nsym
    for i in range(len(data)):
        coef = msg[i]
        if coef != 0:
            for j in range(1, len(g)):
                msg[i + j] ^= _gf_mul(coef, g[j])
    return msg[-nsym:]


def _encode_text(text: str, version: int = 4) -> str:
    """Encode ASCII string into bitstream for Version 4 or 5 Level L."""
    if version == 4:
        total_data = 80
        nsym = 20
    elif version == 5:
        total_data = 106
        nsym = 28
    else:
        raise ValueError(f"Unsupported QR version: {version}")

    raw = [ord(c) for c in text]
    if len(raw) > total_data - 2:
        raise ValueError(f"Text too long ({len(raw)} chars) for QR Version {version} Level L (max {total_data - 2})")

    # 4 bits Mode (Byte mode: 0100) + 8 bits Character Count
    bits = "0100" + f"{len(raw):08b}"
    for b in raw:
        bits += f"{b:08b}"

    # Terminator
    rem = total_data * 8 - len(bits)
    bits += "0" * min(4, rem)
    # Pad to byte boundary
    if len(bits) % 8 != 0:
        bits += "0" * (8 - (len(bits) % 8))

    data_bytes = [int(bits[i : i + 8], 2) for i in range(0, len(bits), 8)]
    pad_patterns = [0xEC, 0x11]
    p_idx = 0
    while len(data_bytes) < total_data:
        data_bytes.append(pad_patterns[p_idx])
        p_idx = 1 - p_idx

    ec_bytes = _rs_encode(data_bytes, nsym)
    all_codewords = data_bytes + ec_bytes

    full_bits = "".join(f"{b:08b}" for b in all_codewords)
    return full_bits


def generate_qr_matrix(text: str) -> np.ndarray:
    """Build binary matrix (1=black, 0=white) with quiet zone for text."""
    version = 4 if len(text) <= 78 else 5
    N = 17 + 4 * version
    mat = np.full((N, N), -1, dtype=int)
    reserved = np.zeros((N, N), dtype=bool)

    def set_module(r: int, c: int, val: int):
        mat[r, c] = val
        reserved[r, c] = True

    # Finder patterns
    def add_finder(r0: int, c0: int):
        for dr in range(7):
            for dc in range(7):
                if dr in (0, 6) or dc in (0, 6) or (2 <= dr <= 4 and 2 <= dc <= 4):
                    set_module(r0 + dr, c0 + dc, 1)
                else:
                    set_module(r0 + dr, c0 + dc, 0)
        # Separator (1 module white border)
        for dr in range(-1, 8):
            for dc in range(-1, 8):
                r, c = r0 + dr, c0 + dc
                if 0 <= r < N and 0 <= c < N and not reserved[r, c]:
                    set_module(r, c, 0)

    add_finder(0, 0)
    add_finder(0, N - 7)
    add_finder(N - 7, 0)

    # Timing patterns
    for i in range(8, N - 8):
        set_module(6, i, 1 if i % 2 == 0 else 0)
        set_module(i, 6, 1 if i % 2 == 0 else 0)

    # Alignment pattern: Version 4 at (26, 26), Version 5 at (30, 30)
    align_pos = 26 if version == 4 else 30
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if abs(dr) == 2 or abs(dc) == 2 or (dr == 0 and dc == 0):
                set_module(align_pos + dr, align_pos + dc, 1)
            else:
                set_module(align_pos + dr, align_pos + dc, 0)

    # Dark module
    dark_row = 4 * version + 9
    set_module(dark_row, 8, 1)

    # Reserve format info areas
    for c in range(9):
        if c != 6:
            reserved[8, c] = True
    for r in range(9):
        if r != 6:
            reserved[r, 8] = True
    for r in range(N - 7, N):
        reserved[r, 8] = True
    for c in range(N - 8, N):
        reserved[8, c] = True

    # Place data modules
    bits = _encode_text(text, version=version)
    bit_idx = 0
    c = N - 1
    up = True
    while c > 0:
        if c == 6:
            c -= 1
        cols = [c, c - 1]
        rows = range(N - 1, -1, -1) if up else range(N)
        for r in rows:
            for col in cols:
                if not reserved[r, col]:
                    val = int(bits[bit_idx]) if bit_idx < len(bits) else 0
                    bit_idx += 1
                    # Mask 0: (r + col) % 2 == 0
                    if (r + col) % 2 == 0:
                        val ^= 1
                    mat[r, col] = val
        up = not up
        c -= 2

    # Format info bits: Level L (01) + Mask 0 (000) = 01000 (8)
    # BCH code calculation
    poly = 8 << 10
    gen = 0x537
    for i in range(14, 9, -1):
        if poly & (1 << i):
            poly ^= (gen << (i - 10))
    fmt_val = ((8 << 10) | poly) ^ 0x5412
    fmt_str = f"{fmt_val:015b}"
    fmt_bits = [int(b) for b in fmt_str]  # MSB first

    # Top-left positions
    tl_coords = [
        (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 7), (8, 8),
        (7, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8),
    ]
    for (r, col), b in zip(tl_coords, fmt_bits):
        mat[r, col] = b

    # Copy to BL and TR
    bl_coords = [(N - 1 - i, 8) for i in range(7)]
    for (r, col), b in zip(bl_coords, fmt_bits[:7]):
        mat[r, col] = b
    tr_coords = [(8, N - 8 + i) for i in range(8)]
    for (r, col), b in zip(tr_coords, fmt_bits[7:]):
        mat[r, col] = b

    # Quiet zone: 4 modules border
    border = 4
    quiet_mat = np.zeros((N + 2 * border, N + 2 * border), dtype=np.uint8)
    quiet_mat[:] = 0  # 0 = white in binary module matrix
    for r in range(N):
        for c in range(N):
            if mat[r, c] == 1:
                quiet_mat[r + border, c + border] = 1

    return quiet_mat


def save_qr_png(text: str, output_path: str | Path, scale: int = 10) -> Path:
    """Generate QR code image and save as PNG file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mat = generate_qr_matrix(text)
    # Invert for grayscale: 1 -> black (0), 0 -> white (255)
    img_array = np.where(mat == 1, 0, 255).astype(np.uint8)
    img_scaled = np.repeat(np.repeat(img_array, scale, axis=0), scale, axis=1)
    img = Image.fromarray(img_scaled, mode="L")
    img.save(path, format="PNG")
    return path
