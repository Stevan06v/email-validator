import queue
import threading
import tkinter
import customtkinter
import csv
from CTkListbox import *
from tkinter import filedialog as fd
from email_validator import validate_email, caching_resolver, EmailNotValidError
from disposable_email_domains import blocklist


class SingleMailToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, email="", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("500x100")
        self.title(f"{email}-Validation")
        self.maxsize(500, 100)
        self.minsize(500, 100)

        validLabel = customtkinter.CTkLabel(master=self, text_color="red",
                                            font=("System", 14, "bold"))
        validLabel.place(relx=.5, rely=.4, anchor=tkinter.CENTER)

        errorMessageLabel = customtkinter.CTkLabel(master=self, text="",
                                                   font=("System", 12))
        errorMessageLabel.place(relx=.5, rely=.45, anchor=tkinter.CENTER)

        def mail_checker():
            try:
                email_info = validate_email(email)
                validLabel.configure(text="Valid email", text_color="green")

                is_in_blocklist = email_info.domain in blocklist

                if not is_in_blocklist:
                    try:
                        with open("blacklist.txt", "r") as f:
                            blacklist = f.read().splitlines()
                            is_in_blocklist = email_info.domain in blacklist
                    except FileNotFoundError:
                        print("Die Blacklist-Datei wurde nicht gefunden.")

                if is_in_blocklist:
                    validLabel.configure(text="Email found in Blacklist", text_color="red")

            except EmailNotValidError as e:
                validLabel.configure(text="Invalid email", text_color="red")
                errorMessageLabel.configure(text=str(e))

        mail_checker()


