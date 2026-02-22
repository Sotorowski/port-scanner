#!/usr/bin/env python3
"""
Professional Port Scanner Tool

Bu araç, belirtilen IP adresindeki port aralığını tarayarak açık portları ve 
çalışan servisleri tespit eder. Threading kullanarak hızlı tarama yapar ve 
timeout mekanizması ile uzun beklemeleri önler.

Özellikler:
- Hızlı çoklu thread tarama
- Servis tespiti (HTTP, SSH, FTP, vb.)
- Timeout koruması
- Hata kontrolü ve validation
- Temiz ve modüler yapı
"""

import socket
import threading
import queue
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Well-known port services dictionary
COMMON_SERVICES = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS', 993: 'IMAPS',
    995: 'POP3S', 3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
    6379: 'Redis', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt'
}

def validate_ip_address(ip_address):
    """
    IP adresinin geçerliliğini kontrol eder.
    
    Args:
        ip_address (str): Kontrol edilecek IP adresi
        
    Returns:
        bool: IP adresi geçerliyse True, değilse False
    """
    try:
        socket.inet_aton(ip_address)
        return True
    except socket.error:
        return False

def validate_port_range(port_range):
    """
    Port aralığının geçerliliğini kontrol eder ve parse eder.
    
    Args:
        port_range (str): Port aralığı (örn: "1-1024")
        
    Returns:
        tuple: (start_port, end_port) veya None (hata durumunda)
    """
    try:
        if '-' in port_range:
            start, end = port_range.split('-')
            start_port = int(start.strip())
            end_port = int(end.strip())
        else:
            # Tek port girilmişse
            start_port = end_port = int(port_range.strip())
        
        if 1 <= start_port <= 65535 and 1 <= end_port <= 65535 and start_port <= end_port:
            return start_port, end_port
        return None
    except ValueError:
        return None

def scan_port(ip_address, port, timeout=1):
    """
    Belirtilen port'u tarar ve açık olup olmadığını kontrol eder.
    
    Args:
        ip_address (str): Hedef IP adresi
        port (int): Taranacak port
        timeout (int): Connection timeout süresi (saniye)
        
    Returns:
        tuple: (port, is_open, service_name) veya None
    """
    try:
        # Socket oluştur ve bağlanmayı dene
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        result = sock.connect_ex((ip_address, port))
        
        if result == 0:  # Port açık
            # Servis bilgisini al
            service_name = COMMON_SERVICES.get(port, 'Unknown')
            
            # Banner grabbing için deneme (opsiyonel)
            try:
                sock.send(b'GET / HTTP/1.1\r\n\r\n')
                banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                if banner and len(banner) > 5:
                    service_name += f" ({banner[:50]}...)"
            except:
                pass
            
            sock.close()
            return (port, True, service_name)
        
        sock.close()
        return None
        
    except Exception:
        return None

def port_scanner(ip_address, start_port, end_port, max_threads=100, timeout=1, specific_ports=None):
    """
    Port scanner ana fonksiyonu.
    
    Args:
        ip_address (str): Hedef IP adresi
        start_port (int): Başlangıç portu
        end_port (int): Bitiş portu
        max_threads (int): Maksimum thread sayısı
        timeout (int): Timeout süresi
        specific_ports (list): Belirli portların listesi (opsiyonel)
        
    Returns:
        list: Açık portların listesi [(port, service_name), ...]
    """
    print(f"\n🔍 {ip_address} adresi taranıyor...")
    
    if specific_ports:
        print(f"📊 Hedef portlar: {', '.join(map(str, specific_ports))}")
        ports_to_scan = specific_ports
    else:
        print(f"📊 Port aralığı: {start_port}-{end_port}")
        ports_to_scan = list(range(start_port, end_port + 1))
    
    print(f"⚡ Thread sayısı: {max_threads}")
    print(f"⏱️  Timeout: {timeout}s")
    print("-" * 60)
    
    open_ports = []
    total_ports = len(ports_to_scan)
    scanned_ports = 0
    
    start_time = time.time()
    
    # ThreadPoolExecutor ile threading yönetimi
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Tüm portları scan et
        future_to_port = {
            executor.submit(scan_port, ip_address, port, timeout): port 
            for port in ports_to_scan
        }
        
        for future in as_completed(future_to_port):
            scanned_ports += 1
            progress = (scanned_ports / total_ports) * 100
            
            # Progress bar
            sys.stdout.write(f"\rİlerleme: {scanned_ports}/{total_ports} ({progress:.1f}%)")
            sys.stdout.flush()
            
            result = future.result()
            if result:
                port, is_open, service_name = result
                open_ports.append((port, service_name))
    
    end_time = time.time()
    scan_duration = end_time - start_time
    
    print(f"\n\n✅ Tarama tamamlandı! ({scan_duration:.2f} saniye)")
    
    return open_ports

