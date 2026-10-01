"""Точка входа в приложение складского учёта."""
import customtkinter as ctk
from tkinter import messagebox

from api_client import ApiClient, ApiError
from database import api_base_url, serial_port
from scale import ScaleMonitor
from ui.main_window import MainWindow


def main():
    client = ApiClient(api_base_url())
    try:
        client.health()
    except ApiError as error:
        root = ctk.CTk()
        root.withdraw()
        messagebox.showerror(
            'Сервер недоступен',
            f'{error}\n\nСначала запустите API:\n'
            '  cd server\n'
            '  uvicorn app.main:app --host 0.0.0.0 --port 8000',
        )
        return

    root = ctk.CTk()
    monitor = ScaleMonitor(client, port=serial_port())
    app = MainWindow(root, client, scale_monitor=monitor)

    def on_weight(_value):
        root.after(0, app._refresh_items)

    monitor.on_weight = on_weight
    monitor.start()
    try:
        root.mainloop()
    finally:
        monitor.stop()


if __name__ == '__main__':
    main()
