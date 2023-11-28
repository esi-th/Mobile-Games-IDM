from bs4 import BeautifulSoup
from pySmartDL import SmartDL
from configs import urls
from tkinter import ttk
import tkinter as tk
import threading
import requests
import shutil
import time
import os


def check_last_update_farsroid(farsroid_url):
    """
    request to farsroid and get GLOBAL version
    :param farsroid_url:
    :param name:
    :return:version number
    """
    response = requests.get(farsroid_url)
    page = BeautifulSoup(response.content, 'lxml')
    content_info = page.find("ul", {"class": "post-infs"}).get_text(strip=True)
    version = list(content_info.split('نسخه نهایی'))
    version = version[1].split('اندروید')

    return version[0]


def check_last_update(url):
    """
    request to apk pure game page and get last version number of game
    :param url: games configs
    :return: GLOBAL last game version number
    """
    response = requests.get(f"https://proxy.scrapeops.io/v1/?api_key=6a7467aa-bbda-4502-8d4b-869d5aea2e36&url="
                            f"{url}/download&bypass=cloudflare")
    page = BeautifulSoup(response.content, 'lxml')
    content_info = page.find("div", {"class": "info-content"}).get_text(strip=True)

    content_info = content_info.split('by')
    version = content_info[0].split('XAPK')

    if len(version) < 2:
        version = content_info[0].split('APK')

    return version[1]


def check_files_version(storage_drive, info):
    """
    check SDcard for saved current version numbers
    :param storage_drive:
    :param info:
    :return: SDCARD game version number
    """
    game_file_path = os.listdir(f"{storage_drive}{info['Base Path']}")[0].split('v')
    our_version = game_file_path[1].split('xapk')

    if len(our_version) < 2:
        our_version = game_file_path[1].split('apk')

    return our_version[0][:-1]


def delete_file(storage_drive, info):
    """
    format disk for rewrite
    :param storage_drive:
    :param info:
    :return:
    """
    game_file_path = f"{storage_drive}{info['Base Path']}"
    game_file_name = os.listdir(f"{storage_drive}{info['Base Path']}")[0]
    os.remove(game_file_path + game_file_name)


def check_for_updates(storage_drive, games_last_version):
    """
    compare GLOBAl game last version number and SDCARD game version number
    :param storage_drive:
    :param games_last_version:
    :return: returns number of available updates
    """
    available_updates = 0
    for name, info in urls.items():

        our_version = check_files_version(storage_drive, info)
        btn_format['state'] = 'disabled'
        ent_log.insert(tk.END, f'{name} | Checking... \n')
        last_version = check_last_update(info['Link'])

        if our_version == last_version:
            ent_log.insert(tk.END, f"{name} Is Last Version | v{our_version}\n\n")
        else:
            games_last_version[name] = {"Last Version": last_version}
            available_updates += 1
            ent_log.insert(tk.END, f'{name} | New version available | v{our_version} to v{last_version}\n\n')

    print(urls)
    return available_updates


def format_disk(storage_drive, names):
    """
    initial format and rewrite SDCARD base files
    :param storage_drive:
    :param names:
    :return:
    """
    try:
        files_list = os.listdir(f"{storage_drive}:/")
        if 'Downloads' in files_list:
            parent = f"{storage_drive}:/"
            directory = 'Downloads'
            path = os.path.join(parent, directory)
            shutil.rmtree(path)

    except OSError:
        ent_log.insert(tk.END, f"\nWong Drive Name OR Internet OR The Drive Is Not connected")
        lbl_status['text'] = f"\nStatus: Wong Drive Name Internet OR OR The Drive Is Not connected"

    dest = f"{storage_drive}:/"
    final_directory = os.path.join(dest, r'Downloads')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    ent_log.insert(tk.END, f"Formating Disk... \n\n")
    for name, info in names.items():
        print(name)
        os.makedirs(f"{storage_drive}:/Downloads/{name}/")
        ent_log.insert(tk.END, f"Creating: {storage_drive}:/Downloads/{name}/\n")
        with open(f"{storage_drive}{info['Base Path']}{name} v0.0.{info['File Type']}", 'w') as fp:
            ent_log.insert(tk.END, f"Creating: {storage_drive}{info['Base Path']}{name} Version: x00.010\n")
            pass
    ent_log.insert(tk.END, f"\nDrive: {storage_drive} Formated Successfully.\n")