class MailsListTopLevelWindow(customtkinter.CTkToplevel):
    def __init__(self, emails, title="", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.toplevel_window = None

        self.geometry("400x300")
        self.title(title)
        self.maxsize(400, 300)
        self.minsize(400, 300)

        def show_value(selected_option):
            if self.toplevel_window and self.toplevel_window.winfo_exists():
                self.toplevel_window.destroy()
            self.toplevel_window = SingleMailToplevelWindow(email=selected_option)

        validLabel = customtkinter.CTkLabel(master=self, text=title,
                                            text_color="red" if title == "Invalid Emails" else "green",
                                            font=("System", 14, "bold"))
        validLabel.pack(padx=20, pady=10)

        listbox = CTkListbox(self, command=show_value)
        listbox.delete("all")
        for index, email in enumerate(emails):
            listbox.insert(index, email)

        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        listbox.place(relx=.5, rely=.4, anchor=tkinter.CENTER, relwidth=.9, relheight=.4)

        def export_data():
            try:
                filename = fd.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
                if filename:
                    with open(filename, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        for email in emails:
                            writer.writerow([email])
                    print("Data exported successfully to", filename)
                else:
                    print("Export canceled.")
            except Exception as e:
                print("Error exporting data:", e)

        # submit-button
        download_list = customtkinter.CTkButton(master=self, text="Download", width=220, height=40,
                                                command=export_data)
        download_list.place(relx=.5, rely=.8, anchor=tkinter.CENTER)


class TabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.toplevel_window = None
        self.another_toplevel_window = None

        self.configure(width=400,
                       height=500)

        # create tabs
        self.add("Single")
        self.add("Multiple")
        self.add("Blacklist")

        self.tab("Single").configure(height=200, width=200)

        # tab "Single":

        # headline
        singleLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="Single-Validator", fg_color="transparent",
                                             font=("System", 20, "bold"))
        singleLabel.place(relx=.5, rely=.05, anchor=tkinter.CENTER)

        def mail_checker():
            try:
                errorMessageLabel.configure(text="")
                resolver = caching_resolver(timeout=10)
                emailInfo = validate_email(emailInput.get(), check_deliverability=True, dns_resolver=resolver)

                normalizedText.configure(text=emailInfo.normalized)
                domainText.configure(text=emailInfo.domain)
                localPartText.configure(text=emailInfo.local_part)

                is_in_blocklist = emailInfo.domain in blocklist

                if not is_in_blocklist:
                    try:
                        with open("blacklist.txt", "r") as f:
                            blacklist = f.read().splitlines()
                            is_in_blocklist = emailInfo.domain in blacklist
                    except FileNotFoundError:
                        print("Die Blacklist-Datei wurde nicht gefunden.")

                if is_in_blocklist is False:
                    validLabel.configure(text="The provided email address is valid!", text_color="green")
                else:
                    validLabel.configure(text="Email-Address found in blacklist!", text_color="red")

            except EmailNotValidError as e:

                normalizedText.configure(text="")
                domainText.configure(text="")
                localPartText.configure(text="")

                validLabel.configure(text="The provided email address is invalid!", text_color="red")
                errorMessageLabel.configure(text=str(e))

        textbox = customtkinter.CTkTextbox(master=self.tab("Single"))
        textbox.insert("0.0", "new text to insert")  # insert at line 0 character 0

        emailInput = customtkinter.CTkEntry(master=self.tab("Single"), width=300, height=40,
                                            placeholder_text="Email for validation")
        emailInput.place(relx=.5, rely=.2, anchor=tkinter.CENTER)

        # Additional labels and fields for parameters in single tab
        normalizedLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="Normalized:", fg_color="transparent",
                                                 font=("System", 12, "bold"))
        normalizedLabel.grid(row=0, column=0, padx=50, pady=(140, 0), sticky="w")

        normalizedText = customtkinter.CTkLabel(master=self.tab("Single"), text="...", font=("System", 12))
        normalizedText.grid(row=0, column=1, padx=5, pady=(140, 0), sticky="w")

        # domain label
        domainLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="Domain:", font=("System", 12, "bold"))
        domainLabel.grid(row=1, column=0, padx=50, pady=0, sticky="w")

        domainText = customtkinter.CTkLabel(master=self.tab("Single"), text="...", font=("System", 12))
        domainText.grid(row=1, column=1, padx=5, pady=0, sticky="w")

        # localPart label
        localPartLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="Local part:", fg_color="transparent",
                                                font=("System", 12, "bold"))
        localPartLabel.grid(row=2, column=0, padx=50, pady=0, sticky="w")

        localPartText = customtkinter.CTkLabel(master=self.tab("Single"), text="...", font=("System", 12))
        localPartText.grid(row=2, column=1, padx=5, pady=0, sticky="w")

        validLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="", text_color="red",
                                            font=("System", 14, "bold"))
        validLabel.place(relx=.5, rely=.65, anchor=tkinter.CENTER)  # Place the button at the bottom

        errorMessageLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="",
                                                   font=("System", 12))
        errorMessageLabel.place(relx=.5, rely=.72, anchor=tkinter.CENTER)  # Place the button at the bottom

        # submit-button
        button = customtkinter.CTkButton(master=self.tab("Single"), text="Validate", width=220, height=40,
                                         command=mail_checker)
        button.place(relx=.5, rely=.9, anchor=tkinter.CENTER)  # Place the button at the bottom

        # tab "Multiple":
        def import_data():
            read_csv_file(csvFilePathInput.get())

        def openFileDialog():
            csvFilePathInput.delete(0, tkinter.END)

            filetypes = [("CSV files", "*.csv")]
            name = fd.askopenfilename(filetypes=filetypes)
            csvFilePathInput.insert(tkinter.END, name)

            print(csvFilePathInput.get())

        def read_csv_file(file_path):
            listbox.delete("all")

            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file)

                thread_count = 4
                emails = list(csv_reader)

                chunked_list = split_into_chunks(emails, thread_count)

                # Create a queue for communication between threads
                queue_for_insert = queue.Queue()

                jobs = []

                for i in range(0, thread_count):
                    thread = threading.Thread(target=insert_operation, args=(chunked_list[i], i + 1, queue_for_insert))
                    jobs.append(thread)

                for j in jobs:
                    j.start()

                for j in jobs:
                    j.join()

                # Retrieve items from the queue and insert them into the UI
                while not queue_for_insert.empty():
                    index, row = queue_for_insert.get()

                    print(index, row)
                    listbox.insert(index, row)

                print(len(listbox.get("all")))

        def insert_operation(emails, curr_list, queue_for_insert):
            for index, row in enumerate(emails):
                if row:
                    queue_for_insert.put((index + (len(emails) * curr_list), row))  # Adjust index

        def split_into_chunks(lst, num_chunks):
            avg_chunk_size = len(lst) / num_chunks
            chunks = []
            last = 0.0

            while last < len(lst):
                chunks.append([item for sublist in lst[int(last):int(last + avg_chunk_size)] for item in sublist])
                last += avg_chunk_size

            return chunks

        def show_value(selected_option):
            if self.toplevel_window and self.toplevel_window.winfo_exists():
                self.toplevel_window.destroy()
            self.toplevel_window = SingleMailToplevelWindow(email=selected_option)

        def validate_all():
            emails = listbox.get("all")
            invalid_emails = []
            valid_emails = []
            blacklist = []

            try:
                with open("blacklist.txt", "r") as f:
                    blacklist = f.read().splitlines()
            except FileNotFoundError:
                print("Die Blacklist-Datei wurde nicht gefunden.")

            print(blacklist)

            for email in emails:
                try:
                    resolver = caching_resolver(timeout=10)
                    email_info = validate_email(email, check_deliverability=True, dns_resolver=resolver)

                    if email_info.domain in blocklist or email_info.domain in blacklist:
                        # info = EmailInfo(email_info.normalized, "blacklisted")
                        invalid_emails.append(email)
                    else:
                        # info = EmailInfo(email_info.normalized, "valid")
                        valid_emails.append(email)

                except EmailNotValidError as e:
                    # info = EmailInfo(email, str(e))
                    invalid_emails.append(email)

            # check if windows exist and destroy if they do
            if self.toplevel_window and self.toplevel_window.winfo_exists():
                self.toplevel_window.destroy()

            if self.another_toplevel_window and self.another_toplevel_window.winfo_exists():
                self.another_toplevel_window.destroy()

            # open windows
            if valid_emails:
                self.toplevel_window = MailsListTopLevelWindow(emails=valid_emails, title="Valid Emails")
            if invalid_emails:
                self.another_toplevel_window = MailsListTopLevelWindow(emails=invalid_emails, title="Invalid Emails")

        # headline
        multipleLabel = customtkinter.CTkLabel(master=self.tab("Multiple"), text="Multiple-Validator",
                                               fg_color="transparent",
                                               font=("System", 20, "bold"))
        multipleLabel.place(relx=.5, rely=.05, anchor=tkinter.CENTER)

        # csvFilePath input field
        csvFilePathInput = customtkinter.CTkEntry(master=self.tab("Multiple"), height=30,
                                                  placeholder_text="CSV-Filepath")
        csvFilePathInput.grid(row=0, column=0, padx=(50, 10), pady=(50, 10), sticky="ew")

        # open filedialog button
        openFileDialog = customtkinter.CTkButton(master=self.tab("Multiple"), text="Open", command=openFileDialog,
                                                 font=("System", 12))
        openFileDialog.grid(row=0, column=1, padx=5, pady=(50, 10))

        listbox = CTkListbox(master=self.tab("Multiple"), command=show_value, height=180, width=50)
        listbox.grid(row=2, column=0, columnspan=2, padx=(50, 10), pady=20, sticky="nsew")

        # submit-button
        validateAllButton = customtkinter.CTkButton(master=self.tab("Multiple"), text="Validate",
                                                    command=validate_all)
        validateAllButton.grid(row=3, column=0, columnspan=1, padx=(50, 10), pady=5, sticky="nsew")

        # submit-button
        buttonMultiple = customtkinter.CTkButton(master=self.tab("Multiple"), text="Import", width=220, height=40,
                                                 command=import_data)
        buttonMultiple.place(relx=.5, rely=.9, anchor=tkinter.CENTER)  # Place the button at the bottom

        # tab "Blacklist":

        def load_blacklist():
            try:
                with open("blacklist.txt", "r") as f:
                    blacklist_content = f.read()
                    blacklistTextbox.delete("1.0", "end")  # Clear existing content
                    blacklistTextbox.insert("1.0", blacklist_content)  # Insert content from file
            except FileNotFoundError:
                print("Die Blacklist-Datei wurde nicht gefunden.")

        def save_blacklist():
            blacklist_content = blacklistTextbox.get("1.0", "end-1c")  # Get all content except the trailing newline
            with open("blacklist.txt", "w") as f:
                f.write(blacklist_content)

        blacklistTextbox = customtkinter.CTkTextbox(master=self.tab("Blacklist"))
        blacklistTextbox = customtkinter.CTkTextbox(master=self.tab("Blacklist"), width=250, height=300)
        blacklistTextbox.place(relx=.5, rely=.4, anchor=tkinter.CENTER)

        loadButton = customtkinter.CTkButton(master=self.tab("Blacklist"), text="Load Blacklist",
                                             command=load_blacklist)
        loadButton.place(relx=.3, rely=.9, anchor=tkinter.CENTER)

        saveButton = customtkinter.CTkButton(master=self.tab("Blacklist"), text="Save Blacklist",
                                             command=save_blacklist)
        saveButton.place(relx=.7, rely=.9, anchor=tkinter.CENTER)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Email-Validator")
        self.geometry("500x600")

        self.maxsize(500, 600)
        self.minsize(500, 600)

        self.tab_view = TabView(master=self)
        self.tab_view.place(relx=.5, rely=.5, anchor=tkinter.CENTER)


app = App()
app.mainloop()
