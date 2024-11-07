import re
from tkinter import Tk, Label, Button, Text, filedialog, messagebox
from tkinter.ttk import Progressbar
from moviepy.video.io.VideoFileClip import VideoFileClip
import threading
import unicodedata


def parse_timestamps(text):
    pattern = r"(\d{1,2}:\d{2})\s*(.*)"
    matches = re.findall(pattern, text)

    timestamps = []
    for match in matches:
        time = match[0]
        label = match[1].strip() if match[1].strip() else f"Clip {len(timestamps) + 1}"
        minutes, seconds = map(int, time.split(":"))
        timestamps.append((minutes * 60 + seconds, label))
    return timestamps


def sanitize_filename(name):
    # Видаляє діакритичні знаки та залишає лише латинські символи та цифри
    normalized = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^A-Za-z0-9_]', '_', normalized)


def cut_video(video_path, timestamps, output_folder, progress):
    clip = VideoFileClip(video_path)
    total_clips = len(timestamps) - 1
    for i in range(total_clips):
        start_time, label = timestamps[i]
        end_time = timestamps[i + 1][0]
        sanitized_label = sanitize_filename(label)
        subclip = clip.subclip(start_time, end_time)
        subclip.write_videofile(f"{output_folder}/{sanitized_label}.mp4", codec="libx264")
        progress['value'] += 100 / total_clips
    clip.close()


def start_cutting():
    global video_path
    if not video_path:
        messagebox.showerror("Помилка", "Будь ласка, оберіть відеофайл.")
        return

    timestamp_text = timestamp_entry.get("1.0", "end-1c").strip()
    if not timestamp_text:
        messagebox.showerror("Помилка", "Будь ласка, введіть тайм-коди.")
        return

    timestamps = parse_timestamps(timestamp_text)
    if len(timestamps) < 2:
        messagebox.showerror("Помилка", "Необхідно більше двох тайм-кодів для нарізки.")
        return

    output_folder = filedialog.askdirectory(title="Оберіть папку для збереження відео")
    if not output_folder:
        messagebox.showerror("Помилка", "Будь ласка, оберіть папку для збереження відео.")
        return

    progress_bar['value'] = 0
    threading.Thread(target=cut_video, args=(video_path, timestamps, output_folder, progress_bar)).start()


def select_video():
    global video_path
    video_path = filedialog.askopenfilename(title="Оберіть відеофайл", filetypes=[("Відеофайли", "*.mp4;*.avi;*.mov")])
    if video_path:
        video_label.config(text=f"Вибрано відео: {video_path}")


def paste_from_clipboard():
    try:
        clipboard_text = root.clipboard_get()
        timestamp_entry.insert("1.0", clipboard_text)
    except:
        messagebox.showerror("Помилка", "Не вдалося вставити з буфера обміну")


# Інтерфейс Tkinter
root = Tk()
root.title("Нарізка відео")

video_path = None
Label(root, text="Натисніть кнопку для вибору відео").pack(pady=5)
Button(root, text="Оберіть відео", command=select_video).pack(pady=5)
video_label = Label(root, text="Відео не вибрано")
video_label.pack(pady=5)

Label(root, text="Введіть тайм-коди:").pack(pady=10)
timestamp_entry = Text(root, height=10, width=40)
timestamp_entry.pack(pady=10)

Button(root, text="Вставити з буфера", command=paste_from_clipboard).pack(pady=5)
Button(root, text="Запустити", command=start_cutting).pack(pady=10)

progress_bar = Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

root.mainloop()
