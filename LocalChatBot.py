from ollama import generate, ps
from tkinter import *
from tkinter import messagebox 
import tkinter.ttk as ttk
import threading
import time
import json
import os

#class berisi constructor dan method (implementasi Modul 5)
class LocalChatBot:
    #=============================== fungsi utama inisialisasi GUI (implementasi Modul 4 & 8 (fungsi inisialisasi & GUI)) ===============================#
    def __init__(self, root):
        # Inisialisasi Jendela Utama
        self.root = root
        self.root.title("Local AI Chat Bot")
        self.root.resizable(False, False)
        self.root.iconbitmap("Data/UNDIPOfficial.ico")

        # ======== COLORS ========
        BG_MAIN = "#121212"
        BG_PANEL = "#1f1f1f"
        BG_TEXTUSER = "#2d2d2d"
        BG_TEXTBOT = "#1e88e5"
        FG_TEXT = "#ffffff"
        ACCENT = "#9C9C97"

        self.root.configure(bg=BG_MAIN)

        # ====== LEFT SIDEBAR PANEL ======
        sidebar = Frame(root, bg=BG_PANEL, width=200, height=600)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        Label(
            sidebar, text="Local AI ChatBot",
            font=("Segoe UI", 16, "bold"), fg="#ffffff", bg=BG_PANEL
        ).pack(pady=15)

        Label(sidebar, text="Choose Model", font=("Segoe UI", 11), fg="#aaaaaa", bg=BG_PANEL).pack(pady=3)

        self.Model_Options = ["granite3.3", "gemma3:1b", "llama3.2:1b", "deepseek-r1", "llama2-uncensored", "sahabatai-9b"]
        self.combo_Model = ttk.Combobox(sidebar, justify='center', values=self.Model_Options, font=('Segoe UI', 11), state='readonly')
        self.combo_Model.current(0)
        self.combo_Model.pack(padx=10, pady=5)

        # Buttons in sidebar
        def style_button(btn, bg_normal, bg_hover):
            btn.configure(bg=bg_normal, fg="white", borderwidth=0, relief="flat", padx=10, pady=6, font=("Segoe UI", 11))

            def on_enter(e): btn["bg"] = bg_hover
            def on_leave(e): btn["bg"] = bg_normal
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        self.clear_button = Button(sidebar, text="Clear History", command=self.clear_history)
        style_button(self.clear_button, "#d32f2f", "#b71c1c")
        self.clear_button.pack(pady=10, fill="x", padx=15)

        self.sys_button = Button(sidebar, text="System Usage", command=self.show_system_usage)
        style_button(self.sys_button, "#1976d2", "#0d47a1")
        self.sys_button.pack(pady=10, fill="x", padx=15)

        # ====== MAIN CHAT AREA =======
        main_panel = Frame(root, bg=BG_MAIN)
        main_panel.pack(side="right", fill="both", expand=True)

        # Custom Scrollbar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar", background="#444", troughcolor=BG_MAIN, arrowcolor="white", bordercolor=BG_MAIN)

        text_frame = Frame(main_panel, bg=BG_MAIN)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.text_area = Text(
            text_frame,
            wrap='word',
            font=('Segoe UI', 12),
            background=BG_PANEL,
            foreground=FG_TEXT,
            relief="flat",
            insertbackground="white"
        )
        self.text_area.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_frame, command=self.text_area.yview, style="Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")
        self.text_area['yscrollcommand'] = scrollbar.set

        # Text bubble colors
        self.text_area.tag_configure('user', background="#2e2e2e", foreground="#ffffff", spacing3=6)
        self.text_area.tag_configure('else', background="#263238", foreground="#ffffff", spacing3=6)

        # ====== INPUT BAR ======
        bottom = Frame(main_panel, bg=BG_MAIN)
        bottom.pack(fill="x", padx=10, pady=5)

        self.loading_label = Label(bottom, text="", font=("Segoe UI", 11), fg="#999", bg=BG_MAIN)
        self.loading_label.pack()

        self.entry = Entry(bottom, font=('Segoe UI', 12), bg="#2b2b2b", fg="white", relief="flat", insertbackground="white")
        self.entry.pack(side='left', fill='x', expand=True, padx=10, pady=10, ipady=6)

        self.send_button = Button(bottom, text="Send", command=self.start_response_thread)
        style_button(self.send_button, ACCENT, "#9C9C97")
        self.send_button.pack(side='right', padx=10, pady=10)

        # — internal variables —
        self.loaded_from_file = False
        self.chat_context = []
        self.loading = False
        self.Parameter = 'None'
        self.Nama_Model = 'None'
        self.last_model = None
        self.sys_window = None

        self.load_chat_history()
        
 


    #================================ Fungsi untuk Memulai Thread Respon =================================#
    def start_response_thread(self):
        t = threading.Thread(target=self.get_response)
        t.start()

    #================================ Fungsi untuk Animasi Loading =================================#
    def animate_loading(self):
        dots = ["", ".", "..", "..."]
        i = 0

        # Loop animasi selama kondisi loading = True
        while self.loading:
            self.loading_label.config(text="Loading" + dots[i % 4] + '\n fun fact: Running AI secara lokal itu berat banget', justify='center')
            i += 1
            time.sleep(0.4)


        #Menghapus teks loading setelah selesai
        self.loading_label.config(text="")

    #==================================== Fungsi untuk Mendapatkan Respon dari Model ====================================#
    def get_response(self):
        user_input = self.entry.get()

        #warning jika input user kosong
        if user_input == "":
            messagebox.showwarning("Peringatan", "Pesan harus di isi!")

        # Menentukan Nama Model, Jumlah Parameter dan Context Length berdasarkan pilihan model menggunakan getter (Implementasi Modul 2 & 6 (Kondisional if-elif & Getter))
        if "gemma3:1b" in self.combo_Model.get():
            self.Parameter = '1 Bilion / Miliar'
            self.Nama_Model = "Gemma 3"
            ctx_length = 65536
        elif "granite3.3" in self.combo_Model.get():
            self.Parameter = '8 Bilion / Miliar'
            self.Nama_Model = "Granite 3.3"
            ctx_length = 16384
        elif "llama3.2:1b" in self.combo_Model.get():
            self.Parameter = '1 Bilion / Miliar'
            self.Nama_Model = "Llama 3.2"
            ctx_length = 65536
        elif "deepseek-r1" in self.combo_Model.get():
            self.Parameter = '7 Bilion / Miliar'
            self.Nama_Model = "DeepSeek R1"
            ctx_length = 32768
        elif "llama2-uncensored" in self.combo_Model.get():
            self.Parameter = '7 Bilion / Miliar'
            self.Nama_Model = "Llama 2 Uncensored"
            ctx_length = 32768
        elif "sahabatai-9b" in self.combo_Model.get():
            self.Parameter = '9 Bilion / Miliar'
            self.Nama_Model = "Gemma2BySahabat-AI"
            ctx_length = 16384

        # Menampilkan Jenis Model dan juga Input User di Area Text
        if self.last_model != self.combo_Model.get():
            self.text_area.insert(END, "Kamu Sedang Menggunakan: " + self.Nama_Model + " dengan " + self.Parameter + " Parameter \n", 'else')
            self.text_area.insert(END, "\n")
            self.last_model = self.combo_Model.get()
            if not self.loaded_from_file:
                self.chat_context = []
            self.loaded_from_file = False 

        self.text_area.insert(END, "You: \n" + user_input + '\n', 'user')
        self.text_area.insert(END, "\n")
        self.entry.delete(0, END)

        # Mengganti status loading menjadi True dan memulai animasi loading
        self.loading = True
        threading.Thread(target=self.animate_loading).start()

        # Men-Generate Respon dari Model (implementasi Modul 3 (perulangan for))
        self.text_area.insert(END,'Bot : \n', 'else')
        for chunk in generate(
            model=self.combo_Model.get(),
            prompt=user_input,
            stream=True,
            context=self.chat_context,       # ← send previous context
            options={'num_ctx': ctx_length, 'context':self.chat_context}  # context length
        ):
        
             # update context setelah menerima chunk baru
            if "context" in chunk:
                self.chat_context = chunk["context"]

            # Menampilkan Respon secara Bertahap di Area Text
            part = chunk["response"]
            self.text_area.insert(END, part, 'else')
            print(part, end='', flush=True)
            self.text_area.see(END)

        # Mengganti status loading menjadi False setelah respon selesai
        self.loading = False
        self.text_area.insert(END, "\n", 'else')
        self.text_area.insert(END, "\n")
        self.text_area.see(END)

    #===============================  Fungsi untuk Menampilkan Penggunaan Sistem ===============================#
    def show_system_usage(self):
        stats = ps()

        # membuat jendela baru jika belum ada dan limit satu jendela)
        if self.sys_window is not None and self.sys_window.winfo_exists():
            self.sys_window.lift()
            return


        # Text area dalam jendela
        self.sys_window = Toplevel(self.root)
        self.sys_window.title("System Usage")
        info = Text(self.sys_window, wrap='word', font=('Arial', 11))
        info.pack(expand=True, fill='both')
        info.delete(1.0, END)

        # Menampilkan informasi penggunaan sistem
        for model in stats['models']:
            info.insert(END, "=== System Usage ===\n")
            info.insert(END, f"             Model: {self.Nama_Model}\n")
            info.insert(END, f"     Parameter: {self.Parameter}\n")
            info.insert(END, f"            VRAM: {model.get('Vram', model.size_vram)/1024/1024} MB\n")
            info.insert(END, f"              Size: {model.get('size', model.size)/1024/1024} MB\n\n")
            info.insert(END, f"           Details: {model.get('details', model.details)}\n")
            info.insert(END, f"Context Length: {model.get('context', model.context_length)}\n")
            info.insert(END, "\n")
            info.insert(END, "====================\n\n")
        return
    
    #================================  Fungsi untuk Menyimpan Riwayat Chat =================================#
    def save_chat_history(self):
        data = {
            "chat_context": self.chat_context,
            "text_area": self.text_area.get("1.0", END),
            "last_model": self.last_model,
            "selected_model": self.combo_Model.get()
        }

        os.makedirs("Data", exist_ok=True)
        with open("Data/chat_history.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    #================================  Fungsi untuk Memuat Riwayat Chat ==================================#
    def load_chat_history(self):
        try:
            with open("Data/chat_history.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            self.chat_context = data.get("chat_context", [])
            self.last_model = data.get("last_model", None)

            # Restore text into chat window
            self.text_area.delete("1.0", END)
            self.text_area.insert(END, data.get("text_area", ""))

            saved_model = data.get("selected_model", None)
            if saved_model in self.Model_Options:
                self.combo_Model.set(saved_model)
            
            self.loaded_from_file = True

    # menangani jika file tidak ditemukan    
        except FileNotFoundError:
            pass

    #===============================  Fungsi untuk Menghapus Riwayat Chat =================================#    
    def clear_history(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear all chat history?")
        if not confirm:
            return

        # Menghapus isi area text dan mereset konteks chat
        self.text_area.delete("1.0", END)
        self.chat_context = []
        self.combo_Model.current(0)

        # Menghapus file riwayat chat jika ada
        try:
            os.remove("Data/chat_history.json")
        except FileNotFoundError:
            pass
        messagebox.showinfo("Success", "Chat history cleared!")


    #=============================== Fungsi untuk Menangani Penutupan Aplikasi ================================#
    def on_close(self):
        self.save_chat_history()
        self.root.destroy()

        
# Menjalankan Aplikasi
if __name__ == "__main__":
    root = Tk()
    app = LocalChatBot(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
    


