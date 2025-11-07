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
from urllib.parse import urlparse

# Setup logging
LOG_DIR = "logtermux"
LOG_FILE = os.path.join(LOG_DIR, "logreport.txt")

def setup_logging():
    """Setup directory dan file log"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"LOG SESSION - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*50}\n")

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
    """Menampilkan header program"""
    print("=" * 60)
    print("           PROGRAM SHORTCUT UTILITIES")
    print("=" * 60)
    print(f"Python {sys.version} - {platform.system()}")
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
    """WiFi check untuk Termux"""
    print("\n1. 📡 Scan WiFi")
    print("2. 📶 Status Koneksi")
    print("3. 🚀 Speed Test")
    
    choice = input("Pilih opsi (1-3): ").strip()
    
    if choice == "1":
        scan_wifi_termux()
    elif choice == "2":
        wifi_status_termux()
    elif choice == "3":
        speed_test()
    else:
        print("❌ Pilihan tidak valid!")

def scan_wifi_termux():
    """Scan WiFi di Termux"""
    print("\n📡 Scanning WiFi...")
    
    try:
        result = subprocess.run(['termux-wifi-scaninfo'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            networks = json.loads(result.stdout)
            print(f"\n📶 Found {len(networks)} networks:")
            for net in networks[:10]:  # Tampilkan 10 pertama
                ssid = net.get('ssid', 'Hidden')
                bssid = net.get('bssid', 'N/A')
                print(f"  📶 {ssid} | {bssid}")
        else:
            print("❌ Gagal scan WiFi")
            print("💡 Pastikan termux-api terinstall dan izin lokasi aktif")
            
    except Exception as e:
        print(f"❌ Error: {e}")

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

def main():
    """Menu utama program"""
    setup_logging()
    log_message("Program started")
    
    while True:
        clear_screen()
        display_header()
        
        req_status = "✅" if REQUESTS_AVAILABLE else "❌"
        speed_status = "✅" if SPEEDTEST_AVAILABLE else "❌"
        
        print("\n📋 MENU UTAMA:")
        print("1. 🔗 Website Checker")
        print("2. 🔤 Random String Generator") 
        print("3. 📡 WiFi Checker")
        print("4. 💻 System Info")
        print("5. 🚀 Auto System Setup")
        print("6. 🚪 Keluar")
        
        print(f"\nStatus: requests {req_status} | speedtest {speed_status}")
        print(f"Logs: {LOG_FILE}")
        
        choice = input("\nPilih program (1-6): ").strip()
        log_message(f"User memilih menu: {choice}")
        
        if choice == "1":
            website_checker()
        elif choice == "2":
            random_string_generator()
        elif choice == "3":
            wifi_checker()
        elif choice == "4":
            show_detailed_system_info()
        elif choice == "5":
            system_setup_requirements()
        elif choice == "6":
            print("\n👋 Terima kasih!")
            log_message("Program exited")
            break
        else:
            print("\n❌ Pilihan tidak valid!")
        
        input("\nTekan Enter untuk lanjut...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program dihentikan")
        log_message("Program interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        log_message(f"Program error: {e}")
