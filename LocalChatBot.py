from ollama import generate, ps
from tkinter import *
from tkinter import messagebox 
import tkinter.ttk as ttk
import threading
import time

#class berisi constructor dan method (implementasi Modul 5)
class LocalChatBot:
    #fungsi inisialisasi GUI (implementasi Modul 4 & 8)
    def __init__(self, root):
        # Inisialisasi Jendela Utama
        self.root = root
        self.root.title("Local AI Chat Bot")
        self.root.resizable(False, False)
        self.root.iconbitmap('Data/UNDIPOfficial.ico')

        # Area Text
        self.text_area = Text(root, wrap='word', font=('Arial', 12))
        self.text_area.pack(expand=True, fill='y', padx=20, pady=10)  

        # Pemilihan Model
        self.model_frame = Frame(root)
        self.model_frame.pack()

        Label(self.model_frame, text="Pilih Model AI : ", font=('Arial', 12)).pack(side= 'left')
        self.Model_Options = ["granite3.3", "gemma3:1b", "llama3.2:1b", "deepseek-r1", "llama2-uncensored", "sahabatai-9b"]
        self.combo_Model = ttk.Combobox(self.model_frame, justify='center', values=self.Model_Options, font=('Arial', 12), state='readonly')
        self.combo_Model.current(0)
        self.combo_Model.pack()

        # Frame untuk Entry, Loading dan Button
        self.frame_talk = Frame(root)
        self.frame_talk.pack(fill='x', padx=20, pady=10)

        # Label untuk Loading
        self.loading_label = Label(self.frame_talk, text="", font=('Arial', 12))
        self.loading_label.pack()

        # Entry untuk Input User
        self.entry = Entry(self.frame_talk, font=('Arial', 12))
        self.entry.pack(side='left', fill='x', expand=True, padx=10, pady=10)

        # Button untuk Mengirim Pesan
        self.send_button = Button(self.frame_talk, text="Send", command=self.start_response_thread, font=('Arial', 12))
        self.send_button.pack(side='right',fill='y', padx=10, pady=10)

        # Button untuk Menampilkan Penggunaan Sistem
        self.sys_button = Button(root, text="System Usage", command=self.show_system_usage, font=('Arial', 12))
        self.sys_button.pack(pady=5)


        # Kondisi default (implementasi Modul 1)
        self.loading = False
        self.Nama_Model = 'None'
        self.last_model = None
        self.sys_window = None
        self.text_area.tag_configure('user', background='#D9D7D0')
        self.text_area.tag_configure('else', background='#F0EFEC')
 


    # Threading untuk Mendapatkan Respon

    def start_response_thread(self):
        t = threading.Thread(target=self.get_response)
        t.start()

    # Fungsi dari Animasi Loading
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

    # Fungsi untuk Mendapatkan Respon dari Model
    def get_response(self):
        user_input = self.entry.get()

        #warning jika input user kosong
        if user_input == "":
            messagebox.showwarning("Peringatan", "Pesan harus di isi!")

        # Menentukan Nama Model dan Parameter berdasarkan pilihan model menggunakan getter (Implementasi Modul 2 & 6)
        if "gemma3:1b" in self.combo_Model.get():
            Parameter = '1'
            self.Nama_Model = "Gemma 3"
        elif "granite3.3" in self.combo_Model.get():
            Parameter = '8'
            self.Nama_Model = "Granite 3.3"
        elif "llama3.2:1b" in self.combo_Model.get():
            Parameter = '1'
            self.Nama_Model = "Llama 3.2"
        elif "deepseek-r1" in self.combo_Model.get():
            Parameter = '7'
            self.Nama_Model = "DeepSeek R1"
        elif "llama2-uncensored" in self.combo_Model.get():
            Parameter = '7'
            self.Nama_Model = "Llama 2 Uncensored"
        elif "sahabatai-9b" in self.combo_Model.get():
            Parameter = '9'
            self.Nama_Model = "Sahabat-AI"

        # Menampilkan Jenis Model dan juga Input User di Area Text
        if self.last_model != self.combo_Model.get():
            self.text_area.insert(END, "Kamu Sedang Menggunakan: " + self.Nama_Model + " dengan " + Parameter + " Miliar Parameter \n", 'else')
            self.text_area.insert(END, "\n")
            self.last_model = self.combo_Model.get()
        self.text_area.insert(END, "You: \n" + user_input + '\n', 'user')
        self.text_area.insert(END, "\n")
        self.entry.delete(0, END)

        # Mengganti status loading menjadi True dan memulai animasi loading
        self.loading = True
        threading.Thread(target=self.animate_loading).start()

        # Men-Generate Respon dari Model (implementasi Modul 3)
        self.text_area.insert(END,'Bot : \n', 'else')
        for chunk in generate(self.combo_Model.get(), user_input, stream=True):
            self.loading = False
            self.text_area.insert(END,chunk['response'], 'else')
            self.text_area.see(END)

        self.text_area.insert(END, "\n", 'else')
        self.text_area.insert(END, "\n")
        self.text_area.see(END)

    # Fungsi untuk Menampilkan Penggunaan Sistem
    def show_system_usage(self):
        stats = ps()

        # Create a new window (like a new tab)
        if self.sys_window is not None and self.sys_window.winfo_exists():
            self.sys_window.lift()
            return


        # Text area inside new tab
        self.sys_window = Toplevel(self.root)
        self.sys_window.title("System Usage")
        info = Text(self.sys_window, wrap='word', font=('Arial', 11))
        info.pack(expand=True, fill='both')
        info.delete(1.0, END)


        for model in stats['models']:
            info.insert(END, "=== System Usage ===\n")
            info.insert(END, f"  Model: {self.Nama_Model}\n")
            info.insert(END, f"  VRAM: {model.get('Vram', model.size_vram)/1024/1024} MB\n")
            info.insert(END, f"    Size: {model.get('size', model.size)/1024/1024} MB\n\n")
            info.insert(END, f"Details: {model.get('details', model.details)}\n")
            info.insert(END, "\n")
            info.insert(END, "====================\n\n")
        return
            


        
# Menjalankan Aplikasi
if __name__ == "__main__":
    root = Tk()
    app = LocalChatBot(root)
    root.mainloop()


