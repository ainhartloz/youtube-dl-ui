import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

def download_video():
    """Download the video in the selected resolution."""
    url = url_entry.get()
    folder = folder_path.get()
    cookies_file = cookies_entry.get()  # Get cookies file path
    if not url or not folder:
        messagebox.showerror("Error", "URL and Folder are required!")
        return

    custom_selection = resolution_dropdown.get()

    if custom_selection == "1080p":
        format_option = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    elif custom_selection == "720p":
        format_option = "bestvideo[height<=720]+bestaudio/best[height<=720]"
    elif custom_selection == "480p":
        format_option = "bestvideo[height<=480]+bestaudio/best[height<=480]"
    else:  # Default to the best available format
        format_option = "bestvideo+bestaudio/best"

    command = [
        "python", "../youtube_dl/__main__.py",
        "-f", format_option,
        "--merge-output-format", "mp4",  # Ensure that audio and video are merged
        "-o", f"{folder}/%(title)s.%(ext)s",
        url
    ]

    if cookies_file:
        command.extend(["--cookies", cookies_file])

    thread = threading.Thread(target=run_download, args=(command,))
    thread.start()

def run_download(command):
    """Runs youtube-dl command and updates the progress bar."""
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line.strip())

            if "%" in line:
                try:
                    percentage_str = line.split("%")[0].split()[-1]
                    percentage = int(percentage_str)
                    progress_bar['value'] = percentage
                    app.update_idletasks()
                except (ValueError, IndexError):
                    continue

        process.communicate()

        if process.returncode == 0:
            messagebox.showinfo("Success", "Download completed!")
        else:
            messagebox.showerror(
                "Error",
                f"Download failed! Check console for details.\nCommand: {' '.join(command)}"
            )

        progress_bar['value'] = 0

    except Exception as e:
        messagebox.showerror("Error", f"Download failed unexpectedly: {str(e)}")
        progress_bar['value'] = 0

def browse_folder():
    """Open a folder selection dialog."""
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)

# UI Section
app = tk.Tk()
app.title("YouTube Downloader")

tk.Label(app, text="Video URL:").grid(row=0, column=0, padx=10, pady=5)
url_entry = tk.Entry(app, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(app, text="Cookies File (Optional):").grid(row=1, column=0, padx=10, pady=5)
cookies_entry = tk.Entry(app, width=50)
cookies_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(app, text="Select Resolution:").grid(row=2, column=0, padx=10, pady=5)
resolution_dropdown = ttk.Combobox(app, width=47)
resolution_dropdown['values'] = ["1080p", "720p", "480p", "Best Available"]
resolution_dropdown.current(0)  # Default to 1080p
resolution_dropdown.grid(row=2, column=1, padx=10, pady=5)

tk.Label(app, text="Save to Folder:").grid(row=3, column=0, padx=10, pady=5)
folder_path = tk.StringVar()
folder_entry = tk.Entry(app, textvariable=folder_path, width=50)
folder_entry.grid(row=3, column=1, padx=10, pady=5)
tk.Button(app, text="Browse", command=browse_folder).grid(row=3, column=2, padx=10, pady=5)

tk.Button(app, text="Download", command=download_video).grid(row=4, column=1, pady=20)

progress_bar = ttk.Progressbar(app, length=400, mode='determinate')
progress_bar.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

app.mainloop()