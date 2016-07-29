"""
Tkinter GUI Class (local usage only)
"""
import threading
import os
import json
import Tkinter as tk

"""
GUI for RHUM (v1) control system
"""
class GUI_v1(threading.Thread):
    def __init__(self, settings='../settings.json'):
        self.active_changes = False
        settings_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), settings)
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as jsonfile:
                self.settings = json.loads(jsonfile.read())  
        else:
            self.settings =  {} # by default is empty until set
        self.active_changes = True
        threading.Thread.__init__(self)
    def run(self):
        self.root = tk.Tk()
        self.root.title("Hydroponics Controller (V1)")
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (w,h))
        self.root.overrideredirect(1)
        [self.root.rowconfigure(i,weight=1) for i in range(12)]
        [self.root.columnconfigure(i,weight=1) for i in range(3)]
        
        # Lights
        self.lights_on = tk.IntVar()
        scale_lights_on = tk.Scale(self.root, from_=0.0, to=24.0, length=200, orient=tk.HORIZONTAL, variable = self.lights_on)
        scale_lights_on.grid(column=0, row=2, ipady=20)
        scale_lights_on.set(self.settings['lights_on'])
        self.lights_off = tk.IntVar()
        scale_lights_off = tk.Scale(self.root, from_=0.0, to=24.0, length=200, orient=tk.HORIZONTAL, variable = self.lights_off)
        scale_lights_off.grid(column=0, row=3, ipady=20)
        scale_lights_off.set(self.settings['lights_off'])
        self.photo1 = tk.IntVar()
        scale_photo1 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.photo1)
        scale_photo1.grid(column=0, row=4, ipady=20)
        scale_photo1.set(self.settings['photo1'])
        self.photo2 = tk.IntVar()
        scale_photo2 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.photo2)
        scale_photo2.grid(column=0, row=5, ipady=20)
        scale_photo2.set(self.settings['photo2'])
        
        # Watering
        self.watering = tk.IntVar()
        self.scale_watering = tk.Scale(self.root, from_=0.0, to=60.0, length=200, orient=tk.HORIZONTAL, variable = self.watering)
        self.scale_watering.grid(column=1, row=2, ipady=20)
        self.scale_watering.set(self.settings['watering'])
        self.smc1 = tk.IntVar()
        scale_smc1 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc1)
        scale_smc1.grid(column=1, row=3, ipady=20)
        scale_smc1.set(self.settings['smc1'])
        self.smc2 = tk.IntVar()
        scale_smc2 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc2)
        scale_smc2.grid(column=1, row=4, ipady=20)
        scale_smc2.set(self.settings['smc2'])
        self.smc3 = tk.IntVar()
        scale_smc3 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc3)
        scale_smc3.grid(column=1, row=5, ipady=20)
        scale_smc3.set(self.settings['smc3'])
        self.smc4 = tk.IntVar()
        scale_smc4 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc4)
        scale_smc4.grid(column=1, row=6, ipady=20)
        scale_smc4.set(self.settings['smc4'])

        # Cycle Time
        self.cycle = tk.IntVar()
        self.scale_cycle = tk.Scale(self.root, from_=0.0, to=360.0, length=200, orient=tk.HORIZONTAL, variable = self.cycle)
        self.scale_cycle.grid(column=2, row=2, ipady=20)
        self.scale_cycle.set(self.settings['cycle'])

        # Set Button
        self.button_set = tk.Button(self.root, text="Set Configuration", command=self.set_config)
        self.button_set.grid(column=1, row=4)

        # Reset to saved values and start engine
        self.set_config()
        self.root.focus_set() # move focus to widget
        self.root.bind("<Escape>", lambda e: e.widget.quit())
        self.root.mainloop()

    def set_config(self, settings='settings.json'): # called from button_set object
        """
        Updates the dictionary object for settings provided by the GUI
        """        
        self.settings['lights_on'] = self.lights_on.get()
        self.settings['lights_off'] = self.lights_off.get()
        self.settings['photo1'] = self.photo1.get()
        self.settings['photo2'] = self.photo2.get()
        self.settings['smc1'] = self.smc1.get()
        self.settings['smc2'] = self.smc2.get()
        self.settings['smc3'] = self.smc3.get()
        self.settings['smc4'] = self.smc4.get()
        self.settings['watering'] = self.watering.get()
        self.settings['cycle'] = self.cycle.get()
        settings_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), settings)
        if os.path.exists(settings_path):
            with open(settings_path, 'w') as jsonfile:
                jsonfile.write(json.dumps(self.settings, indent=4))
        self.active_changes = True # (flag) changes are active!
    def get_new_targets(self):
        """
        Returns the dictionary object for settings provided by the GUI
        """
        self.active_changes = False # (flag) Once changes are retrieved, we assume that they will be sent to the controller
        return self.settings
    def update_readings(self, settings):
        """
        Overrides the dictionary object for settings provided by the GUI
        """
        self.settings = settings
        self.scale_watering.set(settings['watering'])
        self.scale_cycle.set(settings['cycle'])
        self.scale_lights_off.set(settings['lights_off'])
        self.scale_lights_on.set(settings['lights_on'])
        self.scale_photo1.set(settings['photo1'])
        self.scale_photo2.set(settings['photo2'])
        self.scale_smc1.set(settings['smc1'])
        self.scale_smc2.set(settings['smc2'])
        self.scale_smc3.set(settings['smc3'])
        self.scale_smc4.set(settings['smc4'])
    def close(self):
        self.root.destroy()

