import threading  #модуль для створення окремих потоків(щоб програма могла одночасно виконувати кілька завдань, наприклад, приймати повідомлення і працювати з інтерфейсом)
from socket import *  #імпортуємо все з бібліотеки socket для роботи з мережею (створюємо клієнт-сервера)
from customtkinter import *  #імпортуємо розширену бібліотеку tkinter для створення сучасного графічного інтерфейсу

#створюємо головне вікно програми, успадковуючи його від CTk(основний клас з customtkinter)
class MainWindow(CTk):
   def __init__(self):
       super().__init__()  #викликаємо ініціалізатор базового класу CTk
       self.geometry('400x300')  #встановлюємо розмір головного вікна(ширина 400, висота 300)
       self.label = None  #заздалегідь створюємо змінну для ярлика меню(буде створюватись пізніше)
       #створюємо бічну панель-меню(спочатку та яка вузька)
       self.menu_frame = CTkFrame(self, width=30, height=300)
       self.menu_frame.pack_propagate(False)  #забороняємо автоматичну зміну розміру фрейму під вміст
       self.menu_frame.place(x=0, y=0)  #розташовуємо панель зліва
       self.is_show_menu = False  #змінна для перевірки, чи меню відкрите
       self.speed_animate_menu = -5  #швидкість анімації(негативна, бо меню ховається)

       #кнопка для відкриття/закриття меню
       self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
       self.btn.place(x=0, y=0)  #розташовуємо кнопку у верхньому лівому куті

       #поле для відображення історії чату
       self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disable')
       self.chat_field.place(x=0, y=0)

       #поле для введення повідомлення користувачем
       self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
       self.message_entry.place(x=0, y=0)

       #кнопка "надіслати"
       self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
       self.send_button.place(x=0, y=0)

       #підключуємося до серверу(через сокет)
       self.username = 'Artem'  #ім я користувача(поки задано вручну)

       try:
           #створюємо клієнтський сокет
           self.sock = socket(AF_INET, SOCK_STREAM)
           self.sock.connect(('localhost', 8080))  #підключаємось до сервера(порт 8080)

           #надсилаємо привітальне повідомлення на сервер
           hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
           self.sock.send(hello.encode('utf-8'))

           #запускаємо окремий потік для прийому повідомлень(щоб інтерфейс не зависав)
           threading.Thread(target=self.recv_message, daemon=True).start()

       except Exception as e:
           #якщо не вдалося підключитись, виводимо помилку у вікні чату
           self.add_message(f"Не вдалося підключитися до сервера: {e}")
           self.adaptive_ui()  #адаптація інтерфейсу(запускаємо функцію, яка постійно підлаштовує розміри елементів при зміні вікна)

   def toggle_show_menu(self):  #закриття та відкриття меню
       if self.is_show_menu:
           #якщо меню відкрите, то закриваємо
           self.is_show_menu = False
           self.speed_animate_menu *= -1  #міняємо напрямок анімації
           self.btn.configure(text='▶️')  #міняємо значок на кнопку
           self.show_menu()
       else:
           #якщо меню закрите, то відкриваємо
           self.is_show_menu = True
           self.speed_animate_menu *= -1
           self.btn.configure(text='◀️')
           self.show_menu()

           #додаємо всередині меню елементи(поле і напис)
           self.label = CTkLabel(self.menu_frame, text='Імʼя')
           self.label.pack(pady=30)
           self.entry = CTkEntry(self.menu_frame)
           self.entry.pack()

   def show_menu(self):    #анімація цього меню
       #змінюємо ширину меню поступово(анімаційно)
       self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)

       #якщо меню ще не досягло ширини 200 і воно відкривається, то повторюємо анімацію
       if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
           self.after(10, self.show_menu)

       #якщо меню закривається і його ширина ще більша за 40, то продовжуємо
       elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
           self.after(10, self.show_menu)

           #коли меню згортається, то видаляємо з нього віджети
           if self.label and self.entry:
               self.label.destroy()
               self.entry.destroy()

   def adaptive_ui(self):   #адаптація
       #підлаштовуємо висоту меню під висоту вікна
       self.menu_frame.configure(height=self.winfo_height())

       #розташовуємо поле чату праворуч від меню
       self.chat_field.place(x=self.menu_frame.winfo_width())

       #змінюємо розмір поля чату(висота = вікно: висота поля вводу)
       self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(),
                                 height=self.winfo_height() - 40)

       #кнопка "надіслати": внизу праворуч
       self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)

       #поле для введення тексту: зліва від кнопки "надіслати"
       self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
       self.message_entry.configure(
           width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())

       #кожні 50 мс оновлюємо розміщення(щоб все підлаштовувалось при зміні розміру вікна)
       self.after(50, self.adaptive_ui)

   def add_message(self, text):  #додавання повідомлень у чат
       self.chat_field.configure(state='normal')  #даємо змогу редагувати текст
       self.chat_field.insert(END, 'Я: ' + text + '\n')  #додаємо нове повідомлення
       self.chat_field.configure(state='disable')  #знову блокуємо для користувача(щоб не змінював вручну)

   def send_message(self):    #відправка повідомлень
       message = self.message_entry.get()  #отримуємо введений текст
       if message:
           self.add_message(f"{self.username}: {message}")  #відображаємо у себе
           data = f"TEXT@{self.username}@{message}\n"  #форматуємо повідомлення для сервера
           try:
               self.sock.sendall(data.encode())  #відправляємо на сервер
           except:
               pass  #якщо сервер недоступний, то просто ігноруємо
       self.message_entry.delete(0, END)  #та очищаємо поле вводу

   def recv_message(self):   #отримка повідомлень від сервера
       buffer = ""  #тимчасовий буфер для збирання отриманих даних
       while True:
           try:
               chunk = self.sock.recv(4096)  #отримуємо частину даних з сервера
               if not chunk:
                   break  #якщо нічого не прийшло: з'єднання закрито
               buffer += chunk.decode()

               #повідомлення розділені символом \n: обробляємо їх по черзі
               while "\n" in buffer:
                   line, buffer = buffer.split("\n", 1)
                   self.handle_line(line.strip())  #передаємо рядок для обробки
           except:
               break
       self.sock.close()  #закриваємо сокет після виходу з циклу

   def handle_line(self, line):  #обробка отриманих повідомлень(рядків)
       if not line:
           return  #ігноруємо порожні рядки

       parts = line.split("@", 3)  #розділяємо повідомлення по "@"
       msg_type = parts[0]  #перший елемент: тип повідомлення(TEXT, IMAGE, тощо)

       if msg_type == "TEXT":
           if len(parts) >= 3:
               author = parts[1]
               message = parts[2]
               self.add_message(f"{author}: {message}")  #додаємо текст у чат
       elif msg_type == "IMAGE":
           if len(parts) >= 4:
               author = parts[1]
               filename = parts[2]
               self.add_message(f"{author} надіслав(ла) зображення: {filename}")
       else:
           self.add_message(line)  #якщо тип невідомий, то просто показуємо

#запускаємо програму
win = MainWindow()  #створюємо об єкт головного вікна
win.mainloop()  #та запускаємо головний цикл програми(інтерфейс працює доти, поки вікно не закрите)