def print_results(open_ports, ip_address):
    """
    Tarama sonuçlarını ekrana yazdırır.
    
    Args:
        open_ports (list): Açık portların listesi
        ip_address (str): Hedef IP adresi
    """
    if open_ports:
        print(f"\n🎯 {ip_address} adresindeki açık portlar:")
        print("=" * 50)
        
        for port, service in sorted(open_ports):
            print(f"Port {port:5d}/tcp  ->  {service}")
        
        print(f"\n📈 Toplam {len(open_ports)} açık port bulundu.")
    else:
        print(f"\n❌ {ip_address} adresinde açık port bulunamadı.")

def get_user_input():
    """
    Kullanıcıdan giriş bilgilerini alır ve validation yapar.
    
    Returns:
        tuple: (ip_address, start_port, end_port, max_threads, specific_ports) veya None (hata durumunda)
    """
    print("🔧 Professional Port Scanner")
    print("=" * 40)
    print("💡 Kullanım Bilgileri:")
    print("   • IP adresi: Örn: 192.168.1.1 veya 127.0.0.1")
    print("   • Port aralığı: Örn: 1-1024 (aralık), 80 (tek port), 22,80,443 (çoklu port)")
    print("   • Thread sayısı: 1-500 arası (önerilen: 50-100)")
    print()
    
    # IP adresi al
    while True:
        ip_address = input("📍 Hedef IP adresi (örn: 192.168.1.1): ").strip()
        if validate_ip_address(ip_address):
            break
        print("❌ Geçersiz IP adresi! Lütfen formatı kontrol edin: 192.168.1.1")
    
    # Port aralığı al
    specific_ports = None
    while True:
        print("\n🔢 Port girişi seçenekleri:")
        print("   • Aralık:     1-1024 (1'den 1024'e kadar)")
        print("   • Tek port:   80 (sadece 80 portunu)")
        print("   • Çoklu:      22,80,443 (belirtilen portlar)")
        port_range = input("🔢 Port aralığı veya portlar (örn: 1-1024): ").strip()
        
        # Çoklu port kontrolü
        if ',' in port_range:
            try:
                ports = [int(p.strip()) for p in port_range.split(',')]
                if all(1 <= p <= 65535 for p in ports):
                    specific_ports = ports
                    start_port, end_port = min(ports), max(ports)
                    break
                print("❌ Portlar 1-65535 arasında olmalı!")
            except ValueError:
                print("❌ Geçersiz port formatı! Örn: 22,80,443")
        else:
            # Tek port veya aralık
            ports = validate_port_range(port_range)
            if ports:
                start_port, end_port = ports
                break
            print("❌ Geçersiz port aralığı! Örn: 1-1024, 80, veya 22,80,443")
    
    # Thread sayısı al (opsiyonel)
    while True:
        try:
            threads = input("\n⚙️  Thread sayısı (1-500, varsayılan: 100): ").strip()
            max_threads = int(threads) if threads else 100
            if 1 <= max_threads <= 500:
                break
            print("❌ Thread sayısı 1-500 arasında olmalı!")
        except ValueError:
            print("❌ Geçersiz sayı! Lütfen rakam girin.")
    
    return ip_address, start_port, end_port, max_threads, specific_ports

def main():
    """
    Ana program fonksiyonu.
    """
    try:
        # Kullanıcıdan giriş al
        user_input = get_user_input()
        if not user_input:
            return
        
        ip_address, start_port, end_port, max_threads, specific_ports = user_input
        
        # Port taraması yap
        open_ports = port_scanner(ip_address, start_port, end_port, max_threads, specific_ports=specific_ports)
        
        # Sonuçları yazdır
        print_results(open_ports, ip_address)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tarama kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")

if __name__ == "__main__":
    main()
