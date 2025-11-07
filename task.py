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
    
    # Write header log
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

# Cek jika requests sudah terinstall
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

def system_setup_requirements():
    """Fungsi gabungan untuk setup system dan install requirements"""
    while True:
        clear_screen()
        print("\n=== SYSTEM SETUP & REQUIREMENTS ===")
        
        # Tampilkan status current requirements
        print("\n📊 STATUS REQUIREMENTS:")
        
        # Cek Python version
        python_version = sys.version_info
        python_status = "✅" if python_version >= (3, 6) else "❌"
        print(f"{python_status} Python {python_version[0]}.{python_version[1]}.{python_version[2]} {'(OK)' if python_version >= (3, 6) else '(Rekomendasi 3.6+)'}")
        
        # Cek packages
        packages_status = {}
        packages_to_check = [
            ("requests", "Website checker"),
            ("colorama", "Warna terminal"),
            ("speedtest-cli", "Test kecepatan internet"),
            ("termux-api", "Android Termux API"),
            ("nmap", "Network scanning")
        ]
        
        for package, purpose in packages_to_check:
            if package in ["termux-api", "nmap"]:
                # Cek untuk package system
                try:
                    if package == "termux-api":
                        result = subprocess.run(['pkg', 'list-installed'], capture_output=True, text=True)
                        installed = 'termux-api' in result.stdout
                    else:
                        result = subprocess.run([package, '--version'], capture_output=True, text=True)
                        installed = result.returncode == 0
                    
                    if installed:
                        packages_status[package] = "✅"
                        print(f"✅ {package:15} - OK")
                    else:
                        packages_status[package] = "❌"
                        print(f"❌ {package:15} - Belum terinstall")
                except:
                    packages_status[package] = "❌"
                    print(f"❌ {package:15} - Belum terinstall")
            else:
                # Cek Python packages
                try:
                    __import__(package.replace('-', '_') if package == "speedtest-cli" else package)
                    packages_status[package] = "✅"
                    print(f"✅ {package:15} - OK")
                except ImportError:
                    packages_status[package] = "❌"
                    print(f"❌ {package:15} - Belum terinstall")
        
        print(f"\n💻 Sistem Operasi: {platform.system()} {platform.release()}")
        
        # Tampilkan menu options
        print("\n🔧 MENU SETUP:")
        print("1. Install All Requirements (Auto)")
        print("2. Install Python Packages Only")
        print("3. Install System Packages (Termux)")
        print("4. Check System Information")
        print("5. Test Dependencies")
        print("6. Kembali ke Menu Utama")
        
        choice = input("\nPilih opsi (1-6): ").strip()
        
        if choice == "1":
            install_all_requirements()
        elif choice == "2":
            install_python_packages()
        elif choice == "3":
            install_system_packages()
        elif choice == "4":
            show_detailed_system_info()
        elif choice == "5":
            test_dependencies()
        elif choice == "6":
            break
        else:
            print("❌ Pilihan tidak valid!")
        
        input("\nTekan Enter untuk lanjut...")

