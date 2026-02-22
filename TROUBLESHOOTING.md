# Port Scanner Sorun Giderme ve Kullanım Rehberi

## Neden Port Bulunamadı?

### 1. Ağ Bağlantısı Sorunları
- **Hedef cihaz çevrimdışı**: 192.168.1.70 adresindeki cihaz kapalı olabilir
- **Ağ bağlantısı**: Aynı ağda değilseniz erişemezsiniz
- **Firewall**: Hedef cihazda veya ağda firewall portları engelliyor olabilir

### 2. Port Durumu
- **Port kapalı**: 80 ve 1024 portları gerçekten kapalı olabilir
- **Servis çalışmıyor**: Web sunucusu (80) veya diğer servisler çalışmıyor olabilir

### 3. Timeout Ayarları
- **1 saniye çok kısa**: Yavaş ağlarda timeout artırılmalı
- **Yanıt süresi**: Bazı servisler yavaş yanıt verebilir

## Port Aralığı Seçimi

### Yaygın Port Aralıkları:

#### Sistem Portları (0-1023)
```
1-1024    : Temel servisler (HTTP, SSH, FTP, DNS, vb.)
21        : FTP
22        : SSH  
23        : Telnet
25        : SMTP
53        : DNS
80        : HTTP
110       : POP3
143       : IMAP
443       : HTTPS
```

#### Kullanıcı Portları (1024-49151)
```
1025-5000 : Uygulama portları
3306      : MySQL
3389      : RDP
5432      : PostgreSQL
6379      : Redis
8080      : HTTP-Alt
8443      : HTTPS-Alt
```

#### Dinamik Portlar (49152-65535)
```
49152-65535 : Geçici portlar
```

### Önerilen Tarama Stratejileri:

#### Hızlı Tarama (Yaygın Portlar)
```
1-1024     : Sistem portları
80,443,8080,8443 : Web portları
```

#### Detaylı Tarama
```
1-49151    : Tüm sistem ve kullanıcı portları
1-65535    : Tüm portlar (çok uzun sürebilir)
```

#### Özel Tarama
```
3306,3389,5432 : Veritabanı ve uzak masaüstü
```

## Thread Sayısı Nedir?

### Thread'in Anlamı:
Thread, aynı anda birden fazla işlem yapmayı sağlayan "iş parçacığı"dır.

### Thread Sayısı Seçimi:

#### Düşük Thread Sayısı (1-10)
- **Avantaj**: Az kaynak kullanır
- **Dezavantaj**: Çok yavaş tarama
- **Kullanım**: Yavaş sistemler veya dikkatli tarama

#### Orta Thread Sayısı (50-100) ⭐ **Önerilen**
- **Avantaj**: Hızlı ve stabil tarama
- **Dezavantaj**: Orta kaynak kullanımı
- **Kullanım**: Genel kullanım için ideal

#### Yüksek Thread Sayısı (200-500)
- **Avantaj**: Çok hızlı tarama
- **Dezavantaj**: Yüksek kaynak kullanımı, hedef sistem yük bindirebilir
- **Kullanım**: Hızlı tarama için ( dikkatli kullanın )

### Pratik Kural:
```
Ev kullanımı için: 50-100 thread
Kurumsal ağ için: 100-200 thread
İnternet taraması: 200-500 thread
```

## Sorun Çözüm Adımları

### 1. Bağlantı Testi
```bash
# Ping testi
ping 192.168.1.70

# Eğer ping cevap vermiyorsa, cihaz çevrimdışıdır
```

### 2. Bilinen Portları Test Et
```
Port aralığı: 22,80,443,3389
Thread sayısı: 50
```

### 3. Timeout Artır
- Programda timeout değerini 2-3 saniyeye çıkarın
- Özellikle internet taramasında timeout önemli

### 4. Farklı IP Test Et
```
# Kendi makineni test et
IP: 127.0.0.1
Port: 1-1000
```

### 5. Firewall Kontrolü
- Hedef cihazın firewall'ını kontrol et
- Ağ firewall'ını kontrol et

## Örnek Senaryolar

### Senaryo 1: Ev Ağı Taraması
```
IP: 192.168.1.1 (Router)
Port: 1-1024
Thread: 50
```

### Senaryo 2: Web Sunucusu Test
```
IP: 127.0.0.1 (Local)
Port: 80,443,8080,8443
Thread: 100
```

### Senaryo 3: Hızlı Kontrol
```
IP: Hedef IP
Port: 21,22,23,25,53,80,110,143,443,993,995
Thread: 100
```

## Güvenlik Uyarıları

1. **Sadece kendi ağınızı tarayın**
2. **İzinsiz tarama yasa dışıdır**
3. **Yüksek thread sayısı hedef sistemi yavaşlatabilir**
4. **Tarama logları bırakır, dikkatli olun**
