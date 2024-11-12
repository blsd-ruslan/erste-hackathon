'use client'
import {useCallback, useEffect, useRef, useState} from "react";
import "../style/QrScan.css";
import QrScanner from "qr-scanner";

const QrScan = ({ onScanResult, isScanActive }) => {
    const scanner = useRef<QrScanner>();
    const videoEl = useRef<HTMLVideoElement | null>(null);
    const qrBoxEl = useRef<HTMLDivElement | null>(null);
    const [qrOn, setQrOn] = useState<boolean>(true);

    // Wrap onScanSuccess in useCallback to avoid recreating it
    const onScanSuccess = useCallback((result: QrScanner.ScanResult) => {
        console.log(qrOn);
        console.log(result);
        onScanResult(result?.data);
        scanner.current?.stop();
    }, [onScanResult]);

    const onScanFail = useCallback((err: string | Error) => {
        console.log(err);
    }, []);

    useEffect(() => {
        if (isScanActive && videoEl.current && !scanner.current) {
            scanner.current = new QrScanner(videoEl.current, onScanSuccess, {
                onDecodeError: onScanFail,
                preferredCamera: "environment",
                highlightScanRegion: true,
                highlightCodeOutline: true,
                overlay: qrBoxEl.current || undefined,
            });

            if (scanner.current instanceof QrScanner) {
                scanner.current.start().then(() => setQrOn(true)).catch((err) => {
                    if (err) setQrOn(false);
                });
            }
        }

        return () => {
            scanner.current?.stop();
        };
    }, [onScanSuccess, onScanFail]);

    return (
        <div className="flex items-center h-full">
            <div className="qr-reader">
                <video ref={videoEl}></video>
            </div>
        </div>
    );
};

export default QrScan;