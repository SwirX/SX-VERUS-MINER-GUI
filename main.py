import multiprocessing
import re
import subprocess
import threading
import time
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
import json
import psutil
import regex.regex
import checkwallet

with open("./settings.json", "r") as settingsfile:
    settings = json.load(settingsfile)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title = "SX-VerusMiner"
        self.geometry("500x600")
        # values
        self.running = tk.BooleanVar()
        self.status_value = tk.StringVar()
        self.miningstatus = tk.BooleanVar()
        self.max_cores = tk.IntVar()
        self.dedicated_cores = tk.IntVar()
        self.wallet_address = tk.StringVar()
        self.pool_address = tk.StringVar()
        self.worker_name = tk.StringVar()
        self.mining_cmd = tk.StringVar()
        self.mining_cmd_template = tk.StringVar()
        self.output_visible = tk.BooleanVar()
        self.mining_thread = None
        self.mining_process = None
        self.blocks_mined_value = tk.StringVar()
        self.elapsed_time_value = tk.StringVar()
        self.mining_start_timestamp = tk.IntVar()
        self.difficulty_value = tk.StringVar()
        self.mining_speed_value = tk.StringVar()
        self.current_working_thread = tk.StringVar()
        self.temperature = tk.StringVar()
        self.output_queue = multiprocessing.Queue()

        self.homepage_button_text = tk.StringVar()

        # set values
        self.running.set(True)
        self.output_visible.set(False)
        self.blocks_mined_value.set("blocks mined")
        self.elapsed_time_value.set("elapsed time")
        self.difficulty_value.set("difficulty")
        self.mining_speed_value.set("mining speed")
        self.current_working_thread.set("current working core")
        self.temperature.set("Couldn't retreive the temperature")
        self.homepage_button_text.set("Start Mining")

        # get max cores count
        self.max_cores.set(psutil.cpu_count(logical=False))

        #   styles
        # ComboBoxes
        custom_style = ttk.Style()
        custom_style.configure("Custom.TCombobox", selectbackground="#ffffff", selectforeground="#000000")

        # Homepage
        self.homepage_frame = ttk.Frame(self)
        self.header_label = ttk.Label(self.homepage_frame, text="SX-VerusMiner", font=("Berlin Sans FB", 24),
                                      background="#457B9D", foreground="white", anchor="center")
        self.mining_status_label = ttk.Label(self.homepage_frame, textvariable=self.status_value, anchor="center")
        self.start_mining_button = ttk.Button(self.homepage_frame, textvariable=self.homepage_button_text,
                                              command=self.start_mining)

        # Mining page
        self.miningpage_frame = ttk.Frame(self)
        self.stop_mining_button = ttk.Button(self.miningpage_frame, text="Stop Mining", command=self.stop_mining)
        self.blocks_label = ttk.Label(self.miningpage_frame, textvariable=self.blocks_mined_value)
        self.temperature_label = ttk.Label(self.miningpage_frame, textvariable=self.temperature)
        self.elapsed_time_label = ttk.Label(self.miningpage_frame, textvariable=self.elapsed_time_value)
        self.difficulty_label = ttk.Label(self.miningpage_frame, textvariable=self.difficulty_value)
        self.current_working_thread_label = ttk.Label(self.miningpage_frame, textvariable=self.current_working_thread)
        self.toggle_output_button = ttk.Button(self.miningpage_frame, text="Toggle Mining output",
                                               command=self.toggle_output)
        self.output_text = tk.Text(self.miningpage_frame, wrap="none")

        # Settings Page
        self.settingspage_frame = ttk.Frame(self)
        self.settings_header_label = ttk.Label(self.settingspage_frame, text="Settings", font=("Berlin Sans FB", 24),
                                               background="#457B9D", foreground="white", anchor="center")
        # Create a slider for choosing the number of cores

        self.cores_label = ttk.Label(self.settingspage_frame,
                                     text="Select the number of cores:", anchor="center")
        self.cores_label_info = ttk.Label(self.settingspage_frame,
                                          text=f"(maximum cores on this computer are {self.max_cores.get()})",
                                          anchor="center")
        self.cores_scale = ttk.Scale(self.settingspage_frame, from_=1, to=self.max_cores.get(), orient="horizontal",
                                     length=200,
                                     variable=self.dedicated_cores, command=self.set_slider)
        self.cores_set_value = ttk.Label(self.settingspage_frame, textvariable=self.dedicated_cores, width=1)

        # pool address option select
        self.pools_select_label = ttk.Label(self.settingspage_frame, text="Select a pool:")
        self.pools_option_choices = ttk.Combobox(self.settingspage_frame, values=settings["pools"], width=40,
                                                 justify="center", state="readonly", textvariable=self.pool_address,
                                                 style="Custom.TCombobox")

        self.pool_address_entry = ttk.Entry(self.settingspage_frame, textvariable=self.pool_address, justify="center",
                                            state="disabled", foreground="grey", width=40)

        # wallet address
        self.wallet_address_entry_label = ttk.Label(self.settingspage_frame, text="Enter your wallet address:")
        self.wallet_address_entry = ttk.Entry(self.settingspage_frame, textvariable=self.wallet_address,
                                              justify="center", width=50)

        # worker name
        self.worker_name_entry_label = ttk.Label(self.settingspage_frame, text="Enter your worker name:")
        self.worker_name_entry = ttk.Entry(self.settingspage_frame, textvariable=self.worker_name, justify="center",
                                           width=50)

        # Save Button
        self.save_settings_button = ttk.Button(self.settingspage_frame, text="Save Changes", command=self.save_settings)

        # Misc
        self.temperature_control_frame = ttk.LabelFrame(self.settingspage_frame, text="Temperature Control Center")
        self.temperature_control_switch = ttk.Checkbutton(self.temperature_control_frame, text="Toggle")

        # navigationBar Page
        self.navigation_frame = ttk.Frame(self)
        self.home_button = ttk.Button(self.navigation_frame, text="Home", command=self.show_home, style="")
        self.settings_button = ttk.Button(self.navigation_frame, text="Settings", command=self.show_settings)

        #   packingElements
        # homepage
        self.homepage_frame.pack(fill="both")
        self.header_label.pack(fill="x", expand=True)
        self.mining_status_label.pack(fill="x", expand=True)
        self.start_mining_button.pack()

        # mining page
        # self.miningpage_frame.pack(fill="both")
        self.stop_mining_button.pack(padx=5)
        self.blocks_label.pack()
        self.temperature_label.pack()
        self.current_working_thread_label.pack()
        self.elapsed_time_label.pack()
        self.difficulty_label.pack()
        self.toggle_output_button.pack()

        # navigationBar
        self.navigation_frame.pack(side="bottom", pady=5)
        self.home_button.pack(side="left", padx=5)
        self.settings_button.pack(side="left")

        # settings page
        self.settings_header_label.pack(fill="x", expand=True)
        self.cores_label.pack()
        self.cores_label_info.pack(pady=5)
        self.cores_set_value.pack(pady=5)
        self.cores_scale.pack()
        self.pools_select_label.pack(pady=5)
        self.pools_option_choices.pack(pady=5)
        self.pool_address_entry.pack(pady=5)
        self.wallet_address_entry_label.pack(pady=5)
        self.wallet_address_entry.pack(pady=5)
        self.worker_name_entry_label.pack()
        self.worker_name_entry.pack()
        self.save_settings_button.pack(pady=5)
        self.temperature_control_frame.pack(pady=5)
        self.temperature_control_switch.pack()

        # binding functions
        self.pools_option_choices.bind("<<ComboboxSelected>>", self.on_pool_select)
        self.pool_address_entry.bind("<Return>", self.on_pool_entry)
        self.wallet_address_entry.bind("<Return>", self.on_wallet_entry)
        self.worker_name_entry.bind("<Key>", self.on_worker_name_entry)

        # initialising values
        # self.update_info()
        info_updater_thread = threading.Thread(target=self.update_info)
        info_updater_thread.daemon = True
        info_updater_thread.start()

    # functions
    def update_info(self):
        self.miningstatus.set(settings["mining"])
        while self.running.get():
            ## print("updating the info")
            # update is mining label
            is_mining = self.miningstatus.get()
            if is_mining:
                # print("mining is active")
                self.status_value.set("Active")
                self.mining_status_label.configure(background="#4BB94B", foreground="white")
            else:
                # print("mining is inactive")
                self.status_value.set("Inactive")
                self.mining_status_label.configure(background="#fca311", foreground="black")

            # get dedicated threads count
            ## print("getting the dedicated_cores count")
            self.dedicated_cores.set(settings["cores"])

            # get wallet address
            ## print("getting wallet address")
            self.wallet_address.set(settings["walletAddress"])

            # get pool address
            ## print("getting pool address")
            self.pool_address.set(settings["poolAddress"])
            self.pools_option_choices.set(self.pool_address.get())

            # get worker name
            ## print("getting worker name")
            self.worker_name.set(settings["workerName"])

            # get mining commands
            ## print("getting mining commands")
            self.mining_cmd.set(settings["miningCmd"])
            self.mining_cmd_template.set(settings["miningCmdTemplate"])

            # getting cpu temperature
            # self.temperature.set(self.get_cpu_temperature())
            time.sleep(.5)

    def show_settings(self):
        self.homepage_frame.pack_forget()
        self.miningpage_frame.pack_forget()
        self.settingspage_frame.pack(fill="both")

    def show_home(self):
        self.settingspage_frame.pack_forget()
        self.miningpage_frame.pack_forget()
        self.homepage_frame.pack(fill="both")

    def set_slider(self, event):
        self.dedicated_cores.set(round(self.dedicated_cores.get()))

    def on_wallet_entry(self, event):  # Check the wallet
        if self.wallet_address.get().find(" "):
            # print("Invalid Wallet")
            self.wallet_address.set(self.wallet_address.get().replace(" ", ""))

    def on_pool_select(self, event):
        selected_pool = self.pools_option_choices.get()
        if selected_pool == "Custom":
            self.pool_address.set("")
            self.pool_address_entry.configure(state="enabled", foreground="white")
        else:
            self.pool_address_entry.configure(state="disabled", foreground="grey")

    def on_pool_entry(self, event):
        pool_entry = self.pool_address_entry.get()
        match = regex.match(
            r"([a-zA-Z0-9\-]*?)?\.?([a-zA-Z0-9\-]*?)?\.?([a-zA-Z0-9]*?)?\.?([a-zA-Z0-9]*)?\.([a-zA-Z0-9]*)?:\d{4}",
            pool_entry)
        if match is None:
            print('invalid pool link')

    def on_worker_name_entry(self, event):
        worker_name = self.worker_name_entry.get().replace(' ', "_")
        worker_name = re.sub(r'[^a-zA-Z0-9_-]', '', worker_name)
        self.worker_name.set(worker_name)

    def save_settings(self):
        print("saving the settings")
        print("checking the wallet")
        resp = checkwallet.search_wallet(self.wallet_address.get())
        if resp == "Error":
            self.show_custom_warning(
                "Wallet address you provided is either invalid or is newly created\n"
                "No transactions have been found, but if you believe this your wallet, just recheck for safety"
                " and proceed")
        settings["walletAddress"] = self.wallet_address.get()
        settings["poolAddress"] = self.pool_address.get()
        settings["cores"] = self.dedicated_cores.get()
        settings["WorkerName"] = self.worker_name.get()

        cmd = self.mining_cmd_template.get()
        cmd = cmd.replace("<pool>", self.pool_address.get())
        cmd = cmd.replace("<address>", self.wallet_address.get())
        cmd = cmd.replace("<worker>", self.worker_name.get())
        cmd = cmd.replace("<cores>", str(self.dedicated_cores.get()))

        settings["miningCmd"] = cmd
        self.mining_cmd = cmd
        # print("generated new mining command")
        f = open("settings.json", "w")
        json.dump(settings, f, indent=4)
        f.close()
        # print("settings saved")

    def start_elapsed_time(self):
        self.mining_start_timestamp.set(int(time.time()))

    def get_elapsed_time(self):
        if self.mining_start_timestamp.get() == 0:
            print("last time stamp is 0 can't get anything")
            return
        S = int(time.time()) - int(self.mining_start_timestamp.get())
        result = ''
        days = S // 86400
        S = S % 86400
        if days != 0 and days != 1:
            result = f'{days} days '  # writes the seconds only when the value is neither 0 or 1
        elif days == 1:
            result = f'{days} day '  # remove the 's' when the value is 1

        hours = S // 3600
        S = S % 3600
        if hours != 0 and hours != 1:
            result += f'{hours} hours '
        elif hours == 1:
            result += f'{hours} hour '
        minutes = S // 60
        S = S % 60
        if minutes != 0 and minutes != 1:
            result += f'{minutes} minutes '
        elif minutes == 1:
            result += f'{minutes} minute'
        return result

    def toggle_output(self):
        if self.output_visible.get():
            self.output_text.pack_forget()
            self.output_visible.set(False)
        else:
            self.output_text.pack()
            self.output_visible.set(True)

    def show_custom_warning(self, message):
        # Create a new tkinter window for the custom warning dialog
        custom_warning = tk.Toplevel()
        custom_warning.title("Warning")

        # Create a label to display the warning message
        label = tk.Label(custom_warning, text=message)
        label.pack(padx=20, pady=20)

        # Create an "OK" button to close the custom warning dialog
        ok_button = tk.Button(custom_warning, text="OK", command=custom_warning.destroy)
        ok_button.pack(pady=10)

    # start mining
    def start_mining(self):
        if self.mining_thread and self.mining_thread.is_alive():
            self.homepage_frame.pack_forget()
            self.miningpage_frame.pack(fill="both")

        # print("Mining is starting")

        # Replace this with your actual mining command
        # print("getting the command")
        mining_command = self.mining_cmd.get()

        # print("setting the mining value to true")
        self.miningstatus.set(True)
        self.elapsed_time_value.set("just started")

        # print("opening the mining page")
        self.homepage_frame.pack_forget()
        self.miningpage_frame.pack(fill="both")
        self.homepage_button_text.set("Return to the mining page")

        # Function to capture and display the miner output
        def capture_output():
            # print("starting the mining process in a new thread")
            process = subprocess.Popen(mining_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
                                       text=True)
            ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')  # Regular expression to match ANSI escape codes

            for line in process.stdout:
                if self.miningstatus.get() != True:
                    # print("mining is set to false breaking the loop")
                    break
                # Remove ANSI escape codes from the line
                # print("cleaning the line")
                clean_line = ansi_escape.sub('', line)
                line = clean_line
                self.output_text.insert(tk.END, clean_line)
                self.output_text.see(tk.END)  # Scroll to the end to show the latest output

                # Parse the line to extract useful information
                if "accepted:" in line:
                    # print("got useful info from the terminal")
                    blocks = str(re.search(r'\d+/\d+', line).group(0))
                    print("blocks Mined: " + blocks)
                    difficulty = float(re.search(r'diff \d*.\d*', line).group(0).replace("diff ", ""))
                    print(f"Difficulty: {difficulty}")
                    speed = str(re.search(r"\d*.\d* kH/s", line).group(0))
                    print("Mining Speed: " + speed)

                    # print("updating the values")
                    # Update your GUI elements with the extracted data
                    self.blocks_mined_value.set(f"Blocks Mined: {blocks}")
                    self.difficulty_value.set(f"Difficulty: {difficulty:.2f}")
                    self.mining_speed_value.set(speed)
                    self.elapsed_time_value.set(self.get_elapsed_time())

                elif "CPU T" in line:
                    # print("found the working cpu core")
                    no_timestamp = regex.sub(r"\[[\d-]*.[\d:]*\] ", "", line)
                    self.current_working_thread.set("Core " + str(int(no_timestamp.replace("CPU T", "").replace(
                        ": Verus Hashing", ""))))

            # process.wait()
            process.terminate()
            print("Mining process stopped by the user.")


        # Start the mining thread
        self.mining_thread = threading.Thread(target=capture_output)
        self.mining_thread.daemon = True
        self.mining_thread.start()
        self.start_elapsed_time()

    def stop_mining(self):
        # Terminate the mining thread (you can replace this with a more graceful termination method)
        if self.mining_thread and self.mining_thread.is_alive():
            self.miningstatus.set(False)
            self.homepage_frame.pack(fill="both")
            self.miningpage_frame.pack_forget()
            # print("Mining Thread Terminated")
            # print("killing the miner process...")
            self.kill_miner_process()
            self.blocks_mined_value.set("blocks mined")
            self.elapsed_time_value.set("elapsed time")
            self.difficulty_value.set("difficulty")
            self.mining_speed_value.set("mining speed")
            self.current_working_thread.set("current working core")
            self.temperature.set("Couldn't retreive the temperature")
            self.homepage_button_text.set("Start Mining")
            # print("miner process killed successfully")
        else:
            print("Mining is not running.")

    def kill_miner_process(self):
        process_name = "ccminer.exe"
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == process_name:
                try:
                    # Terminate the process
                    process_obj = psutil.Process(process.info['pid'])
                    process_obj.terminate()
                    # print(f"Killed process '{process_name}' with PID {process.info['pid']}")
                except Exception as e:
                    print(f"Failed to kill process '{process_name}': {str(e)}")

    def onDelete(self):
        if self.miningstatus.get():
            answer = tkinter.messagebox.askyesno(title='You are still mining!',
                                                 message='Are you sure that you want to quit?\n'
                                                         f'{self.blocks_mined_value.get()}\n'
                                                         f'{self.difficulty_value.get()}\n'
                                                         f'{self.mining_speed_value}')
            if answer:
                self.running.set(False)
                self.kill_miner_process()
                time.sleep(.5)
                self.destroy()
                exit()
        else:
            self.running.set(False)
            time.sleep(.5)
            self.destroy()
            exit()


if __name__ == "__main__":
    app = App()

    # handle exiting
    app.protocol("WM_DELETE_WINDOW", app.onDelete)
    # set theme
    if settings['theme'] == "sv":
        app.call("source", "themes/sv.tcl")
    elif settings['theme'] == "azure":
        app.call("source", "themes/azure.tcl")
    # set mode
    if settings["darkmode"]:
        app.tk.call("set_theme", "dark")
    else:
        app.tk.call("set_theme", "light")

    app.mainloop()
