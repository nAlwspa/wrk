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

def install_requirements():
    """Fungsi untuk menginstall requirements"""
    print("\n=== INSTALL REQUIREMENTS ===")
    
    requirements = [
        "requests",
        "colorama"
    ]
    
    print("Package yang akan diinstall:")
    for req in requirements:
        print(f"  - {req}")
    
    confirm = input("\nApakah Anda ingin menginstall package tersebut? (y/n): ").lower()
    
    if confirm == 'y':
        print("\n🔧 Menginstall requirements...")
        
        for package in requirements:
            try:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} berhasil diinstall")
            except subprocess.CalledProcessError as e:
                print(f"❌ Gagal install {package}: {e}")
            except Exception as e:
                print(f"❌ Error saat install {package}: {e}")
        
        print("\n🎉 Semua package berhasil diinstall!")
        print("Silakan restart program untuk menerapkan perubahan.")
        input("Tekan Enter untuk keluar...")
        sys.exit(0)
    else:
        print("Installation dibatalkan.")

def check_system_requirements():
    """Cek requirements sistem dan berikan rekomendasi"""
    print("\n=== SYSTEM REQUIREMENTS CHECK ===")
    
    issues = []
    
    # Cek Python version
    python_version = sys.version_info
    if python_version < (3, 6):
        issues.append(f"Python version {python_version[0]}.{python_version[1]} - Rekomendasi: Python 3.6+")
    else:
        print(f"✅ Python {python_version[0]}.{python_version[1]}.{python_version[2]} - OK")
    
    # Cek packages
    packages_to_check = [
        ("requests", "Untuk website checker"),
        ("colorama", "Untuk warna terminal (opsional)")
    ]
    
    for package, purpose in packages_to_check:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            issues.append(f"❌ {package} - Belum terinstall ({purpose})")
    
    # Cek sistem operasi
    system = platform.system()
    print(f"✅ Sistem Operasi: {system} - OK")
    
    if issues:
        print("\n⚠️  ISSUES YANG DITEMUKAN:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n💡 REKOMENDASI:")
        if system == "Windows":
            print("  - Jalankan sebagai Administrator jika perlu")
        elif system == "Linux":
            print("  - Gunakan 'sudo' untuk perintah yang butuh akses root")
        elif "Android" in system or "Linux" in system:
            print("  - Untuk Termux: pastikan sudah 'pkg update && pkg upgrade'")
        
        print("\n🔧 Gunakan opsi '5. Install Requirements' di menu utama")
        input("\nTekan Enter untuk lanjut...")
    else:
        print("\n🎉 Semua requirements terpenuhi!")
        input("Tekan Enter untuk lanjut...")

def website_checker():
    """Program untuk mengecek status website"""
    if not REQUESTS_AVAILABLE:
        print("❌ Module 'requests' belum terinstall!")
        print("Gunakan opsi '5. Install Requirements' terlebih dahulu")
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
        # Password kuat dengan minimal requirements
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
    
    # Generate random string
    result = ''.join(random.choice(characters) for _ in range(length))
    
    print(f"\n🔹 String Acak: {result}")
    
    # Tambahan: generate beberapa string sekaligus
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
            # Show available WiFi profiles
            result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                  capture_output=True, text=True, encoding='utf-8')
            print(result.stdout)
            
            # Show interfaces
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
        ['termux-wifi-scaninfo'],  # Termux specific
        ['nmcli', 'dev', 'wifi'],  # NetworkManager
        ['iwlist', 'scan'],        # iwlist
        ['iw', 'dev', 'list']      # iw
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
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            continue
    
    if not success:
        print("❌ Tidak dapat melakukan scan WiFi")
        print("\n💡 Tips untuk Termux Android:")
        print("1. Install: pkg install termux-api")
        print("2. Atau: pkg install nmap")
        print("3. Berikan permission: termux-setup-storage")
        print("4. Untuk iwlist: pkg install wireless-tools")

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
        
        # IP address
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"IP Address: {result.stdout.strip()}")
        
        # Gateway
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'default' in line:
                    print(f"Gateway: {line}")
                    break
        
        # DNS
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

def show_system_info():
    """Menampilkan informasi sistem"""
    print("\n=== SYSTEM INFORMATION ===")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.architecture()[0]}")
    print(f"Processor: {platform.processor()}")
    
    # Memory info (Linux/Android)
    if platform.system() in ["Linux", "Android"]:
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal' in line or 'MemAvailable' in line:
                        print(line.strip())
        except:
            pass

def main():
    """Menu utama program"""
    while True:
        clear_screen()
        display_header()
        
        # Tampilkan status requirements
        req_status = "✅" if REQUESTS_AVAILABLE else "❌"
        
        print("\n📋 MENU UTAMA:")
        print("1. 🔗 Website Checker")
        print("2. 🔤 Random String Generator") 
        print("3. 📡 Hidden WiFi Checker")
        print("4. 💻 System Information")
        print("5. 🔧 Install Requirements")
        print("6. ✅ Check System Requirements")
        print("7. 🚪 Keluar")
        
        print(f"\nStatus: requests {req_status}")
        
        choice = input("\nPilih program (1-7): ").strip()
        
        if choice == "1":
            website_checker()
        elif choice == "2":
            random_string_generator()
        elif choice == "3":
            wifi_checker()
        elif choice == "4":
            show_system_info()
        elif choice == "5":
            install_requirements()
        elif choice == "6":
            check_system_requirements()
        elif choice == "7":
            print("\n👋 Terima kasih telah menggunakan program!")
            print("📧 Support: https://github.com/your-repo")
            break
        else:
            print("\n❌ Pilihan tidak valid!")
        
        input("\nTekan Enter untuk kembali ke menu...")

if __name__ == "__main__":
    # Auto-check requirements pertama kali
    if not REQUESTS_AVAILABLE:
        print("⚠️  Module 'requests' belum terinstall!")
        print("Gunakan opsi '5. Install Requirements' di menu utama")
        input("Tekan Enter untuk lanjut...")
    
    main()
