import pypresence
import threading
import asyncio
import random
import json
import sys
import os

from time import time, sleep
from math import floor

import tkinter as tk
from tkinter import ttk

if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))

with open("settings.json") as save_file:
    save_data = json.loads(save_file.read())

#UI
root = tk.Tk()
root.title("Status Generator")
frame = ttk.Frame(root, padding=20)
frame.grid()

error_msg = ttk.Label(frame, text="")
error_msg.grid(column=0, row=1)

settings_reference = [
    {
        "title": "Change Picture Every ... Seconds",
        "field": "refresh_rate",
        "int": True,
        "default": 60
    },
    {
        "title": "Timezone Offset From UTC",
        "field": "timezone",
        "int": True,
        "default": -6
    },
    {
        "title": "Line 1 Message",
        "field": "details",
        "int": False
    },
    {
        "title": "Line 2 Message",
        "field": "state",
        "int": False
    },
    {
        "title": "Holo Picture Hover Text",
        "field": "large_text",
        "int": False
    },
    {
        "title": "Cookie Picture Hover Text",
        "field": "small_text",
        "int": False
    },
    {
        "title": "Button 1 Text",
        "field": "button1_text",
        "int": False
    },
    {
        "title": "Button 1 Link",
        "field": "button1_link",
        "int": False
    },
    {
        "title": "Button 2 Text",
        "field": "button2_text",
        "int": False
    },
    {
        "title": "Button 2 Link",
        "field": "button2_link",
        "int": False
    }
]

for i, field in enumerate(settings_reference):
    ttk.Label(frame, text=field["title"]).grid(row=i * 2 + 1, column=0)
    entry = ttk.Entry(frame)
    entry.grid(row=i * 2 + 2, column=0)
    entry.insert(0, save_data[field["field"]])
    field.update({"entry": entry})

#UI Save Sync
def settings_reader():

    def convert_int(x, default=1):
        try:
            return int(x)
        except:
            return default

    while True:
        sleep(1)
        do_write = False

        for field in settings_reference:
            if field["int"]:
                if convert_int(field["entry"].get(), default=field["default"]) != save_data[field["field"]]:
                    save_data[field["field"]] = convert_int(field["entry"].get())
                    do_write = True
            else:
                if field["entry"].get() != save_data[field["field"]]:
                    save_data[field["field"]] = field["entry"].get()
                    do_write = True

        if do_write:
            with open("settings.json", "w") as save_file:
                save_file.write(json.dumps(save_data, indent=2))

threading.Thread(target=settings_reader, daemon=True).start()

#RPC
rpc = pypresence.Presence("1320522645426405436", loop=asyncio.new_event_loop())
rpc.connect()

def rpc_loop():
    def index_bag():
        options = list(range(26))
        while True:
            yield options.pop(random.randint(0, len(options) - 1))
            if options == []:
                options = list(range(26))

    for id in index_bag():
        try:
            rpc.update(
                details = save_data["details"],
                state = save_data["state"],

                start = floor(time()) - (floor(time()) + 3600 * int(save_data["timezone"])) % 86400, #UTC - 6 hours mod seconds in a day

                large_image=str(id),
                large_text=save_data["large_text"],

                small_image="cookie",
                small_text=save_data["small_text"],

                buttons = [
                    {"label": save_data["button1_text"], "url": save_data["button1_link"]},
                    {"label": save_data["button2_text"], "url": save_data["button2_link"]}
                ]
            )
        except Exception as e:
            error_msg.config(text=f"Status: {type(e)}: {e}")
        finally:
            error_msg.config(text="Status: Good")
        sleep(save_data["refresh_rate"])

threading.Thread(target=rpc_loop, daemon=True).start()

root.mainloop()
sys.exit()