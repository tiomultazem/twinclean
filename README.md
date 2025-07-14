# TwinClean

**TwinClean** adalah aplikasi GUI berbasis Python (`tkinter`) untuk mendeteksi dan menghapus file duplikat pada sistem operasi Windows. Dirancang untuk pengguna non-teknis maupun teknis, TwinClean menawarkan antarmuka yang sederhana, progresif, dan interaktif.

---

## 🚀 Fitur Utama

- Deteksi file duplikat berdasarkan **hash MD5** (bit-level accuracy).
- UI berbasis **Tkinter** dengan:
  - Tombol `Browse` untuk pilih folder.
  - **Progress bar** dan persentase pemindaian.
  - **Tabel interaktif** hasil deteksi (nama, tipe, ukuran, tanggal, path).
  - **Checkbox simulatif** untuk pilih file duplikat yang ingin dihapus.
  - **Klik dua kali** membuka File Explorer dengan file langsung terseleksi.
  - **Hover** baris dengan highlight biru muda.
  - **Klik 1x** = highlight biru aktif.
- Tombol **Stop Proses** dan **Restart Aplikasi**.
- **Scroll horizontal & vertikal** untuk tabel besar.

---

## 🛠 Penjelasan Teknis

### 1. Hashing File

```python
hashlib.md5()  # digunakan untuk menghitung hash isi file secara bit-per-bit
```

### 2. Struktur UI

```python
tk.Tk() + ttk.Treeview
```

- Scrollbar:
  - vertikal → `yscrollcommand`
  - horizontal → `xscrollcommand` via `Canvas` wrapper
- Responsive layout

### 3. Hover & Seleksi

```python
tree.bind('<Motion>', ...)     # hover effect
tree.bind('<Button-1>', ...)   # toggle centang (checkbox simulatif)
tree.bind('<Double-1>', ...)   # buka file di File Explorer (select file)
```

### 4. Penghapusan File

```python
os.remove(path)  # hanya hapus file yang dicentang
```

### 5. Restart Aplikasi

```python
os.execl(sys.executable, sys.executable, *sys.argv)
```

---

## ▶️ Cara Menjalankan

```bash
python app.py
```

> Pastikan sudah terinstal:
> - Python 3.x
> - Modul `tkinter` (default di Windows)

---

## ⚠️ Catatan Tambahan

- Hanya mendeteksi file duplikat berdasarkan **isi file**, bukan berdasarkan nama.
- Tidak disarankan digunakan di folder sistem (misalnya: `C:\\Windows`) kecuali dijalankan sebagai administrator.

---

## 📄 Lisensi

```
Hak Cipta © 2025 Gilang Wahyu Prasetyo - BPS Kabupaten Tabalong

Diperbolehkan digunakan untuk keperluan pribadi dan edukasi,
tidak untuk komersialisasi tanpa izin tertulis dari pemilik hak cipta.
```
