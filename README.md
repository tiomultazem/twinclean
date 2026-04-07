
---

# TwinClean

**TwinClean** adalah aplikasi untuk mencari dan menghapus file duplikat di komputer Anda
dengan mudah. Duplikat file akan tampil berdekatan atas bawah di hasil pencarian.


---

## ✨ Cara Kerja Aplikasi

Setiap file memiliki isi berupa data (byte).
Data ini kemudian dihitung menggunakan MD5 sehingga menghasilkan kode unik (disebut hash).

TwinClean membandingkan hash dari setiap file:

- Jika hash sama persis, maka isi file 100% identik → dianggap duplikat
- Jika berbeda sedikit saja, hash akan ikut berubah → dianggap file berbeda

---

## ✨ Apa yang Bisa Dilakukan?

* Mencari file yang sama (duplikat) secara otomatis
* Menampilkan daftar file yang ditemukan
* Memilih file mana yang ingin dihapus
* Menghapus file dengan aman

---

## ▶️ Cara Menggunakan

### Cara 1 (Paling mudah – tanpa instal Python)

1. Buka file **TwinClean.exe**
2. Klik tombol **Browse** untuk memilih folder
3. Klik **Scan**
4. Pilih file duplikat yang ingin dihapus
5. Klik **Hapus**

---

### Cara 2 (Menggunakan Python)

1. Pastikan Python sudah terpasang
2. Jalankan perintah:

```bash
python app.py
```

---

## ⚠️ Perhatian

* Pastikan Anda tidak menghapus file penting
* Disarankan tidak digunakan pada folder sistem

---

## 📄 Lisensi

Hak Cipta © 2025 Gilang Wahyu Prasetyo
Digunakan untuk keperluan pribadi dan edukasi.
