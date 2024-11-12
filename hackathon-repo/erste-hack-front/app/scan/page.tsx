'use client'

import { useState } from 'react'
import {QrCode, CheckCircle2, XCircle} from 'lucide-react'
import {Button, Card} from "@geist-ui/react"
import Sidebar from "@/app/components/Sidebar";
import QrScan from "@/app/components/QrScanner";

// Assume this is your QR scanner component

const styles = {
    card: {
        backgroundColor: '#1B1932',
        border: 'none',
        borderRadius: '1.5rem',
    },
}

// TODO make reload of qr correct

export default function QRScannerPage() {
    const [scanResult, setScanResult] = useState<string | null>(null)
    const [isScanActive, setIsScanActive] = useState<boolean>(false)
    const [isValid, setIsValid] = useState<boolean | null>(null)

    const toggleQrScannerVisibility = function() {
        const qrContainer = document.getElementById('qr-scanner-container');
        const icon = document.getElementById('big-qr-icon');

        if (qrContainer.classList.contains('hidden')) {
            setIsScanActive(true);
            qrContainer.classList.remove('hidden');
            icon.classList.add('hidden');
        } else {
            setIsScanActive(false);
            qrContainer.classList.add('hidden');
            icon.classList.remove('hidden');
        }
    }

    const handleScan = (result: string) => {
        setScanResult(result)
        console.log('result', scanResult)
        setIsValid(result.trim().length > 0)
    }

    return (
        <div className="flex min-h-screen flex-col bg-[#0D0B21]">
            <div className="flex flex-1 flex-col md:flex-row">
                <Sidebar/>

                <main className="flex-1 p-6">

                    <div className="grid grid-cols-1 md:grid-cols-2 md:max-w-screen-md min-h-96 gap-6">
                        {/* QR Scanner Card */}
                        <Card style={styles.card}>
                            <div className="hidden" id="qr-scanner-container">
                                <QrScan onScanResult={handleScan} isScanActive={isScanActive}/>
                            </div>
                            <Card.Content className="flex flex-1 flex-col gap-4 min-w-md justify-center items-center">
                                <QrCode color="grey" id='big-qr-icon' className="w-16 h-16 mx-auto mb-4"/>
                                <Button onClick={toggleQrScannerVisibility} icon={<QrCode/>}>
                                    Scan QR
                                </Button>
                            </Card.Content>
                        </Card>

                        {/* Result Card */}
                        <Card style={styles.card} className="bg-[#1B1932] border-0">
                            <Card.Content>
                                <h4>Scan Result</h4>
                            </Card.Content>
                            <Card.Content>
                                {scanResult ? (
                                    <div className="space-y-4">
                                        <div className="flex items-center space-x-2">
                                            {isValid ? (
                                                <CheckCircle2 className="w-6 h-6 text-green-500"/>
                                            ) : (
                                                <XCircle className="w-6 h-6 text-red-500"/>
                                            )}
                                            <span className="text-lg font-medium">
                    {isValid ? 'Valid QR Code' : 'Invalid QR Code'}
                  </span>
                                        </div>
                                        <div className="p-4 bg-gray-800 rounded-lg">
                                            <h3 className="text-sm font-medium text-gray-400 mb-2">Content:</h3>
                                            <p className="text-white break-all">{scanResult}</p>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-center text-gray-400">
                                        <p>Scan a QR code to see the result</p>
                                    </div>
                                )}
                            </Card.Content>
                        </Card>


                    </div>
                    {/*<QrScan/>*/}
                </main>
            </div>
        </div>
    )
}