from datetime import datetime
import os
from pathlib import Path
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import traceback

from labs import LABS


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / 'runtime' / 'python' / 'python.exe'
WEBOTS_HOME = ROOT / 'runtime' / 'webots'
WEBOTS = WEBOTS_HOME / 'msys64' / 'mingw64' / 'bin' / 'webots.exe'
WORLD_DIR = ROOT / 'kit' / 'worlds'
LOG_DIR = ROOT / 'logs'


def environment():
    env = {key: value for key, value in os.environ.items()
           if not key.upper().startswith(('PYTHON', 'WEBOTS_', 'TCL_', 'TK_', 'QT_'))}
    env.update(ROBO_KIT_PYTHON=str(PYTHON), PYTHONNOUSERSITE='1',
               PYTHONDONTWRITEBYTECODE='1', WEBOTS_HOME=str(WEBOTS_HOME))
    return env


def webots_command(world, realtime=True):
    return [str(WEBOTS), '--batch', '--stdout', '--stderr',
            '--mode=realtime' if realtime else '--mode=fast', str(world)]


def start_process(world, logfile):
    LOG_DIR.mkdir(exist_ok=True)
    with logfile.open('wb') as stream:
        return subprocess.Popen(webots_command(world), cwd=str(WEBOTS.parent), env=environment(),
                                stdout=stream, stderr=subprocess.STDOUT,
                                creationflags=subprocess.CREATE_NO_WINDOW)


class Launcher:
    def __init__(self, window):
        self.window = window
        self.process = None
        self.running_lab = None
        self.logfile = None
        self.status = tk.StringVar(value='请选择实验。建议从 10.1 开始。')
        self.detail = tk.StringVar()
        window.title('训练师机器人仿真｜实验启动台')
        window.geometry('790x650')
        window.minsize(670, 580)
        panel = ttk.Frame(window, padding=16)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='训练师机器人仿真', font=('Microsoft YaHei UI', 18, 'bold')).pack(anchor='w')
        ttk.Label(panel, text='请选择实验 → 开始仿真 → 观察结果 → 自行记录').pack(anchor='w', pady=(4, 10))
        list_panel = ttk.Frame(panel)
        list_panel.pack(fill='both', expand=True)
        scrollbar = ttk.Scrollbar(list_panel, orient='vertical')
        self.table = ttk.Treeview(list_panel, columns=('code', 'name'), show='headings',
                                  height=16, selectmode='browse', yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.table.yview)
        scrollbar.pack(side='right', fill='y')
        self.table.heading('code', text='实验编号')
        self.table.heading('name', text='实验名称')
        self.table.column('code', width=95, stretch=False, anchor='center')
        self.table.column('name', width=520)
        self.table.pack(side='left', fill='both', expand=True)
        for code, name, _, _ in LABS:
            self.table.insert('', 'end', iid=code, values=(code, name))
        self.table.bind('<<TreeviewSelect>>', self.select)
        self.table.bind('<Double-Button-1>', self.double_click)
        self.table.selection_set(LABS[0][0])
        ttk.Label(panel, textvariable=self.detail, wraplength=610, justify='left').pack(fill='x', pady=(9, 6))
        buttons = ttk.Frame(panel)
        buttons.pack(fill='x', pady=(4, 8))
        self.start_button = ttk.Button(buttons, text='开始仿真', command=self.start)
        self.start_button.pack(side='left', padx=(0, 8))
        for label, path in [('打开运行日志', LOG_DIR), ('新手说明', ROOT / '使用说明.txt')]:
            ttk.Button(buttons, text=label, command=lambda target=path: self.open_path(target)).pack(side='left', padx=(0, 8))
        ttk.Label(panel, textvariable=self.status, wraplength=610, justify='left').pack(fill='x')
        window.protocol('WM_DELETE_WINDOW', self.close)
        self.select()
        window.after(80, self.poll)

    def selection(self):
        selected = self.table.selection()
        return next((lab for lab in LABS if selected and lab[0] == selected[0]), None)

    def select(self, event=None):
        lab = self.selection()
        self.detail.set('截图时机：' + lab[3] if lab else '请选择实验。')

    def double_click(self, event):
        if self.table.identify_row(event.y):
            self.start()

    def open_path(self, path):
        try:
            if path == LOG_DIR:
                path.mkdir(exist_ok=True)
            os.startfile(str(path))
        except OSError as exc:
            messagebox.showerror('无法打开文件', str(exc), parent=self.window)

    def start(self):
        lab = self.selection()
        if not lab or self.process is not None:
            return
        try:
            if not WEBOTS.is_file() or not PYTHON.is_file():
                raise FileNotFoundError('运行环境不完整。请用 Windows「全部解压缩」重新解压 ZIP，不要在压缩包内运行。')
            if not (WORLD_DIR / lab[2]).is_file():
                raise FileNotFoundError(lab[2])
            calibration = ROOT / 'kit' / 'shared' / 'eye2arm.json'
            if lab[0] in ('11.7', '11.8') and not calibration.is_file():
                raise FileNotFoundError('缺少标定文件。请先运行 11.6，看到 eye2arm.json written 后再回来。')
            self.logfile = LOG_DIR / f'{lab[0]}_{datetime.now():%Y%m%d_%H%M%S_%f}.log'
            self.process = start_process(WORLD_DIR / lab[2], self.logfile)
        except OSError as exc:
            messagebox.showerror('无法启动 Webots', str(exc), parent=self.window)
            return
        self.running_lab = lab[0]
        self.start_button.state(['disabled'])
        self.status.set(f'正在运行 {self.running_lab}。关掉该 Webots 窗口后可选下一项。')
        self.window.iconify()

    def poll(self):
        if self.process is not None:
            code = self.process.poll()
            if code is not None:
                lab = self.running_lab
                self.process = self.running_lab = None
                self.start_button.state(['!disabled'])
                self.window.deiconify()
                self.window.lift()
                if code == 0:
                    self.status.set(f'{lab} 已关闭，可继续选下一项。')
                else:
                    self.status.set(f'{lab} 的 Webots 已退出（{code}）。请查看日志 {self.logfile.name}。')
        self.window.after(80, self.poll)

    def close(self):
        if self.process is not None and not messagebox.askyesno(
            '退出启动台', '实验正在运行。退出启动台不会关闭 Webots。确定退出吗？',
            parent=self.window,
        ):
            return
        self.window.destroy()


def main():
    window = tk.Tk()
    Launcher(window)
    window.mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import ctypes

        LOG_DIR.mkdir(exist_ok=True)
        (LOG_DIR / 'launcher-error.log').write_text(traceback.format_exc(), encoding='utf-8')
        ctypes.windll.user32.MessageBoxW(None, '启动台出错。请查看 logs/launcher-error.log。', '训练师仿真', 16)
