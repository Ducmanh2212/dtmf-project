"""
Giao diện người dùng trên Python bằng Tkinter để demo sinh và giải mã DTMF.
Bản nâng cấp giao diện theo phong cách desktop app hiện đại hơn:
- Header rõ ràng
- Card layout
- Nút đẹp hơn
- Có nhập thời gian ghi mic
- Khu vực kết quả lớn, dễ nhìn
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys

# Dẫn path để load module nội bộ
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsp.encoder import generate_dtmf_tone
from dsp.decoder import detect_dtmf_tone
from dsp.constants import SAMPLE_RATE
from desktop_app.audio_io import play_signal, record_signal, save_wav, load_wav


class DTMFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DTMF Encode / Decode - Desktop App")
        self.root.geometry("860x620")
        self.root.minsize(820, 580)
        self.root.configure(bg="#f4f7fb")

        self._build_ui()

    def _build_ui(self):
        # =========================
        # Header
        # =========================
        header = tk.Frame(self.root, bg="#f4f7fb")
        header.pack(fill="x", padx=24, pady=(20, 10))

        lbl_title = tk.Label(
            header,
            text="DTMF Encode / Decode",
            font=("Arial", 22, "bold"),
            bg="#f4f7fb",
            fg="#0f172a"
        )
        lbl_title.pack(anchor="w")

        lbl_subtitle = tk.Label(
            header,
            text="Mô phỏng sinh, phát, thu và giải mã tín hiệu DTMF trên Desktop App",
            font=("Arial", 11),
            bg="#f4f7fb",
            fg="#475569"
        )
        lbl_subtitle.pack(anchor="w", pady=(4, 0))

        # =========================
        # Main container
        # =========================
        container = tk.Frame(self.root, bg="#f4f7fb")
        container.pack(fill="both", expand=True, padx=24, pady=10)

        # =========================
        # Card: Encode
        # =========================
        card_encode = tk.Frame(
            container,
            bg="white",
            highlightbackground="#e2e8f0",
            highlightthickness=1
        )
        card_encode.pack(fill="x", pady=(0, 14))

        encode_inner = tk.Frame(card_encode, bg="white")
        encode_inner.pack(fill="x", padx=18, pady=18)

        tk.Label(
            encode_inner,
            text="Encoder",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#0f172a"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))

        tk.Label(
            encode_inner,
            text="Nhập chuỗi ký tự DTMF để phát và lưu WAV tự động",
            font=("Arial", 10),
            bg="white",
            fg="#64748b"
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 14))

        tk.Label(
            encode_inner,
            text="Chuỗi DTMF",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#1e293b"
        ).grid(row=2, column=0, sticky="w", pady=6)

        self.entry_digits = tk.Entry(
            encode_inner,
            width=34,
            font=("Arial", 13),
            relief="flat",
            bg="#f8fafc",
            fg="#0f172a",
            highlightthickness=1,
            highlightbackground="#cbd5e1",
            highlightcolor="#2563eb",
            insertbackground="#0f172a"
        )
        self.entry_digits.grid(row=2, column=1, sticky="ew", padx=(10, 12), pady=6)
        self.entry_digits.insert(0, "123#90A")

        self.btn_encode = tk.Button(
            encode_inner,
            text="Encode + Lưu WAV + Phát",
            command=self.on_encode_play,
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            font=("Arial", 11, "bold"),
            padx=16,
            pady=10,
            cursor="hand2"
        )
        self.btn_encode.grid(row=2, column=2, pady=6)

        encode_inner.grid_columnconfigure(1, weight=1)

        # =========================
        # Card: Decode
        # =========================
        card_decode = tk.Frame(
            container,
            bg="white",
            highlightbackground="#e2e8f0",
            highlightthickness=1
        )
        card_decode.pack(fill="x", pady=(0, 14))

        decode_inner = tk.Frame(card_decode, bg="white")
        decode_inner.pack(fill="x", padx=18, pady=18)

        tk.Label(
            decode_inner,
            text="Decoder",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#0f172a"
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))

        tk.Label(
            decode_inner,
            text="Giải mã tín hiệu DTMF từ microphone hoặc file WAV",
            font=("Arial", 10),
            bg="white",
            fg="#64748b"
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 14))

        tk.Label(
            decode_inner,
            text="Thời gian ghi mic (giây)",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#1e293b"
        ).grid(row=2, column=0, sticky="w", pady=6)

        self.entry_record_duration = tk.Entry(
            decode_inner,
            width=10,
            font=("Arial", 12),
            relief="flat",
            bg="#f8fafc",
            fg="#0f172a",
            highlightthickness=1,
            highlightbackground="#cbd5e1",
            highlightcolor="#2563eb",
            insertbackground="#0f172a"
        )
        self.entry_record_duration.grid(row=2, column=1, sticky="w", padx=(10, 10), pady=6)
        self.entry_record_duration.insert(0, "5")

        self.btn_record = tk.Button(
            decode_inner,
            text="Thu mic + Decode",
            width=18,
            command=self.on_record_decode,
            bg="#0ea5e9",
            fg="white",
            activebackground="#0284c7",
            activeforeground="white",
            relief="flat",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=10,
            cursor="hand2"
        )
        self.btn_record.grid(row=2, column=2, padx=8, pady=6)

        self.btn_load_wav = tk.Button(
            decode_inner,
            text="Import WAV + Decode",
            width=18,
            command=self.on_load_wav_decode,
            bg="#f59e0b",
            fg="white",
            activebackground="#d97706",
            activeforeground="white",
            relief="flat",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=10,
            cursor="hand2"
        )
        self.btn_load_wav.grid(row=2, column=3, padx=8, pady=6)

        # =========================
        # Card: Result
        # =========================
        card_result = tk.Frame(
            container,
            bg="white",
            highlightbackground="#e2e8f0",
            highlightthickness=1
        )
        card_result.pack(fill="both", expand=True)

        result_inner = tk.Frame(card_result, bg="white")
        result_inner.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            result_inner,
            text="Kết quả xử lý",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#0f172a"
        ).pack(anchor="w")

        tk.Label(
            result_inner,
            text="Thông tin phát, ghi âm, import file và chuỗi DTMF nhận diện được",
            font=("Arial", 10),
            bg="white",
            fg="#64748b"
        ).pack(anchor="w", pady=(4, 12))

        self.text_result = tk.Text(
            result_inner,
            height=14,
            font=("Consolas", 11),
            bg="#0f172a",
            fg="#e2e8f0",
            relief="flat",
            padx=14,
            pady=14,
            wrap="word"
        )
        self.text_result.pack(fill="both", expand=True)

        self.text_result.insert("1.0", "Sẵn sàng.\nHãy nhập chuỗi DTMF hoặc chọn nguồn decode.")
        self.text_result.config(state="disabled")

        footer = tk.Frame(self.root, bg="#f4f7fb")
        footer.pack(fill="x", padx=24, pady=(0, 16))

        self.lbl_status = tk.Label(
            footer,
            text="Trạng thái: Sẵn sàng",
            font=("Arial", 10, "bold"),
            bg="#f4f7fb",
            fg="#334155"
        )
        self.lbl_status.pack(anchor="w")

    def _set_result(self, text):
        self.text_result.config(state="normal")
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert("1.0", text)
        self.text_result.config(state="disabled")

    def _set_status(self, text, color="#334155"):
        self.lbl_status.config(text=f"Trạng thái: {text}", fg=color)
        self.root.update()

    def _safe_filename(self, digits):
        return digits.replace("*", "star").replace("#", "hash")

    def _parse_record_duration(self):
        raw = self.entry_record_duration.get().strip()
        if not raw:
            return 5.0
        try:
            value = float(raw)
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            raise ValueError("Thời gian ghi mic phải là số dương, ví dụ 3 hoặc 5.")

    def on_encode_play(self):
        digits = self.entry_digits.get().strip()
        if not digits:
            messagebox.showwarning(
                "Cảnh báo",
                "Vui lòng nhập chuỗi ký tự DTMF cần phát (0-9, A-D, *, #)."
            )
            return

        try:
            self.btn_encode.config(state="disabled")
            self._set_status("Đang encode và phát tín hiệu...", "#1d4ed8")
            self._set_result("Đang tạo tín hiệu DTMF...")

            # 1. Sinh tín hiệu
            audio_signal = generate_dtmf_tone(digits)

            # 2. Lưu WAV
            safe_filename = self._safe_filename(digits)
            output_wav = f"dtmf_tone_{safe_filename}.wav"
            save_wav(output_wav, audio_signal, SAMPLE_RATE)

            # 3. Phát âm
            play_signal(audio_signal, SAMPLE_RATE)

            self._set_result(
                "ENCODE THÀNH CÔNG\n\n"
                f"Chuỗi đầu vào: {digits}\n"
                f"Sample rate: {SAMPLE_RATE} Hz\n"
                f"File WAV đã lưu: {output_wav}\n\n"
                "Tín hiệu đã được phát qua loa."
            )
            self._set_status("Đã encode, lưu WAV và phát xong", "#15803d")

            messagebox.showinfo(
                "Hoàn tất",
                f"Phát loa hoàn tất.\nĐã lưu tự động file âm thanh: {output_wav}"
            )

        except ValueError as ve:
            self._set_status("Dữ liệu đầu vào không hợp lệ", "#dc2626")
            messagebox.showerror("Ký tự sai", str(ve))
        except Exception as e:
            self._set_status("Lỗi hệ thống", "#dc2626")
            messagebox.showerror("Lỗi hệ thống", f"Không thể phát/ghi sóng: {e}")
        finally:
            self.btn_encode.config(state="normal")

    def on_record_decode(self):
        try:
            record_duration = self._parse_record_duration()

            self.btn_record.config(state="disabled", text="Đang ghi mic...")
            self._set_status(f"Đang thu mic trong {record_duration:.1f} giây...", "#0284c7")
            self._set_result(
                f"Đang ghi âm từ microphone trong {record_duration:.1f} giây...\n"
                "Vui lòng phát tín hiệu DTMF gần microphone."
            )

            # Ghi âm
            audio_signal = record_signal(record_duration, SAMPLE_RATE)

            self._set_status("Đang giải mã tín hiệu từ microphone...", "#7c3aed")
            self._set_result("Đã thu âm xong.\nĐang quét Goertzel để nhận diện DTMF...")

            # Decode
            decoded_digits = detect_dtmf_tone(audio_signal, SAMPLE_RATE)
            self._show_decoded_result(decoded_digits, source=f"Microphone ({record_duration:.1f}s)")

        except Exception as e:
            self._set_status("Lỗi khi thu mic hoặc decode", "#dc2626")
            messagebox.showerror("Lỗi microphone / DSP", f"Lỗi mic hoặc DSP: {e}")
            self._set_result("Không thể ghi mic hoặc giải mã tín hiệu.")
        finally:
            self.btn_record.config(state="normal", text="Thu mic + Decode")

    def on_load_wav_decode(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file tín hiệu DTMF (.wav)",
            filetypes=(("WAV Audio Files", "*.wav"), ("All Files", "*.*"))
        )

        if not file_path:
            return

        try:
            self._set_status("Đang đọc file WAV...", "#d97706")
            self._set_result(f"Đang mở file: {os.path.basename(file_path)}")

            audio_signal, sr = load_wav(file_path)

            self._set_status("Đang giải mã file WAV...", "#7c3aed")
            self._set_result(
                f"Đã đọc file: {os.path.basename(file_path)}\n"
                "Đang quét Goertzel để nhận diện DTMF..."
            )

            decoded_digits = detect_dtmf_tone(audio_signal, sr)
            self._show_decoded_result(decoded_digits, source=f"File WAV: {os.path.basename(file_path)}")

        except Exception as e:
            self._set_status("Lỗi file WAV", "#dc2626")
            messagebox.showerror("Lỗi file", f"Định dạng lỗi hoặc file không tồn tại: {e}")
            self._set_result("Failed to decode file WAV.")

    def _show_decoded_result(self, decoded_digits, source="Nguồn không xác định"):
        if decoded_digits:
            self._set_result(
                "DECODE THÀNH CÔNG\n\n"
                f"Nguồn tín hiệu: {source}\n"
                f"Kết quả nhận diện: {decoded_digits}\n\n"
                "Hệ thống đã phát hiện được tín hiệu DTMF hợp lệ."
            )
            self._set_status("Decode thành công", "#15803d")
        else:
            self._set_result(
                "KHÔNG NHẬN DIỆN ĐƯỢC DTMF\n\n"
                f"Nguồn tín hiệu: {source}\n"
                "Không tìm thấy tín hiệu DTMF hợp lệ hoặc tín hiệu quá nhiễu."
            )
            self._set_status("Không tìm thấy tín hiệu DTMF", "#64748b")


def run():
    root = tk.Tk()
    app = DTMFApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()