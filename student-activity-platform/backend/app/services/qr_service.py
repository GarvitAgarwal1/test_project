"""QR code generation service."""
import io
import qrcode
from qrcode.constants import ERROR_CORRECT_H


def generate_qr_image(data: str, size: int = 10) -> bytes:
    """Generate QR code image as PNG bytes."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