"""
GUI for the custom Bronfman RHUM control system
"""
class GUI_bronfman(threading.Thread):
    
    def __init__(self, settings='../settings.json'):
        self.active_changes = False
        self.settings_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), settings)
        if os.path.exists(self.settings_path):
            print "FOUND SETTINGS FILE"
            with open(self.settings_path, 'r') as jsonfile:
                self.settings = json.loads(jsonfile.read())  
        else:
            raise Exception("Failed to get settings!")
        self.active_changes = True

        # The named keys for all of the items in the GUI and 
        setting_keys = [
            "lights_off", 
            "lights_on", 
            "ambient_min",
            "overhead_level",
            "soil_1",
            "soil_2",
            "soil_3",
            "soil_4",
        ]
        self.settings = { str(key):value for key,value in self.settings.items() } # convert from unicode to ascii
        for k in setting_keys:
            try:
                self.settings[k]
            except:
                self.settings[k] = 0
        threading.Thread.__init__(self)
        self.font = font="Arial 11 bold"

    def run(self, w=640, h=480):
        print("INITIAL_PARAMS: %s" % self.settings)
        self.root = tk.Tk()
        self.root.title("Hydroponics Controller (Bronfman)")
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (w,h))
        self.root.overrideredirect(1)
        [self.root.rowconfigure(i,weight=1) for i in range(10)]
        [self.root.columnconfigure(i,weight=1) for i in range(3)]
        
        ## Lights
        # Intercanopy
        self.lights_on = tk.IntVar()
        self.scale_lights_on = tk.Scale(self.root, from_=0.0, to=24.0, length=200, orient=tk.HORIZONTAL, variable = self.lights_on, width=25)
        self.scale_lights_on.grid(column=0, row=3, ipady=20)
        self.scale_lights_on.set(self.settings['lights_on'])
        self.lights_off = tk.IntVar()
        self.scale_lights_off = tk.Scale(self.root, from_=0.0, to=24.0, length=200, orient=tk.HORIZONTAL, variable = self.lights_off, width=25)
        self.scale_lights_off.grid(column=0, row=5, ipady=20)
        self.scale_lights_off.set(self.settings['lights_off'])
        self.label_lights_on = tk.Label(self.root, text='Lumiere ON (hr)', font=self.font)
        self.label_lights_on.grid(column=0, row=2)
        self.label_lights_off = tk.Label(self.root, text='Lumiere OFF (hr)', font=self.font)
        self.label_lights_off.grid(column=0, row=4)
        
        # Overhead Light Trigger
        self.ambient_light_template = 'Limite Lumiere Active: %d%%'
        self.label_ambient_min = tk.Label(self.root, text=self.ambient_light_template, font=self.font)
        self.label_ambient_min.grid(column=0, row=7)
        self.ambient_min = tk.IntVar()
        self.scale_ambient_min = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.ambient_min, width=25)
        self.scale_ambient_min.grid(column=0, row=8, ipady=20)
        self.scale_ambient_min.set(self.settings['ambient_min'])

        ## Soil Moisture Values
        # Soil MC #1
        self.smc1_template = 'Bed #1, Nord: %d%%'
        self.label_smc1 = tk.Label(self.root, text=self.smc1_template, font=self.font)
        self.label_smc1.grid(column=1, row=2)
        self.smc1 = tk.IntVar()
        self.scale_smc1 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc1, width=25)
        self.scale_smc1.grid(column=1, row=3, ipady=20)
        self.scale_smc1.set(self.settings['soil_1'])

        # Soil MC #2
        self.smc2_template = 'Bed #1, Sud: %d%%'
        self.label_smc2 = tk.Label(self.root, text=self.smc2_template, font=self.font)
        self.label_smc2.grid(column=1, row=4)
        self.smc2 = tk.IntVar()
        self.scale_smc2 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc2, width=25)
        self.scale_smc2.grid(column=1, row=5, ipady=20)
        self.scale_smc2.set(self.settings['soil_2'])

        # Soil MC #3
        self.smc3_template = 'Bed #2, Nord: %d%%'
        self.label_smc3 = tk.Label(self.root, text=self.smc3_template, font=self.font)
        self.label_smc3.grid(column=2, row=2)
        self.smc3 = tk.IntVar()
        self.scale_smc3 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc3, width=25)
        self.scale_smc3.grid(column=2, row=3, ipady=20)
        self.scale_smc3.set(self.settings['soil_3'])
        
        # Soil MC #4
        self.smc4_template = 'Bed #2, Sud: %d%%'
        self.label_smc4 = tk.Label(self.root, text=self.smc4_template, font=self.font)
        self.label_smc4.grid(column=2, row=4)
        self.smc4 = tk.IntVar()
        self.scale_smc4 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc4, width=25)
        self.scale_smc4.grid(column=2, row=5, ipady=20)
        self.scale_smc4.set(self.settings['soil_4'])

        # Overhead Light Level
        self.overhead_level_template = 'Overhead Lumiere: %d%%'
        self.label_overhead_level = tk.Label(self.root, text=self.overhead_level_template, font=self.font)
        self.label_overhead_level.grid(column=1, row=7)
        self.overhead_level = tk.IntVar()
        self.scale_overhead_level = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.overhead_level, width=25)
        self.scale_overhead_level.grid(column=1, row=8, ipady=20)
        self.scale_overhead_level.set(self.settings['overhead_level'])

        # Kill
        self.button_kill = tk.Button(self.root, text="Update", command=self.set_config, bg = "green", padx=20, pady=20)
        self.button_kill.grid(column=2, row=7)
        self.button_kill = tk.Button(self.root, text="All Off", command=self.kill_all, bg = "red", padx=20, pady=20)
        self.button_kill.grid(column=2, row=8)

        # Focus, fullscreen, set to saved values, and start application
        self.update_values(None)
        self.root.focus_set() # move focus to widget
        self.set_config()
        self.root.bind("<Escape>", lambda e: e.widget.quit())
        self.root.mainloop()

    def set_config(self): # called from button_set object
        """
        Updates the dictionary object for settings provided by the GUI
        """        
        self.settings['lights_on'] = self.lights_on.get()
        self.settings['lights_off'] = self.lights_off.get()
        self.settings['ambient_min'] = self.ambient_min.get()
        self.settings['soil_1'] = self.smc1.get()
        self.settings['soil_2'] = self.smc2.get()
        self.settings['soil_3'] = self.smc3.get()
        self.settings['soil_4'] = self.smc4.get()
        self.settings['overhead_level'] = self.overhead_level.get()

        # Save settings to config file in case of reboot / power-loss
        print "UPDATING SETTINGS FILE"
        with open(self.settings_path, 'w') as jsonfile:
            jsonfile.write(json.dumps(self.settings, indent=4))
        self.active_changes = True # (flag) changes are active!

    def get_values(self):
        """
        Returns the dictionary object for settings provided by the GUI
        """
        self.active_changes = False # (flag) Once changes are retrieved, we assume that they will be sent to the controller
        return self.settings

    def update_values(self, values):
        """
        Overrides the dictionary object for settings provided by the GUI
        """
        if values is not None:
            self.settings.update(values)

        # External (from MCU)
        self.label_smc1.configure(text=self.smc1_template % self.settings['s1'], font=self.font)
        self.label_smc2.configure(text=self.smc2_template % self.settings['s2'], font=self.font)
        self.label_smc3.configure(text=self.smc3_template % self.settings['s3'], font=self.font)
        self.label_smc4.configure(text=self.smc4_template % self.settings['s4'], font=self.font)
        self.label_ambient_min.configure(text=self.ambient_light_template % self.settings['p'], font=self.font)

        # Internal (from GUI)
        self.label_overhead_level.configure(text=self.overhead_level_template % self.overhead_level.get(), font=self.font)
        self.active_changes = True # (flag) Once changes are retrieved, we assume that they will be sent to the controller

    def kill_all(self):
        """
        Disable all valves and lights
        """
        self.settings['lights_on'] = 12
        self.settings['lights_off'] = 12
        self.settings['overhead_level'] = 0
        self.settings['soil_1'] = 0
        self.settings['soil_2'] = 0
        self.settings['soil_3'] = 0
        self.settings['soil_4'] = 0
        self.scale_overhead_level.set(self.settings['overhead_level'])
        self.scale_smc1.set(self.settings['soil_1'])
        self.scale_smc2.set(self.settings['soil_2'])
        self.scale_smc3.set(self.settings['soil_3'])
        self.scale_smc4.set(self.settings['soil_4'])
        self.active_changes = True # (flag) Once changes are retrieved, we assume that they will be sent to the controller

    def close(self):
        """
        Safely close the TK GUI
        """
        print("CAUGHT CLOSE SIGNAL")
        self.root.destroy()
