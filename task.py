import os
import random
import string
import subprocess
import sys
import platform
from urllib.parse import urlparse

# Cek jika requests sudah terinstall
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

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
            ("colorama", "Warna terminal (opsional)")
        ]
        
        for package, purpose in packages_to_check:
            try:
                __import__(package)
                packages_status[package] = "✅"
                print(f"✅ {package:15} - OK")
            except ImportError:
                packages_status[package] = "❌"
                print(f"❌ {package:15} - Belum terinstall")
        
        print(f"\n💻 Sistem Operasi: {platform.system()} {platform.release()}")
        
        # Tampilkan menu options
        print("\n🔧 MENU SETUP:")
        print("1. Install All Requirements (Auto)")
        print("2. Install Requests (Website Checker)")
        print("3. Install Colorama (Warna Terminal)")
        print("4. Check System Information")
        print("5. Test Dependencies")
        print("6. Kembali ke Menu Utama")
        
        choice = input("\nPilih opsi (1-6): ").strip()
        
        if choice == "1":
            install_all_requirements()
        elif choice == "2":
            install_specific_package("requests")
        elif choice == "3":
            install_specific_package("colorama")
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
    
    requirements = [
        ("requests", "Untuk website checker"),
        ("colorama", "Untuk warna terminal")
    ]
    
    print("Package yang akan diinstall:")
    for package, description in requirements:
        print(f"  - {package:15} ({description})")
    
    confirm = input("\nApakah Anda ingin menginstall semua package? (y/n): ").lower()
    
    if confirm == 'y':
        print("\n🔧 Memulai installation...")
        success_count = 0
        total_count = len(requirements)
        
        for package, description in requirements:
            try:
                print(f"\n📦 Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} berhasil diinstall")
                success_count += 1
            except subprocess.CalledProcessError as e:
                print(f"❌ Gagal install {package}: {e}")
            except Exception as e:
                print(f"❌ Error saat install {package}: {e}")
        
        print(f"\n📊 HASIL INSTALLATION:")
        print(f"✅ Berhasil: {success_count}/{total_count}")
        
        if success_count == total_count:
            print("🎉 Semua package berhasil diinstall!")
            print("Silakan restart program untuk menerapkan perubahan.")
        else:
            print("⚠️ Beberapa package gagal diinstall.")
            print("Coba install manual dengan opsi specific.")
            
    else:
        print("Installation dibatalkan.")

def install_specific_package(package_name):
    """Install package tertentu"""
    print(f"\n=== INSTALL {package_name.upper()} ===")
    
    package_info = {
        "requests": "Library untuk HTTP requests (dibutuhkan Website Checker)",
        "colorama": "Library untuk warna di terminal (opsional)"
    }
    
    description = package_info.get(package_name, "Package utility")
    print(f"Package: {package_name}")
    print(f"Deskripsi: {description}")
    
    confirm = input(f"\nApakah Anda ingin menginstall {package_name}? (y/n): ").lower()
    
    if confirm == 'y':
        try:
            print(f"🔧 Installing {package_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ {package_name} berhasil diinstall!")
            
            # Update status
            global REQUESTS_AVAILABLE
            if package_name == "requests":
                try:
                    import requests
                    REQUESTS_AVAILABLE = True
                except ImportError:
                    pass
                    
        except subprocess.CalledProcessError as e:
            print(f"❌ Gagal install {package_name}: {e}")
            print("💡 Coba gunakan: pip install " + package_name)
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("Installation dibatalkan.")

def show_detailed_system_info():
    """Menampilkan informasi sistem detail"""
    print("\n=== DETAILED SYSTEM INFORMATION ===")
    
    # Basic info
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.architecture()[0]}")
    print(f"Processor: {platform.processor() or 'Tidak diketahui'}")
    
    # Python executable dan path
    print(f"Python Executable: {sys.executable}")
    print(f"Python Path: {sys.prefix}")
    
    # PIP information
    try:
        pip_version = subprocess.check_output([sys.executable, "-m", "pip", "--version"]).decode().strip()
        print(f"PIP Version: {pip_version}")
    except:
        print("PIP Version: Tidak dapat dideteksi")
    
    # Platform specific info
    system = platform.system()
    if system == "Windows":
        print("Windows Version:", platform.win32_ver())
    elif system == "Linux":
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if 'PRETTY_NAME' in line:
                        print("OS:", line.split('=')[1].strip().strip('"'))
                        break
        except:
            pass
            
        # Memory info untuk Linux/Android
        try:
            with open('/proc/meminfo', 'r') as f:
                mem_lines = f.readlines()[:3]
                print("\n💾 Memory Info:")
                for line in mem_lines:
                    print("  " + line.strip())
        except:
            pass
    
    elif "Android" in system:
        print("📱 Environment: Android Termux")
        try:
            # Cek termux packages
            result = subprocess.run(['pkg', 'list-installed'], capture_output=True, text=True)
            if result.returncode == 0:
                pkg_count = len([line for line in result.stdout.split('\n') if line.strip()])
                print(f"Installed Packages: {pkg_count}")
        except:
            pass

def test_dependencies():
    """Test semua dependencies"""
    print("\n=== DEPENDENCIES TEST ===")
    
    tests = [
        ("Python Version", test_python_version),
        ("Requests Module", test_requests),
        ("Network Connection", test_network),
        ("PIP Availability", test_pip),
        ("System Commands", test_system_commands)
    ]
    
    print("🧪 Menjalankan tests...\n")
    
    for test_name, test_func in tests:
        try:
            result, message = test_func()
            status = "✅" if result else "❌"
            print(f"{status} {test_name:20} : {message}")
        except Exception as e:
            print(f"❌ {test_name:20} : ERROR - {e}")

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
    
    try:
        print(f"\n🔍 Mengecek {url}...")
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"🟢 Status: {'✅ ONLINE' if response.status_code == 200 else '⚠️  MASALAH'}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f} detik")
        print(f"🖥️  Server: {response.headers.get('Server', 'Tidak diketahui')}")
        print(f"🔒 Encoding: {response.encoding}")
        print(f"📦 Size: {len(response.content)} bytes")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        print("Website tidak dapat diakses atau tidak ditemukan")