def install_all_requirements():
    """Install semua requirements sekaligus"""
    print("\n=== INSTALL ALL REQUIREMENTS ===")
    
    log_message("Memulai install semua requirements")
    
    # Install system packages untuk Termux
    if platform.system() == "Linux" and "ANDROID_ROOT" in os.environ:
        print("\n📦 Installing System Packages (Termux)...")
        system_packages = ["termux-api", "nmap", "wireless-tools", "procps"]
        
        for pkg in system_packages:
            try:
                log_message(f"Installing system package: {pkg}")
                print(f"Installing {pkg}...")
                result = subprocess.run(['pkg', 'install', '-y', pkg], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {pkg} berhasil diinstall")
                    log_message(f"✅ {pkg} berhasil diinstall")
                else:
                    print(f"❌ Gagal install {pkg}")
                    log_message(f"❌ Gagal install {pkg}: {result.stderr}")
            except Exception as e:
                print(f"❌ Error install {pkg}: {e}")
                log_message(f"❌ Error install {pkg}: {e}")
    
    # Install Python packages
    install_python_packages()

def install_python_packages():
    """Install Python packages saja"""
    print("\n=== INSTALL PYTHON PACKAGES ===")
    
    python_packages = [
        ("requests", "Untuk website checker"),
        ("speedtest-cli", "Untuk test kecepatan internet"),
        ("colorama", "Untuk warna terminal")
    ]
    
    print("Python packages yang akan diinstall:")
    for package, description in python_packages:
        print(f"  - {package:15} ({description})")
    
    confirm = input("\nApakah Anda ingin menginstall semua Python packages? (y/n): ").lower()
    
    if confirm == 'y':
        log_message("Memulai install Python packages")
        success_count = 0
        total_count = len(python_packages)
        
        for package, description in python_packages:
            try:
                log_message(f"Installing Python package: {package}")
                print(f"\n📦 Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} berhasil diinstall")
                log_message(f"✅ {package} berhasil diinstall")
                success_count += 1
                
                # Update global status
                if package == "requests":
                    global REQUESTS_AVAILABLE
                    try:
                        import requests
                        REQUESTS_AVAILABLE = True
                    except ImportError:
                        pass
                elif package == "speedtest-cli":
                    global SPEEDTEST_AVAILABLE
                    try:
                        import speedtest
                        SPEEDTEST_AVAILABLE = True
                    except ImportError:
                        pass
                        
            except subprocess.CalledProcessError as e:
                print(f"❌ Gagal install {package}: {e}")
                log_message(f"❌ Gagal install {package}: {e}")
            except Exception as e:
                print(f"❌ Error saat install {package}: {e}")
                log_message(f"❌ Error saat install {package}: {e}")
        
        print(f"\n📊 HASIL INSTALLATION:")
        print(f"✅ Berhasil: {success_count}/{total_count}")
        log_message(f"Hasil installation: {success_count}/{total_count} berhasil")
        
        if success_count == total_count:
            print("🎉 Semua package berhasil diinstall!")
        else:
            print("⚠️ Beberapa package gagal diinstall.")
            
    else:
        print("Installation dibatalkan.")

def install_system_packages():
    """Install system packages untuk Termux"""
    if platform.system() != "Linux" or "ANDROID_ROOT" not in os.environ:
        print("❌ Fitur ini hanya untuk Termux Android")
        return
        
    print("\n=== INSTALL SYSTEM PACKAGES (TERMUX) ===")
    
    system_packages = [
        ("termux-api", "Untuk akses API Android"),
        ("nmap", "Untuk network scanning"),
        ("wireless-tools", "Untuk tools WiFi (iwconfig, iwlist)"),
        ("procps", "Untuk process utilities (ps, top)"),
        ("net-tools", "Untuk network tools (ifconfig, netstat)")
    ]
    
    print("System packages yang akan diinstall:")
    for package, description in system_packages:
        print(f"  - {package:15} ({description})")
    
    confirm = input("\nApakah Anda ingin menginstall semua system packages? (y/n): ").lower()
    
    if confirm == 'y':
        log_message("Memulai install system packages")
        success_count = 0
        total_count = len(system_packages)
        
        for package, description in system_packages:
            try:
                log_message(f"Installing system package: {package}")
                print(f"Installing {package}...")
                result = subprocess.run(['pkg', 'install', '-y', package], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {package} berhasil diinstall")
                    log_message(f"✅ {package} berhasil diinstall")
                    success_count += 1
                else:
                    print(f"❌ Gagal install {package}")
                    log_message(f"❌ Gagal install {package}: {result.stderr}")
            except Exception as e:
                print(f"❌ Error install {package}: {e}")
                log_message(f"❌ Error install {package}: {e}")
        
        print(f"\n📊 HASIL INSTALLATION:")
        print(f"✅ Berhasil: {success_count}/{total_count}")
        log_message(f"Hasil system installation: {success_count}/{total_count} berhasil")
        
    else:
        print("Installation dibatalkan.")

def show_detailed_system_info():
    """Menampilkan informasi sistem detail"""
    print("\n=== DETAILED SYSTEM INFORMATION ===")
    log_message("Mengakses detailed system information")
    
    # Basic info
    print(f"🕐 Waktu Sistem: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"💻 Platform: {platform.system()} {platform.release()}")
    print(f"🏗️  Architecture: {platform.architecture()[0]}")
    
    # Device name
    try:
        device_name = socket.gethostname()
        print(f"📱 Device Name: {device_name}")
    except:
        print("📱 Device Name: Tidak dapat dideteksi")
    
    # IP Address
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print(f"🌐 IP Address: {ip_address}")
        
        # Public IP
        if REQUESTS_AVAILABLE:
            try:
                public_ip = requests.get('https://api.ipify.org', timeout=5).text
                print(f"🌍 Public IP: {public_ip}")
                
                # Location info
                try:
                    location_info = requests.get(f'http://ip-api.com/json/{public_ip}', timeout=5).json()
                    if location_info['status'] == 'success':
                        print(f"📍 Location: {location_info.get('city', 'N/A')}, {location_info.get('country', 'N/A')}")
                        print(f"🏢 ISP: {location_info.get('isp', 'N/A')}")
                except:
                    pass
            except:
                print("🌍 Public IP: Tidak dapat terhubung")
    except:
        print("🌐 IP Address: Tidak dapat dideteksi")
    
    # Battery info untuk Android
    if platform.system() == "Linux" and "ANDROID_ROOT" in os.environ:
        try:
            print("\n🔋 Battery Information:")
            # Menggunakan termux-battery-status
            result = subprocess.run(['termux-battery-status'], capture_output=True, text=True)
            if result.returncode == 0:
                battery_data = json.loads(result.stdout)
                percentage = battery_data.get('percentage', 'N/A')
                status = battery_data.get('status', 'N/A')
                health = battery_data.get('health', 'N/A')
                plugged = battery_data.get('plugged', 'N/A')
                
                print(f"  Percentage: {percentage}%")
                print(f"  Status: {status}")
                print(f"  Health: {health}")
                print(f"  Plugged: {'🔌 Charging' if plugged != 'UNPLUGGED' else '🔋 Battery'}")
            else:
                print("  ❌ Battery info tidak tersedia")
        except Exception as e:
            print(f"  ❌ Error battery info: {e}")
    
    # Network connection type
    print("\n📶 Network Information:")
    try:
        # Cek apakah terhubung WiFi
        if platform.system() == "Linux" and "ANDROID_ROOT" in os.environ:
            result = subprocess.run(['termux-wifi-connectioninfo'], capture_output=True, text=True)
            if result.returncode == 0:
                wifi_info = json.loads(result.stdout)
                ssid = wifi_info.get('ssid', 'Not Connected')
                print(f"  WiFi: {ssid}")
                print(f"  Status: {'✅ Connected' if ssid != 'Not Connected' else '❌ Disconnected'}")
            else:
                print("  ❌ WiFi info tidak tersedia")
        else:
            # Untuk non-Android
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
            if 'wlan' in result.stdout or 'wifi' in result.stdout:
                print("  Connection: 📶 WiFi")
            else:
                print("  Connection: 📱 Mobile Data/Ethernet")
    except Exception as e:
        print(f"  ❌ Error network info: {e}")
    
    # Additional system info
    print(f"\n📁 Working Directory: {os.getcwd()}")
    print(f"📝 Log File: {LOG_FILE}")

def test_dependencies():
    """Test semua dependencies"""
    print("\n=== DEPENDENCIES TEST ===")
    log_message("Menjalankan dependencies test")
    
    tests = [
        ("Python Version", test_python_version),
        ("Requests Module", test_requests),
        ("Speedtest Module", test_speedtest),
        ("Network Connection", test_network),
        ("PIP Availability", test_pip),
        ("System Commands", test_system_commands),
        ("Termux API", test_termux_api)
    ]
    
    print("🧪 Menjalankan tests...\n")
    
    for test_name, test_func in tests:
        try:
            result, message = test_func()
            status = "✅" if result else "❌"
            print(f"{status} {test_name:20} : {message}")
            log_message(f"Test {test_name}: {status} - {message}")
        except Exception as e:
            print(f"❌ {test_name:20} : ERROR - {e}")
            log_message(f"Test {test_name}: ERROR - {e}")

def test_python_version():
    """Test Python version"""
    version = sys.version_info
    if version >= (3, 6):
        return True, f"OK (v{version.major}.{version.minor}.{version.micro})"
    else:
        return False, f"Rekomendasi 3.6+ (current: v{version.major}.{version.minor})"

def test_requests():
    """Test requests module"""
    try:
        import requests
        return True, "OK - Terinstall"
    except ImportError:
        return False, "Tidak terinstall"

def test_speedtest():
    """Test speedtest module"""
    try:
        import speedtest
        return True, "OK - Terinstall"
    except ImportError:
        return False, "Tidak terinstall"

def test_network():
    """Test koneksi network"""
    try:
        import requests
        response = requests.get('https://www.google.com', timeout=5)
        return True, "OK - Connected"
    except:
        return False, "Tidak terhubung"

def test_pip():
    """Test PIP availability"""
    try:
        subprocess.check_output([sys.executable, "-m", "pip", "--version"])
        return True, "OK - Available"
    except:
        return False, "Tidak tersedia"

def test_system_commands():
    """Test system commands"""
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.check_output(['cmd', '/c', 'echo', 'test'], timeout=5)
        else:
            subprocess.check_output(['echo', 'test'], timeout=5)
        return True, "OK - Commands work"
    except:
        return False, "Error executing commands"

def test_termux_api():
    """Test Termux API"""
    if platform.system() == "Linux" and "ANDROID_ROOT" in os.environ:
        try:
            result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=10)
            return result.returncode == 0, "Available" if result.returncode == 0 else "Not available"
        except:
            return False, "Not installed"
    return True, "N/A (Not Android)"

def website_checker():
    """Program untuk mengecek status website"""
    if not REQUESTS_AVAILABLE:
        print("❌ Module 'requests' belum terinstall!")
        print("Gunakan opsi '5. System Setup & Requirements' terlebih dahulu")
        return
    
    print("\n=== WEBSITE CHECKER ===")
    url = input("Masukkan URL/domain website (contoh: https://google.com): ").strip()
    
    if not url:
        print("URL tidak boleh kosong!")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    log_message(f"Website check: {url}")
    
    try:
        print(f"\n🔍 Mengecek {url}...")
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"🟢 Status: {'✅ ONLINE' if response.status_code == 200 else '⚠️  MASALAH'}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f} detik")
        print(f"🖥️  Server: {response.headers.get('Server', 'Tidak diketahui')}")
        print(f"🔒 Encoding: {response.encoding}")
        print(f"📦 Size: {len(response.content)} bytes")
        
        log_message(f"Website {url}: Status {response.status_code}, Time {response.elapsed.total_seconds():.2f}s")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        print("Website tidak dapat diakses atau tidak ditemukan")
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
            if length > 1000:
                print("⚠️  Panjang terlalu besar, mungkin akan lambat!")
        except ValueError:
            print("❌ Masukkan angka yang valid!")
            continue
        
        print("\n🎲 Pilihan karakter:")
        print("1. Huruf besar saja (A-Z)")
        print("2. Huruf kecil saja (a-z)") 
        print("3. Huruf besar dan kecil (A-Za-z)")
        print("4. Angka saja (0-9)")
        print("5. Huruf dan angka (A-Za-z0-9)")
        print("6. Huruf, angka, dan simbol (A-Za-z0-9!@#$%)")
        print("7. Password kuat (huruf, angka, simbol)")
        print("8. Custom (input manual karakter)")
        
        choice = input("Pilih opsi (1-8): ").strip()
        
        characters = ""
        
        if choice == "1":
            characters = string.ascii_uppercase
            print("Menggunakan: A-Z")
        elif choice == "2":
            characters = string.ascii_lowercase
            print("Menggunakan: a-z")
        elif choice == "3":
            characters = string.ascii_letters
            print("Menggunakan: A-Za-z")
        elif choice == "4":
            characters = string.digits
            print("Menggunakan: 0-9")
        elif choice == "5":
            characters = string.ascii_letters + string.digits
            print("Menggunakan: A-Za-z0-9")
        elif choice == "6":
            characters = string.ascii_letters + string.digits + string.punctuation
            print("Menggunakan: A-Za-z0-9 + simbol")
        elif choice == "7":
            characters = string.ascii_letters + string.digits + "!@#$%&*"
            print("Menggunakan: karakter password kuat")
        elif choice == "8":
            characters = input("Masukkan karakter custom: ")
            if not characters:
                print("❌ Karakter tidak boleh kosong!")
                continue
            print(f"Menggunakan: {characters}")
        else:
            print("❌ Pilihan tidak valid!")
            continue
        
        # Generate random string
        result = ''.join(random.choice(characters) for _ in range(length))
        print(f"\n🔹 String Acak: {result}")
        log_message(f"Generated random string: {result}")
        
        # Tanya apakah ingin generate lagi dengan panjang yang sama
        while True:
            print("\nPilihan:")
            print("1. Generate lagi dengan panjang sama")
            print("2. Generate dengan panjang berbeda")
            print("3. Kembali ke menu utama")
            
            sub_choice = input("Pilih opsi (1-3): ").strip()
            
            if sub_choice == "1":
                result = ''.join(random.choice(characters) for _ in range(length))
                print(f"\n🔹 String Acak: {result}")
                log_message(f"Generated random string: {result}")
            elif sub_choice == "2":
                break  # Keluar ke input panjang baru
            elif sub_choice == "3":
                return  # Kembali ke menu utama
            else:
                print("❌ Pilihan tidak valid!")

def wifi_checker():
    """Program untuk mengecek jaringan WiFi (termasuk hidden)"""
    print("\n=== HIDDEN WIFI CHECKER ===")
    log_message("Mengakses WiFi checker")
    
    system = platform.system()
    print(f"Sistem: {system}")
    
    if system == "Windows":
        windows_wifi_check()
    elif system == "Linux" or "Android" in system:
        linux_wifi_check()
    else:
        print(f"❌ Sistem {system} belum didukung sepenuhnya")

def windows_wifi_check():
    """WiFi check untuk Windows"""
    print("\n📡 Menampilkan jaringan WiFi yang tersedia...")
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                              capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        
        print("\n📡 Informasi WiFi Interface:")
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                              capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Coba jalankan sebagai Administrator")

def linux_wifi_check():
    """WiFi check untuk Linux/Android"""
    print("\nPilihan:")
    print("1. Scan jaringan WiFi terdekat")
    print("2. Cek interface WiFi & Status Koneksi")
    print("3. Test koneksi internet (Upload/Download)")
    print("4. Informasi jaringan saat ini")
    
    choice = input("Pilih opsi (1-4): ").strip()
    
    if choice == "1":
        scan_wifi_linux()
    elif choice == "2":
        check_wifi_connection_status()
    elif choice == "3":
        test_network_speed()
    elif choice == "4":
        check_current_network()
    else:
        print("❌ Pilihan tidak valid!")

def scan_wifi_linux():
    """Scan WiFi untuk Linux/Android dengan multiple methods"""
    print("\n📡 Scanning WiFi networks...")
    log_message("Memulai WiFi scan")
    
    methods = [
        {"name": "Termux API", "cmd": ["termux-wifi-scaninfo"], "timeout": 30},
        {"name": "NetworkManager", "cmd": ["nmcli", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi"], "timeout": 20},
        {"name": "iwlist", "cmd": ["iwlist", "scan"], "timeout": 30},
        {"name": "iw", "cmd": ["iw", "dev"], "timeout": 10},
    ]
    
    success = False
    for method in methods:
        try:
            log_message(f"Mencoba scan dengan: {method['name']}")
            print(f"\n🔄 Mencoba: {method['name']}...")
            result = subprocess.run(method["cmd"], capture_output=True, text=True, timeout=method["timeout"])
            
            if result.returncode == 0 and result.stdout.strip():
                print(f"\n✅ BERHASIL dengan {method['name']}:")
                print("=" * 50)
                print(result.stdout)
                print("=" * 50)
                log_message(f"Scan berhasil dengan {method['name']}")
                success = True
                break
            else:
                print(f"❌ {method['name']} tidak berhasil")
                log_message(f"Scan gagal dengan {method['name']}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {method['name']} timeout")
            log_message(f"Scan timeout dengan {method['name']}")
        except FileNotFoundError:
            print(f"📛 {method['name']} tidak tersedia")
            log_message(f"Tool tidak tersedia: {method['name']}")
        except Exception as e:
            print(f"❌ Error dengan {method['name']}: {e}")
            log_message(f"Error dengan {method['name']}: {e}")
    
    if not success:
        print("\n❌ Tidak dapat melakukan scan WiFi dengan metode apapun")
        print("\n💡 SOLUSI untuk Termux Android:")
        print("1. Install termux-api: pkg install termux-api")
        print("2. Berikan permission: termux-setup-storage")
        print("3. Berikan WiFi permission di pengaturan Android")
        print("4. Pastikan lokasi diaktifkan (diperlukan untuk WiFi scan)")
        print("5. Coba install: pkg install network-tools")
        log_message("WiFi scan gagal semua metode")

def check_wifi_connection_status():
    """Cek status koneksi WiFi terkini"""
    print("\n📶 WiFi Connection Status")
    log_message("Mengecek status koneksi WiFi")
    
    try:
        # Untuk Android Termux
        if platform.system() == "Linux" and "ANDROID_ROOT" in os.environ:
            result = subprocess.run(['termux-wifi-connectioninfo'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                wifi_info = json.loads(result.stdout)
                ssid = wifi_info.get('ssid', 'Not Connected')
                bssid = wifi_info.get('bssid', 'N/A')
                ip = wifi_info.get('ip', 'N/A')
                link_speed = wifi_info.get('link_speed', 'N/A')
                frequency = wifi_info.get('frequency', 'N/A')
                
                print(f"📶 SSID: {ssid}")
                print(f"📡 BSSID: {bssid}")
                print(f"🌐 IP Address: {ip}")
                print(f"⚡ Link Speed: {link_speed} Mbps")
                print(f"📊 Frequency: {frequency} MHz")
                print(f"🔗 Status: {'✅ Terhubung' if ssid != 'Not Connected' else '❌ Terputus'}")
                
                log_message(f"WiFi Status: SSID={ssid}, IP={ip}, Connected={ssid != 'Not Connected'}")
            else:
                print("❌ Tidak bisa mendapatkan info koneksi WiFi")
        else:
            # Untuk Linux biasa
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
                log_message("WiFi info via iwconfig")
            else:
                print("❌ Tidak bisa mendapatkan info WiFi")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        log_message(f"Error WiFi status: {e}")

def test_network_speed():
    """Test kecepatan upload/download jaringan"""
    print("\n🌐 Network Speed Test")
    log_message("Memulai speed test")
    
    if not SPEEDTEST_AVAILABLE:
        print("❌ Module 'speedtest-cli' belum terinstall!")
        print("Gunakan opsi '5. System Setup & Requirements' untuk install")
        return
    
    try:
        print("🔍 Mencari server terbaik...")
        st = speedtest.Speedtest()
        st.get_best_server()
        
        print("📥 Testing download speed...")
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        print(f"📥 Download Speed: {download_speed:.2f} Mbps")
        
        print("📤 Testing upload speed...")
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        print(f"📤 Upload Speed: {upload_speed:.2f} Mbps")
        
        print("📊 Testing ping...")
        ping = st.results.ping
        print(f"🏓 Ping: {ping:.2f} ms")
        
        print(f"🌐 Server: {st.results.server['name']}")
        print(f"🏢 Sponsor: {st.results.server['sponsor']}")
        
        log_message(f"SpeedTest - Download: {download_speed:.2f} Mbps, Upload: {upload_speed:.2f} Mbps, Ping: {ping:.2f} ms")
        
    except Exception as e:
        print(f"❌ Error speed test: {e}")
        log_message(f"Speed test error: {e}")

def check_current_network():
    """Cek informasi jaringan saat ini"""
    print("\n📊 Informasi Jaringan Saat Ini")
    log_message("Mengecek informasi jaringan saat ini")
    
    try:
        # IP addresses
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"📍 Local IP: {result.stdout.strip()}")
        
        # Gateway
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'default' in line:
                    print(f"🚪 Gateway: {line}")
                    break
        
        # DNS
        try:
            with open('/etc/resolv.conf', 'r') as f:
                dns_servers = [line for line in f if 'nameserver' in line]
                if dns_servers:
                    print("🔗 DNS Servers:")
                    for dns in dns_servers:
                        print(f"  {dns.strip()}")
        except:
            pass
        
        # Interface status
        print("\n📡 Network Interfaces:")
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            if result.returncode != 0:
                result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"❌ Error interfaces: {e}")
            
        log_message("Network info checked")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        log_message(f"Network info error: {e}")

def main():
    """Menu utama program"""
    # Setup logging pertama kali
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
        print("3. 📡 Hidden WiFi Checker")
        print("4. 💻 System Information")
        print("5. 🔧 System Setup & Requirements")
        print("6. 🚪 Keluar")
        
        print(f"\nStatus: requests {req_status}, speedtest {speed_status}")
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
            print("\n👋 Terima kasih telah menggunakan program!")
            print("📧 Support: https://github.com/your-repo")
            log_message("Program exited")
            break
        else:
            print("\n❌ Pilihan tidak valid!")
            log_message(f"Invalid menu choice: {choice}")
        
        input("\nTekan Enter untuk kembali ke menu...")

if __name__ == "__main__":
    try:
        if not REQUESTS_AVAILABLE:
            print("⚠️  Module 'requests' belum terinstall!")
            print("Gunakan opsi '5. System Setup & Requirements' di menu utama")
            input("Tekan Enter untuk lanjut...")
        
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program dihentikan oleh user")
        log_message("Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        log_message(f"Program error: {e}")
