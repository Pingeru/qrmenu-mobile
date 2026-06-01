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
            success, decoded_info, points = detector.detectAndDecode(frame)
            
            if success and decoded_info:
                # Return the decoded QR code content
                return decoded_info
            
            # Display the frame (optional, for feedback)
            cv2.imshow("QR Code Scanner - Press 'q' to cancel", frame)
            
            # Press 'q' to cancel scanning
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    return None
