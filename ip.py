import requests
import re

def validate_ip(ip):
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    match = re.match(pattern, ip)
    if not match:
        return False
    for group in match.groups():
        if int(group) > 255:
            return False
    return True

def validate_mac(mac):
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return re.match(pattern, mac) is not None

def ip_lookup():
    while True:
        ip = input("Masukkan IP address: ")
        if validate_ip(ip):
            try:
                response = requests.get(f"https://iplocation.io/ip/{ip}")
                if response.status_code == 200:
                    print(f"\nInformasi untuk IP {ip}:")
                    print(response.text)
                else:
                    print("Gagal mengambil data IP")
            except:
                print("Error: Tidak dapat terhubung ke server")
            break
        else:
            print("IP tidak valid, silakan coba lagi")

def mac_lookup():
    while True:
        mac = input("Masukkan MAC address: ")
        if validate_mac(mac):
            print(f"MAC {mac} valid")
            break
        else:
            print("MAC tidak valid, silakan coba lagi")

def main():
    while True:
        print("\n1. IP Lookup")
        print("2. MAC Lookup")
        print("3. Keluar")
        
        pilihan = input("Pilih menu (1-3): ")
        
        if pilihan == '1':
            ip_lookup()
        elif pilihan == '2':
            mac_lookup()
        elif pilihan == '3':
            print("Program selesai")
            break
        else:
            print("Pilihan tidak valid")

if __name__ == "__main__":
    main()
