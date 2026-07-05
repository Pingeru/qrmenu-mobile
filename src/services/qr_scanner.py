import asyncio
import os
from typing import Optional
from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol

async def scan_qr_code(image_path: Optional[str] = None) -> Optional[str]:
    """Decode a QR code from a captured image file path."""
    if not image_path:
        return None
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _decode_image_sync, image_path)

def _decode_image_sync(image_path: str) -> Optional[str]:
    """Decode a QR code from an image file using pyzbar and Pillow."""
    normalized_path = _normalize_image_path(image_path)
    if not normalized_path or not os.path.exists(normalized_path):
        return None

    try:
        # Pillow ile resmi aç
        with Image.open(normalized_path) as img:
            # pyzbar ile sadece QR kodları ara (Performansı artırır)
            decoded_objects = decode(img, symbols=[ZBarSymbol.QRCODE])
            
            if decoded_objects:
                # İlk bulduğu QR kodun verisini utf-8 olarak çöz
                qr_data = decoded_objects[0].data.decode('utf-8')
                return _extract_business_id(qr_data)
                
    except Exception:
        # Mobil platformda çökme yaşanmaması için hata durumunda yutulur
        pass

    return None

def _normalize_image_path(image_path: str) -> Optional[str]:
    if not image_path:
        return None
    normalized = image_path.strip()
    if normalized.startswith("file://"):
        normalized = normalized[7:]
    return normalized

def _extract_business_id(decoded_value: str) -> Optional[str]:
    if not decoded_value:
        return None
    cleaned = decoded_value.strip().rstrip("/")
    if not cleaned:
        return None
    business_id = cleaned.split("/")[-1]
    return business_id or None