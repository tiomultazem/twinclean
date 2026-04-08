import os
import sys
import time
import hashlib
import subprocess
import tkinter as tk
from tkinter import filedialog

import flet as ft


class DuplicateFinderApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "TwinClean-Detektor File Duplikat"
        self.page.window.width = 1200
        self.page.window.height = 750
        self.page.padding = 12
        self.page.theme_mode = ft.ThemeMode.DARK

        self.selected_dir = ""
        self.selected_files = set()
        self.abort_flag = False
        self.rows_data = []
        self.duplicate_groups = []
        self.delete_dialog = None

        self.dir_text = ft.TextField(
            label="Pilih Folder",
            expand=True,
            read_only=True,
        )

        self.progress = ft.ProgressBar(value=0, width=500)
        self.progress_label = ft.Text("")

        self.table = ft.DataTable(
            expand=True,
            show_checkbox_column=True,
            column_spacing=20,
            heading_row_height=42,
            data_row_min_height=40,
            columns=[
                ft.DataColumn(ft.Text("Grup")),
                ft.DataColumn(ft.Text("Nama")),
                ft.DataColumn(ft.Text("Tanggal")),
                ft.DataColumn(ft.Text("Tipe")),
                ft.DataColumn(ft.Text("Ukuran")),
                ft.DataColumn(ft.Text("Path")),
                ft.DataColumn(ft.Text("Aksi")),
            ],
            rows=[],
        )

        self.btn_browse = ft.Button("Browse", on_click=self.browse_directory)
        self.btn_scan = ft.Button("Cari Duplikat", on_click=self.start_find_duplicates)
        self.btn_stop = ft.Button("Stop Proses", on_click=self.stop_process)
        self.btn_delete = ft.Button("Hapus File yang Dicentang", on_click=self.confirm_delete)

        self.footer_text = ft.Text(
            spans=[
                ft.TextSpan("Made with "),
                ft.TextSpan(
                    "❤️",
                    on_click=self.toggle_theme,
                    style=ft.TextStyle(),
                ),
                ft.TextSpan(" Gilang Wahyu Prasetyo © BPS Kabupaten Tabalong"),
            ],
            size=12,
        )

        self.build_ui()
        self.update_footer_theme()

    def build_ui(self):
        self.page.add(
            ft.Column(
                expand=True,
                controls=[
                    ft.Row(
                        controls=[
                            self.dir_text,
                            self.btn_browse,
                            self.btn_scan,
                            self.btn_stop,
                            self.btn_delete,
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(content=self.progress, padding=0),
                            self.progress_label,
                        ]
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[self.table],
                        ),
                    ),
                    ft.Container(
                        padding=ft.Padding.only(top=4),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[self.footer_text],
                        ),
                    ),
                ],
            )
        )

    def update_footer_theme(self):
        if self.page.theme_mode == ft.ThemeMode.DARK:
            text_color = ft.Colors.GREY_500
        else:
            text_color = ft.Colors.GREY_700

        self.footer_text.color = text_color
        self.page.update()

    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
        self.update_footer_theme()

    def browse_directory(self, e):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory()
        root.destroy()

        if folder:
            self.selected_dir = folder
            self.dir_text.value = folder
            self.page.update()

    def hash_file(self, path):
        hasher = hashlib.md5()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    if self.abort_flag:
                        return None
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None

    def start_find_duplicates(self, e):
        self.page.run_thread(self.find_duplicates)

    def find_duplicates(self):
        self.abort_flag = False
        directory = self.selected_dir

        if not os.path.isdir(directory):
            self.progress_label.value = "Direktori tidak valid."
            self.page.update()
            return

        self.table.rows = []
        self.selected_files.clear()
        self.rows_data.clear()
        self.duplicate_groups.clear()

        hashes = {}
        all_files = []

        for foldername, subfolders, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                all_files.append(filepath)

        total = len(all_files)
        if total == 0:
            self.progress.value = 0
            self.progress_label.value = "Folder kosong."
            self.page.update()
            return

        self.progress.value = 0
        self.progress_label.value = "0%"
        self.page.update()

        for i, filepath in enumerate(all_files):
            if self.abort_flag:
                self.progress_label.value = "Dibatalkan!"
                self.page.update()
                return

            filehash = self.hash_file(filepath)
            if filehash:
                hashes.setdefault(filehash, []).append(filepath)

            self.progress.value = (i + 1) / total
            percent = int(((i + 1) / total) * 100)
            self.progress_label.value = f"{percent}%"
            self.page.update()

        grouped_paths = [paths for paths in hashes.values() if len(paths) > 1]

        self.duplicate_groups = grouped_paths

        for group_index, group_paths in enumerate(self.duplicate_groups, start=1):
            for path in group_paths:
                try:
                    stat = os.stat(path)
                    self.rows_data.append(
                        {
                            "group": group_index,
                            "name": os.path.basename(path),
                            "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_ctime)),
                            "type": os.path.splitext(path)[1],
                            "size": f"{stat.st_size/1024:.2f} KB",
                            "path": path,
                        }
                    )
                except Exception:
                    continue

        self.build_rows()

        if not self.duplicate_groups:
            self.progress_label.value = "Tidak ditemukan file duplikat."
        else:
            self.progress_label.value = (
                f"Ditemukan {len(self.rows_data)} file duplikat dalam {len(self.duplicate_groups)} grup."
            )

        self.page.update()

    def build_rows(self):
        rows = []

        for item in self.rows_data:
            path = item["path"]

            rows.append(
                ft.DataRow(
                    selected=path in self.selected_files,
                    on_select_change=lambda e, p=path: self.toggle_selection(e, p),
                    cells=[
                        ft.DataCell(ft.Text(str(item["group"]))),
                        ft.DataCell(ft.Text(item["name"])),
                        ft.DataCell(ft.Text(item["date"])),
                        ft.DataCell(ft.Text(item["type"])),
                        ft.DataCell(ft.Text(item["size"])),
                        ft.DataCell(ft.Text(path)),
                        ft.DataCell(
                            ft.Button("Buka", on_click=lambda e, p=path: self.open_in_explorer(p))
                        ),
                    ],
                )
            )

        self.table.rows = rows

    def toggle_selection(self, e, path):
        selected = str(e.data).lower() == "true"
        if selected:
            self.selected_files.add(path)
        else:
            self.selected_files.discard(path)
        e.control.selected = selected
        self.page.update()

    def open_in_explorer(self, path):
        if os.path.isfile(path):
            try:
                subprocess.run(["explorer", "/select,", os.path.normpath(path)], check=False)
            except Exception:
                pass

    def confirm_delete(self, e):
        total = len(self.selected_files)

        if total == 0:
            self.progress_label.value = "Tidak ada file yang dipilih untuk dihapus."
            self.page.update()
            return

        self.delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Konfirmasi Penghapusan"),
            content=ft.Text(f"Apakah Anda yakin ingin menghapus {total} file yang dipilih?"),
            actions=[
                ft.TextButton("Batal", on_click=self.cancel_delete),
                ft.TextButton("Ya, Hapus", on_click=self.handle_confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.show_dialog(self.delete_dialog)

    def cancel_delete(self, e):
        self.page.pop_dialog()
        self.page.update()

    def handle_confirm_delete(self, e):
        self.page.pop_dialog()
        self.page.update()
        self.do_delete_selected_files()

    def do_delete_selected_files(self):
        to_delete = list(self.selected_files)

        if not to_delete:
            self.progress_label.value = "Tidak ada file yang dipilih untuk dihapus."
            self.page.update()
            return

        deleted = 0
        for path in to_delete:
            try:
                os.remove(path)
                deleted += 1
            except Exception:
                continue

        self.progress_label.value = f"Berhasil menghapus {deleted} file."
        self.page.update()
        self.find_duplicates()

    def stop_process(self, e):
        self.abort_flag = True
        self.progress_label.value = "Menghentikan proses..."
        self.page.update()

    def restart_app(self, e=None):
        python = sys.executable
        os.execl(python, python, *sys.argv)


def main(page: ft.Page):
    DuplicateFinderApp(page)


if __name__ == "__main__":
    ft.run(main)