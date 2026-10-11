# Diagnosa DNS & keterjangkauan port

## Alur `dig` yang benar (dari terdekat ke otoritatif)
```sh
whois <domain> | grep -iE 'registrar|name server|status|expiry'   # siapa pengelolanya
dig +short NS <domain>                                            # NS delegasi
dig +short NS <domain-parent>                                     # server TLD

# Query NS OTORITATIF langsung (langkah paling menentukan):
for ns in $(dig +short NS <domain>); do
  echo "--- $ns ---"
  dig @$ns <domain> A +noall +answer +authority
  dig @$ns <domain> SOA +short          # SOA ada = zone hidup
  dig @$ns <domain> +noall +comments | grep -oE 'status: [A-Z]+'
done
```

## Membaca status
| Status | Dari | Arti | Tindakan |
|---|---|---|---|
| `NOERROR` + answer | NS otoritatif | Zone hidup, record ada | Lanjut ke port/ingress |
| `NOERROR` + 0 answer | NS otoritatif | Zone hidup, record belum ada | Tambah A record |
| `REFUSED` | NS otoritatif | NS hidup, **tidak punya zone itu** | Zone belum di-provision di provider → aktifkan di provider, atau pindah NS |
| `SERVFAIL` | resolver publik | Tak bisa dapat jawaban (delegasi/zone bermasalah) | Cek NS otoritatif untuk tahu sebabnya |
| `SERVFAIL`/timeout | NS otoritatif | NS tak menjawab | Provider DNS bermasalah |

Kontrol cepat: query zone lain yang dikelola provider yang sama (`dig @<ns> <provider-domain> SOA`).
Kalau zone itu `NOERROR` tapi domain kita `REFUSED`, masalahnya di zone domain kita, bukan servernya.

## Verifikasi keterjangkauan port DARI LUAR
Tes dari host yang sama tidak sah (NAT hairpin). Pakai layanan eksternal:
```sh
# 1) siapkan listener sementara (atau pakai layanan asli yang sudah listen)
sudo python3 -m http.server 80 --bind 0.0.0.0 >/tmp/probe.log 2>&1 &

# 2) minta check-host.net memeriksa dari beberapa node
RID=$(curl -s "https://check-host.net/check-tcp?host=<IP>:80&max_nodes=4" \
  -H "Accept: application/json" | grep -o '"request_id":"[^"]*"' | cut -d'"' -f4)
sleep 8
curl -s "https://check-host.net/check-result/$RID" -H "Accept: application/json"
#   {"address":"<IP>","time":...}  -> TERBUKA dari luar
#   {"error":"Connection timed out"} -> diblok (security group atau firewall host)

# 3) bersihkan listener sementara
sudo pkill -f "http.server 80"
```
Ulangi untuk port 443. Jangan tinggalkan listener sementara berjalan.
