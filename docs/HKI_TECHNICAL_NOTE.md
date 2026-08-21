# Catatan Teknis HKI LOGIVISTA SULAMPUA

## 1. Identitas program

- Nama: LOGIVISTA SULAMPUA
- Judul teknis: Sistem Analitik Visibilitas Jaringan Distribusi dan Disparitas Harga Komoditas Antarpulau Berbasis PDI-CV
- Versi implementasi: 0.1.0
- Tahun: 2026
- Jenis ciptaan yang dituju: Program Komputer
- Cakupan awal: Kabupaten Halmahera Barat
- Status: implementasi referensi dari draf teknis

## 2. Kontribusi teknis yang diwujudkan

Implementasi memisahkan lima lapisan fungsi:

1. validasi dan normalisasi observasi harga serta data rute;
2. agregasi harga per wilayah dengan metadata sumber dan periode;
3. perhitungan CV populasi dan PDI v0.1;
4. analisis jaringan distribusi terarah dan konektivitas lemah;
5. penyajian melalui API, dashboard, serta jejak audit SQLite.

Kode sumber, organisasi modul, struktur data, alur API, tampilan dashboard, dokumentasi, dan materi contoh merupakan ekspresi program yang disimpan dalam repositori ini.

## 3. Batas formula

PDI v0.1 didefinisikan sebagai:

```text
(harga rata-rata wilayah maksimum - harga rata-rata wilayah minimum)
------------------------------------------------------------------- × 100%
                rata-rata harga seluruh wilayah
```

Nama versi harus selalu disertakan. Formula ini adalah usulan operasional pada draf dan belum dinyatakan sebagai standar statistik universal atau indeks resmi pemerintah.

CV dihitung dari simpangan baku populasi harga rata-rata wilayah. Keputusan tersebut harus dicatat dalam laporan agar hasil dapat direplikasi.

## 4. Batas data dan wilayah

- Data di folder `samples/` bersifat sintetis dan anonim.
- Nama wilayah administratif pada contoh hanya digunakan untuk konteks demonstrasi.
- Tidak ada koordinat rinci, identitas pedagang, kredensial, atau data personal.
- Nama SULAMPUA adalah arah perluasan. Versi 0.1.0 hanya menetapkan Halmahera Barat sebagai wilayah implementasi awal.
- Integrasi SP2KP/SIGM, BPS, pelabuhan, pasar, atau sumber lain belum diklaim aktif.

## 5. Reproduksibilitas

Pengujian otomatis memeriksa:

- nilai CV dan PDI v0.1 pada data yang hasilnya diketahui;
- agregasi rata-rata per wilayah;
- penolakan kolom wajib yang tidak lengkap;
- penolakan campuran komoditas dan satuan;
- deteksi komponen jaringan terpisah;
- metrik derajat simpul dan lead time berbobot frekuensi;
- impor CSV;
- penyimpanan audit SQLite.

Perintah:

```bash
python -m unittest discover -s backend/tests -v
```

## 6. Bukti versi untuk pengajuan

Sebelum pendaftaran, disarankan menyimpan:

1. arsip ZIP rilis;
2. hash SHA-256 arsip;
3. URL repositori;
4. SHA commit yang diajukan;
5. tanggal rilis dan tangkapan layar halaman rilis;
6. hasil pengujian otomatis;
7. lampiran program komputer yang konsisten dengan versi kode.

Dokumen pengajuan sebaiknya tidak hanya menautkan cabang `main`, karena isi cabang dapat berubah. Gunakan tautan commit atau tag yang bersifat tetap.

## 7. Pencipta dan hak

Pencipta:

- Miftahol Arifin
- Famila Dwi Winati
- Rui Almer

Pemegang Hak Cipta: Telkom University.

Publikasi repositori tidak mengalihkan hak dan tidak otomatis memberi lisensi penggunaan kepada pihak lain.
