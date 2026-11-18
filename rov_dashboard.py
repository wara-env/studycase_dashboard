import tkinter as tk
from tkinter import messagebox, ttk

class ROVDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ROV Dashboard Terintegrasi - ABYAN MAHESWARA")
        self.root.geometry("750x620")

        # --- 1. FRAME MONITORING SENSOR ---
        sensor_frame = ttk.LabelFrame(root, text="Simulasi Sensor Wahana")
        sensor_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(sensor_frame, text="Suhu Air (°C):").grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.entry_temp = ttk.Entry(sensor_frame, width=10)
        self.entry_temp.insert(0, "28") 
        self.entry_temp.grid(row=0, column=1, padx=5, pady=8)

        # Parameter Kedalaman yang sebelumnya kurang
        ttk.Label(sensor_frame, text="Kedalaman (m):").grid(row=0, column=2, padx=5, pady=8, sticky="w")
        self.entry_depth = ttk.Entry(sensor_frame, width=10)
        self.entry_depth.insert(0, "5") 
        self.entry_depth.grid(row=0, column=3, padx=5, pady=8)

        ttk.Label(sensor_frame, text="Sisa Baterai (%):").grid(row=0, column=4, padx=5, pady=8, sticky="w")
        self.entry_batt = ttk.Entry(sensor_frame, width=10)
        self.entry_batt.insert(0, "80") 
        self.entry_batt.grid(row=0, column=5, padx=5, pady=8)

        # --- 2. FRAME KONTROL THRUSTER ---
        control_frame = ttk.LabelFrame(root, text="Kontrol Mekanis Thruster")
        control_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(control_frame, text="Pilih Thruster:").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.combo_thruster = ttk.Combobox(control_frame, values=["Thruster Kiri Depan", "Thruster Kanan Belakang", "Thruster Vertikal"], state="readonly", width=25)
        self.combo_thruster.grid(row=0, column=1, columnspan=2, sticky="w", padx=5, pady=8)

        ttk.Label(control_frame, text="Arah Putaran:").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        self.dir_var = tk.StringVar(value="Maju")
        ttk.Radiobutton(control_frame, text="Maju", variable=self.dir_var, value="Maju").grid(row=1, column=1, sticky="w", padx=5, pady=8)
        ttk.Radiobutton(control_frame, text="Mundur", variable=self.dir_var, value="Mundur").grid(row=1, column=2, sticky="w", padx=5, pady=8)

        ttk.Label(control_frame, text="Kecepatan (%):").grid(row=2, column=0, sticky="w", padx=5, pady=8)
        self.speed_slider = tk.Scale(control_frame, from_=0, to=100, orient="horizontal", length=300)
        self.speed_slider.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=8)

        # --- 3. TOMBOL AKSI & KILL SWITCH ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        self.btn_send = tk.Button(btn_frame, text="Kirim Perintah", bg="green", fg="white", font=("Arial", 10, "bold"), command=self.send_command)
        self.btn_send.pack(side="left", expand=True, fill="x", padx=5, ipady=5)

        self.btn_kill = tk.Button(btn_frame, text="KILL SWITCH / EMERGENCY STOP", bg="red", fg="white", font=("Arial", 11, "bold"), command=self.emergency_stop)
        self.btn_kill.pack(side="right", expand=True, fill="x", padx=5, ipady=5)

        # --- 4. AREA LOG AKTIVITAS ---
        log_frame = ttk.LabelFrame(root, text="System Activity Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_area = tk.Text(log_frame, height=12, state="disabled")
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)

        # Variabel pelacak kecepatan sebelumnya (untuk validasi lonjakan 0 ke 100)
        self.prev_speed = 0

    def log_message(self, message, is_error=False):
        self.log_area.config(state="normal")
        tag = "error" if is_error else "normal"
        self.log_area.tag_config("error", foreground="red")
        self.log_area.insert("end", message + "\n", tag)
        self.log_area.see("end")
        self.log_area.config(state="disabled")

    def send_command(self):
        # 1. Validasi Thruster belum dipilih
        thruster = self.combo_thruster.get()
        if not thruster:
            messagebox.showerror("Error Safety", "Peringatan: Belum memilih thruster!")
            return

        # 2. Validasi Input Sensor (Angka / Non-Huruf untuk Suhu, Kedalaman, dan Baterai)
        try:
            temp = float(self.entry_temp.get())
            depth = float(self.entry_depth.get())
            batt = float(self.entry_batt.get())
        except ValueError:
            messagebox.showerror("Format Error", "Nilai Suhu, Kedalaman, dan Baterai harus berupa angka yang valid (tidak boleh huruf)!")
            return

        # 3. Validasi Interlock Sensor Ekstrem (Suhu > 45°C ATAU Baterai < 15%)
        if temp > 45.0 or batt < 15.0:
            msg = f"INTERLOCK AKTIF! Suhu ({temp}°C) atau Baterai ({batt}%) berada di ambang batas bahaya!"
            messagebox.showwarning("Bahaya Komponen", msg)
            self.log_message(f"[BLOCKED] {msg}", is_error=True)
            return

        # 4. Validasi Lonjakan Ekstrem (0% langsung ke 100%)
        current_speed = self.speed_slider.get()
        if self.prev_speed == 0 and current_speed == 100:
            messagebox.showerror("Lonjakan Arus", "Peringatan: Dilarang melompat dari 0% langsung ke 100% untuk mencegah lonjakan arus listrik!")
            return

        # Jika lolos seluruh validasi:
        direction = self.dir_var.get()
        self.prev_speed = current_speed
        success_msg = f"[SUKSES] Perintah dikirim ke {thruster} | Arah: {direction} | Kecepatan: {current_speed}% | Suhu: {temp}°C | Kedalaman: {depth}m | Baterai: {batt}%"
        self.log_message(success_msg)

    def emergency_stop(self):
        self.speed_slider.set(0)
        self.prev_speed = 0
        warning_msg = "[EMERGENCY] KILL SWITCH DITEKAN! Seluruh thruster dihentikan paksa (Speed = 0%)."
        messagebox.showwarning("DARURAT", warning_msg)
        self.log_message(warning_msg, is_error=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = ROVDashboard(root)
    root.mainloop()