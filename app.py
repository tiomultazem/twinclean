import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
import sys
import subprocess

class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pendeteksi File Duplikat")
        self.root.geometry("1200x750")

        self.selected_dir = tk.StringVar()
        self.duplicates = []
        self.selected_files = set()
        self.abort_flag = False

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.map("Treeview", background=[("selected", "#3399FF")])
        style.configure("Treeview", rowheight=24)
        style.configure("Treeview.Heading", font=(None, 10, "bold"))
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        self.tree_hover_row = None
        self.root.bind_all("<Motion>", self.on_hover, add="+")

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Pilih Folder:").pack(side=tk.LEFT, padx=5)
        tk.Entry(frame, textvariable=self.selected_dir, width=50).pack(side=tk.LEFT)
        tk.Button(frame, text="Browse", command=self.browse_directory).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Cari Duplikat", command=self.find_duplicates).pack(side=tk.LEFT, padx=5)

        columns = ("selected", "name", "date", "type", "size", "path")
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree_scroll_y = tk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x = tk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show='headings',
            selectmode='browse',
            height=20,
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set
        )

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=200 if col == 'path' else 140, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Button-1>", self.toggle_selection)
        self.tree.bind("<Double-1>", self.open_in_explorer)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate", length=800)
        self.progress.pack(pady=5)
        self.progress_label = tk.Label(self.root, text="")
        self.progress_label.pack()

        self.delete_btn = tk.Button(self.root, text="Hapus File yang Dicentang", command=self.confirm_delete, bg='red', fg='white')
        self.delete_btn.pack(pady=5)

        self.restart_btn = tk.Button(self.root, text="Restart Aplikasi", command=self.restart_app, bg='blue', fg='white')
        self.restart_btn.pack(pady=5)

        self.stop_btn = tk.Button(self.root, text="Stop Proses", command=self.stop_process, bg='orange', fg='black')
        self.stop_btn.pack(pady=5)

    def on_hover(self, event):
        region = self.tree.identify("region", event.x, event.y)
        row_id = self.tree.identify_row(event.y)
        if region == "cell" and row_id:
            if self.tree_hover_row != row_id:
                if self.tree_hover_row:
                    self.tree.item(self.tree_hover_row, tags=())
                self.tree_hover_row = row_id
                self.tree.item(row_id, tags=("hover",))
                self.tree.tag_configure("hover", background="#cceeff")

    def browse_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.selected_dir.set(dir_path)

    def hash_file(self, path):
        hasher = hashlib.md5()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return None

    def find_duplicates(self):
        self.abort_flag = False
        directory = self.selected_dir.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", "Direktori tidak valid.")
            return

        self.tree.delete(*self.tree.get_children())
        self.duplicates.clear()
        self.selected_files.clear()

        hashes = {}
        all_files = []

        for foldername, subfolders, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                all_files.append(filepath)

        total = len(all_files)
        self.progress["maximum"] = total
        self.progress["value"] = 0
        self.progress_label.config(text="0%")
        self.root.update_idletasks()

        for i, filepath in enumerate(all_files):
            if self.abort_flag:
                self.progress_label.config(text="Dibatalkan!")
                return
            filehash = self.hash_file(filepath)
            if filehash:
                if filehash in hashes:
                    self.duplicates.append((hashes[filehash], filepath))
                else:
                    hashes[filehash] = filepath
            self.progress["value"] = i + 1
            percent = int(((i + 1) / total) * 100)
            self.progress_label.config(text=f"{percent}%")
            self.root.update_idletasks()

        seen = set()
        for original, dup in self.duplicates:
            for path in (original, dup):
                if path in seen:
                    continue
                seen.add(path)
                try:
                    stat = os.stat(path)
                    file_id = self.tree.insert('', 'end', values=(
                        '',
                        os.path.basename(path),
                        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_ctime)),
                        os.path.splitext(path)[1],
                        f"{stat.st_size/1024:.2f} KB",
                        path
                    ))
                except:
                    continue

        if not self.duplicates:
            messagebox.showinfo("Hasil", "Tidak ditemukan file duplikat.")

    def stop_process(self):
        self.abort_flag = True

    def toggle_selection(self, event):
        region = self.tree.identify("region", event.x, event.y)
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row_id or col != '#1':
            return

        current = self.tree.set(row_id, "selected")
        new_value = '✅' if current == '' else ''
        self.tree.set(row_id, "selected", new_value)
        path = self.tree.set(row_id, "path")

        if new_value:
            self.selected_files.add(path)
        else:
            self.selected_files.discard(path)

    def open_in_explorer(self, event):
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row_id or col != '#2':
            return
        path = self.tree.set(row_id, "path")
        if os.path.isfile(path):
            try:
                subprocess.run(["explorer", "/select,", os.path.normpath(path)], check=False)
            except Exception as e:
                messagebox.showerror("Gagal membuka", str(e))

    def confirm_delete(self):
        to_delete = list(self.selected_files)
        if not to_delete:
            messagebox.showinfo("Info", "Tidak ada file yang dipilih untuk dihapus.")
            return

        if messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin menghapus {len(to_delete)} file?"):
            deleted = 0
            for path in to_delete:
                try:
                    os.remove(path)
                    deleted += 1
                except:
                    continue
            messagebox.showinfo("Selesai", f"Berhasil menghapus {deleted} file.")
            self.find_duplicates()

    def restart_app(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()
