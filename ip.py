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

def ip_lookup():
    while True:
        ip = input("Masukkan IP address: ")
        if validate_ip(ip):
            try:
                response = requests.get(f"https://ipapi.co/{ip}/json/")
                if response.status_code == 200:
                    data = response.json()
                    print(f"\nInformasi untuk IP {ip}:")
                    print(f"IP: {data.get('ip', 'N/A')}")
                    print(f"Kota: {data.get('city', 'N/A')}")
                    print(f"Region: {data.get('region', 'N/A')}")
                    print(f"Negara: {data.get('country_name', 'N/A')}")
                    print(f"Kode Negara: {data.get('country_code', 'N/A')}")
                    print(f"Zona Waktu: {data.get('timezone', 'N/A')}")
                    print(f"ISP: {data.get('org', 'N/A')}")
                    print(f"Latitude: {data.get('latitude', 'N/A')}")
                    print(f"Longitude: {data.get('longitude', 'N/A')}")
                    
                    lat = data.get('latitude')
                    lon = data.get('longitude')
                    if lat and lon:
                        maps_url = f"https://maps.google.com/?q={lat},{lon}"
                        print(f"Google Maps: {maps_url}")
                    else:
                        print("Google Maps: Lokasi tidak tersedia")
                else:
                    print("Gagal mengambil data IP")
            except Exception as e:
                print(f"Error: {e}")
            break
        else:
            print("IP tidak valid, silakan coba lagi")

def main():
    while True:
        print("\n1. IP Lookup")
        print("2. Keluar")
        
        pilihan = input("Pilih menu (1-2): ")
        
        if pilihan == '1':
            ip_lookup()
        elif pilihan == '2':
            print("Program selesai")
            break
        else:
            print("Pilihan tidak valid")

if __name__ == "__main__":
    main()