def random_string_generator():
    """Program untuk generate string acak"""
    print("\n=== RANDOM STRING GENERATOR ===")
    
    try:
        length = int(input("Panjang string: "))
        if length <= 0:
            print("❌ Panjang harus lebih dari 0!")
            return
        if length > 1000:
            print("⚠️  Panjang terlalu besar, mungkin akan lambat!")
    except ValueError:
        print("❌ Masukkan angka yang valid!")
        return
    
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
            return
        print(f"Menggunakan: {characters}")
    else:
        print("❌ Pilihan tidak valid!")
        return
    
    result = ''.join(random.choice(characters) for _ in range(length))
    print(f"\n🔹 String Acak: {result}")
    
    generate_more = input("\nGenerate lebih banyak? (y/n): ").lower()
    if generate_more == 'y':
        try:
            count = int(input("Berapa banyak string: "))
            if count > 20:
                print("⚠️  Jumlah terlalu besar, dibatasi 20")
                count = 20
                
            print("\n" + "=" * 40)
            print(f"📋 {count} RANDOM STRINGS:")
            print("=" * 40)
            for i in range(count):
                result = ''.join(random.choice(characters) for _ in range(length))
                print(f"{i+1:2d}. {result}")
        except ValueError:
            print("❌ Input tidak valid!")

def wifi_checker():
    """Program untuk mengecek jaringan WiFi (termasuk hidden)"""
    print("\n=== HIDDEN WIFI CHECKER ===")
    
    system = platform.system()
    print(f"Sistem: {system}")
    
    if system == "Windows":
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
    
    elif system == "Linux" or "Android" in system:
        print("\nPilihan:")
        print("1. Scan jaringan WiFi terdekat")
        print("2. Cek interface WiFi")
        print("3. Test koneksi internet")
        print("4. Informasi jaringan saat ini")
        
        choice = input("Pilih opsi (1-4): ").strip()
        
        if choice == "1":
            scan_wifi_linux()
        elif choice == "2":
            check_network_interfaces()
        elif choice == "3":
            test_internet_connection()
        elif choice == "4":
            check_current_network()
        else:
            print("❌ Pilihan tidak valid!")
    
    else:
        print(f"❌ Sistem {system} belum didukung sepenuhnya")

def scan_wifi_linux():
    """Scan WiFi untuk Linux/Android"""
    print("\n📡 Scanning WiFi networks...")
    
    commands_to_try = [
        ['termux-wifi-scaninfo'],
        ['nmcli', 'dev', 'wifi'],
        ['iwlist', 'scan'],
        ['iw', 'dev', 'list']
    ]
    
    success = False
    for cmd in commands_to_try:
        try:
            print(f"Mencoba: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                print(result.stdout)
                success = True
                break
        except:
            continue
    
    if not success:
        print("❌ Tidak dapat melakukan scan WiFi")
        print("\n💡 Tips untuk Termux Android:")
        print("1. Install: pkg install termux-api")
        print("2. Atau: pkg install nmap")
        print("3. Berikan permission: termux-setup-storage")

def check_network_interfaces():
    """Cek network interfaces"""
    try:
        print("\n📡 Network Interfaces:")
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        if result.returncode != 0:
            result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_internet_connection():
    """Test koneksi internet"""
    if not REQUESTS_AVAILABLE:
        print("❌ Tidak bisa test koneksi: 'requests' belum terinstall")
        return
        
    print("\n🌐 Testing koneksi internet...")
    try:
        response = requests.get('https://www.google.com', timeout=10)
        print("✅ Koneksi internet OK")
        print(f"⏱️  Response time: {response.elapsed.total_seconds():.2f}s")
    except:
        print("❌ Tidak ada koneksi internet")

def check_current_network():
    """Cek informasi jaringan saat ini"""
    try:
        print("\n📊 Informasi Jaringan Saat Ini:")
        
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"IP Address: {result.stdout.strip()}")
        
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'default' in line:
                    print(f"Gateway: {line}")
                    break
        
        try:
            with open('/etc/resolv.conf', 'r') as f:
                dns_servers = [line for line in f if 'nameserver' in line]
                if dns_servers:
                    print("DNS Servers:")
                    for dns in dns_servers:
                        print(f"  {dns.strip()}")
        except:
            pass
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Menu utama program"""
    while True:
        clear_screen()
        display_header()
        
        req_status = "✅" if REQUESTS_AVAILABLE else "❌"
        
        print("\n📋 MENU UTAMA:")
        print("1. 🔗 Website Checker")
        print("2. 🔤 Random String Generator") 
        print("3. 📡 Hidden WiFi Checker")
        print("4. 💻 System Information")
        print("5. 🔧 System Setup & Requirements")
        print("6. 🚪 Keluar")
        
        print(f"\nStatus: requests {req_status}")
        
        choice = input("\nPilih program (1-6): ").strip()
        
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
            break
        else:
            print("\n❌ Pilihan tidak valid!")
        
        input("\nTekan Enter untuk kembali ke menu...")

if __name__ == "__main__":
    if not REQUESTS_AVAILABLE:
        print("⚠️  Module 'requests' belum terinstall!")
        print("Gunakan opsi '5. System Setup & Requirements' di menu utama")
        input("Tekan Enter untuk lanjut...")
    
    main()