if __name__ == '__main__':
    games_last_version = dict()
    for url in urls:
        games_last_version.update({url: {"Last Version": '0.0'}})

    window = tk.Tk()
    window.resizable(width=False, height=False)
    window.title('Mojo Downloader')

    work_status = "Idle"

    drive_name = tk.StringVar()


    def start_check():
        try:
            lbl_status['text'] = 'Status: Checking...'
            available_updates = check_for_updates(drive_name.get(), games_last_version)
            ent_log.insert(tk.END, f"Found {available_updates} Updates.\n\n")
            lbl_status['text'] = 'Status: Idle'
            lbl_available_updates['text'] = f'Available Updates: {available_updates}'
            btn_start['state'] = 'enabled'
            btn_format['state'] = 'enabled'
        except OSError:
            ent_log.insert(tk.END, f"\nWong Drive Name OR Internet OR The Drive Is Not connected\n")
            lbl_status['text'] = f'\nStatus: Wong Drive Name OR Internet OR The Drive Is Not connected\n'
        return


    def start_update():
        ent_log.insert(tk.END, f'Updating Started...\n\n')
        btn_format['state'] = 'disabled'
        for name, update in games_last_version.items():
            if update['Last Version'] != '0.0':
                dest = f"{drive_name.get()}{urls[name]['Base Path']}{name} " \
                       f"v{games_last_version[name]['Last Version']}.{urls[name]['File Type']}"
                delete_file(drive_name.get(), urls[name])
                ent_log.insert(tk.END, f'Updating {name}...\n')
                obj = SmartDL(urls[name]['Download Link'], dest, progress_bar=True)
                obj.start(blocking=False)

                while not obj.isFinished():
                    lbl_speed['text'] = f"Speed: {obj.get_speed(human=True)}"
                    lbl_ad['text'] = f"Already downloaded: {obj.get_dl_size(human=True)}"
                    lbl_progress['text'] = f"Progress: {int(obj.get_progress() * 100)}%"
                    lbl_status['text'] = f"Status: {obj.get_status()}"
                    pb_download['value'] = int(obj.get_progress() * 100)
                    window.update()
                    time.sleep(0.2)

                path = obj.get_dest()
                ent_log.insert(tk.END, f'{name} Updated successfully.\n\n')
        lbl_status['text'] = f"Status: Idle"
        ent_log.insert(tk.END, f'\n\nAll Games Updated Successfully.')


    def start_format():
        format_disk(drive_name.get(), urls)


    btn_check = ttk.Button(
        master=window,
        text='Check for Updates',
        command=threading.Thread(target=start_check).start,
        width=20
    )

    btn_start = ttk.Button(
        master=window,
        text='Start',
        command=threading.Thread(target=start_update).start,
        width=20,
        state='disabled'
    )

    btn_format = ttk.Button(
        master=window,
        text='Format Disk',
        command=threading.Thread(target=start_format).start,
        width=20
    )

    ent_drive = ttk.Entry(
        master=window,
        width=4,
        textvariable=drive_name
    )

    ent_log = tk.Text(
        master=window,
        width=80,
        height=10,
        font=("Helvetica", 9)
    )

    lbl_available_updates = ttk.Label(
        master=window,
        text=f'Available Updates: 0'

    )
    lbl_drive_name = ttk.Label(
        master=window,
        text='Drive Name: '
    )

    lbl_status = ttk.Label(
        master=window,
        text='Status: Idle'
    )

    lbl_speed = ttk.Label(
        master=window,
        text='Speed: 0 MB/s'
    )

    lbl_ad = ttk.Label(
        master=window,
        text='Already downloaded: 0 MB'
    )

    lbl_eta = ttk.Label(
        master=window,
        text='Eta: 0 Seconds'
    )

    lbl_progress = ttk.Label(
        master=window,
        text='Progress: 0%'
    )

    lbl_help = ttk.Label(
        master=window,
        text='HELP => @esiam01'
    )

    pb_download = ttk.Progressbar(
        master=window,
        mode='determinate',
        value=0
    )
    btn_check.grid(row=0, column=0, padx=10, pady=10, sticky='we')
    btn_start.grid(row=0, column=1, padx=10, pady=10, sticky='we')
    btn_format.grid(row=0, column=2, padx=10, pady=10, sticky='we')
    lbl_drive_name.grid(row=1, column=0, padx=10, pady=10, sticky='w')
    lbl_available_updates.grid(row=1, column=1, padx=10, pady=10)
    ent_drive.grid(row=1, column=0, padx=10, pady=10, sticky='e')
    lbl_status.grid(row=2, column=0, padx=10, pady=10, sticky='w', columnspan=3)
    ent_log.grid(row=5, column=0, padx=10, pady=10, columnspan=3)
    pb_download.grid(row=3, column=0, pady=10, padx=10, columnspan=3, sticky='we')
    lbl_speed.grid(row=4, column=0, pady=10, padx=10)
    lbl_ad.grid(row=4, column=2, pady=10, padx=10)
    lbl_progress.grid(row=4, column=1, pady=10, padx=10)
    lbl_help.grid(row=2, column=2, pady=10, padx=10)
    window.mainloop()
