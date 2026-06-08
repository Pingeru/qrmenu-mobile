import cv2
import asyncio
from typing import Optional


async def scan_qr_code() -> Optional[str]:
    """
    Scan a QR code using the device camera.
    Returns the decoded QR code data or None if no QR code is found or user cancels.
    Runs in a separate thread to avoid blocking the UI.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _scan_qr_code_sync)


def _scan_qr_code_sync() -> Optional[str]:
    """Synchronous QR code scanning using OpenCV."""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return None
    
    try:
        # Try to detect QR codes from camera frames
        detector = cv2.QRCodeDetector()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect and decode QR code
            data, bbox, straight_qrcode = detector.detectAndDecode(frame)
            
            # returns https://qrmenu.dovanay.com/menu/6a13f8d3be5344199f7811e0 for test
            # we should return business id part
            if data:
                # Extract business_id, handling trailing slashes
                business_id = data.rstrip("/").split("/")[-1]
                if business_id:  # Ensure we got a valid ID
                    return business_id       
            
            # Display the frame (optional, for feedback)
            cv2.imshow("QR Code Scanner - Press 'q' to cancel", frame)
            
            # Press 'q' to cancel scanning
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    return None
