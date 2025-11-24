import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import tkinter.font as tkfont
import os
import sys

# 解决模块导入问题
sys.path.append(os.path.dirname(__file__))
from generator import CopybookGenerator

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("汉字字帖生成器 v2.2 - 多页版")
        self.root.minsize(1000, 850)
        self.root.geometry("1100x920")
        
        self.generator = CopybookGenerator()
        
        # --- 路径处理 ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        resource_dir = os.path.join(project_root, 'resources')
        
        default_font = os.path.join(resource_dir, 'simkai.ttf')
        if not os.path.exists(default_font):
            default_font = ""
        
        # --- 变量初始化 ---
        self.font_path = tk.StringVar(value=default_font)
        self.paper_size = tk.StringVar(value="A4")
        self.grid_style = tk.StringVar(value="米字格")
        
        self.hand_mode = tk.StringVar(value="右手 (从左向右)")
        self.practice_mode = tk.StringVar(value="笔顺分解") 
        self.align_mode = tk.StringVar(value="顶部")
        self.grid_size_str = tk.StringVar(value="自动 (填满版面)")
        
        self.fill_page = tk.BooleanVar(value=True)
        self.stroke_rest_mode = tk.StringVar(value="剩余描红") 

        # 新增变量
        self.page_mode = tk.StringVar(value="单页模式") # 单页 / 多页
        self.title_display_mode = tk.StringVar(value="每页显示") # 每页显示 / 仅首页

        self.color_combo_val = tk.StringVar(value="粉色")
        self.custom_rows = tk.IntVar(value=10)
        self.custom_cols = tk.IntVar(value=12)
        self.has_title = tk.BooleanVar(value=True)
        self.custom_size_val = tk.DoubleVar(value=1.2)
        
        self.ui_scale = tk.DoubleVar(value=1.0)
        
        self.base_font_size = 10
        self.text_font_size = 12
        
        self.create_widgets()
        self.on_paper_change(None)
        self.update_ui_scale(1.0)
        self.on_size_change(None)
        self.on_mode_change(None) 
        self.on_page_mode_change()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # ================== 顶部缩放 ==================
        frame_scale = tk.Frame(main_frame)
        frame_scale.pack(fill="x", pady=(0, 15))
        tk.Label(frame_scale, text="界面缩放:").pack(side="left")
        scale_slider = tk.Scale(frame_scale, from_=0.8, to=2.0, resolution=0.1, 
                                orient="horizontal", length=200, variable=self.ui_scale, 
                                command=self.update_ui_scale)
        scale_slider.set(1.0)
        scale_slider.pack(side="left", padx=10)

        # ================== 基础设置 ==================
        frame_basic = tk.LabelFrame(main_frame, text="基础布局设置", padx=15, pady=15)
        frame_basic.pack(fill="x", pady=(0, 15))
        
        tk.Label(frame_basic, text="纸张尺寸:").grid(row=0, column=0, sticky="w")
        self.combo_paper = ttk.Combobox(frame_basic, textvariable=self.paper_size, 
                                        values=["A4", "A5", "自定义"], width=10, state="readonly")
        self.combo_paper.grid(row=0, column=1, padx=5, sticky="w")
        self.combo_paper.bind("<<ComboboxSelected>>", self.on_paper_change)
        
        self.lbl_grid_hint = tk.Label(frame_basic, text="", fg="gray", width=16, anchor="w")
        self.lbl_grid_hint.grid(row=0, column=2, padx=5)

        self.frame_custom_input = tk.Frame(frame_basic)
        self.frame_custom_input.grid(row=0, column=3, columnspan=4, sticky="w", padx=10)
        tk.Label(self.frame_custom_input, text="行数:").pack(side="left")
        self.spin_rows = tk.Spinbox(self.frame_custom_input, from_=1, to=50, textvariable=self.custom_rows, width=4)
        self.spin_rows.pack(side="left", padx=(0, 10))
        tk.Label(self.frame_custom_input, text="列数:").pack(side="left")
        self.spin_cols = tk.Spinbox(self.frame_custom_input, from_=1, to=50, textvariable=self.custom_cols, width=4)
        self.spin_cols.pack(side="left")

        tk.Label(frame_basic, text="书写模式:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        hand_opts = ["左手 (从右向左)", "右手 (从左向右)"]
        ttk.Combobox(frame_basic, textvariable=self.hand_mode, values=hand_opts, width=18, state="readonly").grid(row=1, column=1, columnspan=2, padx=5, pady=(10, 0), sticky="w")
        
        tk.Label(frame_basic, text="字体路径:").grid(row=1, column=3, sticky="e", pady=(10, 0), padx=(20, 5))
        tk.Entry(frame_basic, textvariable=self.font_path, width=25).grid(row=1, column=4, pady=(10, 0), sticky="w")
        tk.Button(frame_basic, text="浏览", command=self.browse_font, width=6).grid(row=1, column=5, pady=(10, 0), padx=5)

        # ================== 样式外观 ==================
        frame_style = tk.LabelFrame(main_frame, text="样式外观设置", padx=15, pady=15)
        frame_style.pack(fill="x", pady=(0, 15))
        
        f_size = tk.Frame(frame_style)
        f_size.pack(fill="x", pady=(0, 10))
        tk.Label(f_size, text="格子大小:").pack(side="left")
        size_opts = ["自动 (填满版面)", "1.0 cm", "1.2 cm", "1.5 cm", "1.8 cm", "2.0 cm", "自定义"]
        self.combo_size = ttk.Combobox(f_size, textvariable=self.grid_size_str, values=size_opts, width=16, state="readonly")
        self.combo_size.pack(side="left", padx=(5, 10))
        self.combo_size.bind("<<ComboboxSelected>>", self.on_size_change)
        
        tk.Label(f_size, text="数值 (cm):").pack(side="left")
        self.entry_custom_size = tk.Entry(f_size, textvariable=self.custom_size_val, width=6)
        self.entry_custom_size.pack(side="left", padx=5)
        self.lbl_size_tip = tk.Label(f_size, text="(固定大小不缩放)", fg="gray")
        self.lbl_size_tip.pack(side="left", padx=5)

        f_style_opts = tk.Frame(frame_style)
        f_style_opts.pack(fill="x")
        
        tk.Label(f_style_opts, text="类型:").pack(side="left")
        ttk.Combobox(f_style_opts, textvariable=self.grid_style, values=["米字格", "田字格", "口字格"], width=8, state="readonly").pack(side="left", padx=(5, 15))
        
        tk.Label(f_style_opts, text="颜色:").pack(side="left")
        ttk.Combobox(f_style_opts, textvariable=self.color_combo_val, values=["粉色", "红色", "灰色", "黑色"], width=6, state="readonly").pack(side="left", padx=(5, 15))
        
        tk.Label(f_style_opts, text="模式:").pack(side="left")
        self.combo_mode = ttk.Combobox(f_style_opts, textvariable=self.practice_mode, values=["全描红", "一半描红", "临摹", "笔顺分解"], width=10, state="readonly")
        self.combo_mode.pack(side="left", padx=(5, 10))
        self.combo_mode.bind("<<ComboboxSelected>>", self.on_mode_change)

        self.frame_stroke_opt = tk.Frame(f_style_opts)
        self.frame_stroke_opt.pack(side="left", padx=(0, 10))
        tk.Label(self.frame_stroke_opt, text="填充:").pack(side="left")
        ttk.Combobox(self.frame_stroke_opt, textvariable=self.stroke_rest_mode, values=["剩余描红", "剩余留空"], width=8, state="readonly").pack(side="left", padx=5)
        
        # 移除了原来的“自动循环填满”CheckBox，改用分页模式控制

        # ================== 内容输入 ==================
        tk.Label(main_frame, text="输入汉字内容:").pack(anchor="w", pady=(0, 5))
        self.text_input = scrolledtext.ScrolledText(main_frame, height=8)
        self.text_input.pack(fill="both", expand=True)
        self.text_input.insert(tk.END, "我爱你中国\n#\n饕餮盛宴")
        
        # 新增：输入提示
        lbl_hint = tk.Label(main_frame, text="提示：输入 # 号可强制让本行留空（跳过一行）", fg="#007AFF", anchor="w")
        lbl_hint.pack(fill="x", pady=(2, 5))

        # ================== 底部 (分页与输出) ==================
        frame_bot = tk.LabelFrame(main_frame, text="输出与版式", padx=15, pady=10)
        frame_bot.pack(fill="x", pady=10)
        
        # 第一排：分页设置
        f_page_set = tk.Frame(frame_bot)
        f_page_set.pack(fill="x", pady=(0, 5))
        
        tk.Label(f_page_set, text="分页设置:").pack(side="left")
        ttk.Radiobutton(f_page_set, text="单页模式", variable=self.page_mode, value="单页模式", command=self.on_page_mode_change).pack(side="left", padx=5)
        ttk.Radiobutton(f_page_set, text="多页模式 (自动翻页)", variable=self.page_mode, value="多页模式", command=self.on_page_mode_change).pack(side="left", padx=5)
        
        # 单页模式下才显示的“循环填满”
        self.chk_fill = tk.Checkbutton(f_page_set, text="单页循环填满", variable=self.fill_page)
        self.chk_fill.pack(side="left", padx=(10, 0))
        
        tk.Label(f_page_set, text="|  版面对齐:").pack(side="left", padx=(15, 5))
        ttk.Combobox(f_page_set, textvariable=self.align_mode, values=["居中", "顶部"], width=8, state="readonly").pack(side="left")

        # 第二排：标题与生成
        f_title_gen = tk.Frame(frame_bot)
        f_title_gen.pack(fill="x", pady=(5, 0))
        
        tk.Checkbutton(f_title_gen, text="包含标题", variable=self.has_title, command=self.toggle_title_entry).pack(side="left")
        self.entry_title = tk.Entry(f_title_gen, width=15)
        self.entry_title.insert(0, "汉字练习")
        self.entry_title.pack(side="left", padx=5)
        
        self.frame_title_mode = tk.Frame(f_title_gen)
        self.frame_title_mode.pack(side="left", padx=5)
        tk.Label(self.frame_title_mode, text="显示:").pack(side="left")
        ttk.Combobox(self.frame_title_mode, textvariable=self.title_display_mode, values=["每页显示", "仅首页"], width=8, state="readonly").pack(side="left")
        
        tk.Button(f_title_gen, text="生成 PDF 字帖", command=self.generate, 
                  bg="#007AFF", fg="white", 
                  width=18, height=1, relief="flat").pack(side="right")

    def toggle_title_entry(self):
        state = "normal" if self.has_title.get() else "disabled"
        self.entry_title.config(state=state)
        
    def on_page_mode_change(self):
        mode = self.page_mode.get()
        if mode == "单页模式":
            self.chk_fill.pack(side="left", padx=(10, 0)) # 显示循环填满
            self.frame_title_mode.pack_forget() # 隐藏每页/首页选项
        else:
            self.chk_fill.pack_forget() # 多页不循环，隐藏
            self.frame_title_mode.pack(side="left", padx=5)

    def on_mode_change(self, event):
        if self.practice_mode.get() == "笔顺分解":
            self.frame_stroke_opt.pack(side="left", padx=(0, 10))
        else:
            self.frame_stroke_opt.pack_forget()

    def on_size_change(self, event):
        val = self.grid_size_str.get()
        if val == "自定义":
            self.entry_custom_size.config(state="normal")
            self.lbl_size_tip.config(text="(请输入数值)")
        elif "自动" in val:
            self.entry_custom_size.config(state="disabled")
            self.lbl_size_tip.config(text="(填满可用区域)")
        else:
            try:
                num = float(val.split()[0])
                self.custom_size_val.set(num)
                self.entry_custom_size.config(state="disabled")
                self.lbl_size_tip.config(text="(尺寸固定)")
            except: pass

    def update_ui_scale(self, val):
        scale = float(val)
        new_base_size = int(self.base_font_size * scale)
        new_text_size = int(self.text_font_size * scale)
        
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=new_base_size)
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(size=new_text_size)
        caption_font = tkfont.nametofont("TkCaptionFont")
        caption_font.configure(size=new_base_size, weight="normal")
        
        style = ttk.Style()
        style.configure('.', font=('TkDefaultFont', new_base_size))
        style.configure('TCombobox', font=('TkDefaultFont', new_base_size))
        
        try: self.text_input.configure(font=("SimHei", new_text_size))
        except: pass

    def on_paper_change(self, event):
        choice = self.paper_size.get()
        if choice == "A4":
            self.lbl_grid_hint.config(text="15行 × 12列")
            self.toggle_custom_inputs(False)
        elif choice == "A5":
            self.lbl_grid_hint.config(text="10行 × 8列")
            self.toggle_custom_inputs(False)
        else: 
            self.lbl_grid_hint.config(text="自定义网格")
            self.toggle_custom_inputs(True)

    def toggle_custom_inputs(self, enable):
        state = "normal" if enable else "disabled"
        self.spin_rows.config(state=state)
        self.spin_cols.config(state=state)

    def browse_font(self):
        f = filedialog.askopenfilename(filetypes=[("Font", "*.ttf *.ttc *.otf")])
        if f: self.font_path.set(f)

    def generate(self):
        text = self.text_input.get("1.0", tk.END).strip()
        color_map = {"粉色": "#FFB6C1", "红色": "#FF0000", "灰色": "#A9A9A9", "黑色": "#000000"}
        
        hand_val = self.hand_mode.get()
        hand_code = "right" if "右手" in hand_val else "left"
        
        align_val = self.align_mode.get()
        align_code = "top" if align_val == "顶部" else "center"
        
        rest_val = self.stroke_rest_mode.get()
        rest_code = "trace" if "描红" in rest_val else "empty"
        
        # 分页参数
        is_multipage = (self.page_mode.get() == "多页模式")
        title_every_page = (self.title_display_mode.get() == "每页显示")
        
        size_str = self.grid_size_str.get()
        if "自动" in size_str:
            grid_size_type = "auto"
            grid_size_val = 0
        else:
            grid_size_type = "fixed"
            try: grid_size_val = self.custom_size_val.get()
            except:
                messagebox.showerror("错误", "请输入有效的格子尺寸数值")
                return

        title_content = self.entry_title.get().strip()
        if not title_content: title_content = "汉字练习"

        params = {
            "text": text,
            "font_path": self.font_path.get(),
            "paper_size": self.paper_size.get(),
            "hand_mode": hand_code,
            "grid_style": self.grid_style.get(),
            "grid_color": color_map.get(self.color_combo_val.get(), "#FFB6C1"),
            "practice_mode": self.practice_mode.get(),
            
            # 逻辑修改：单页模式下才允许 fill_page，多页模式下强制 false (顺序写完)
            "fill_page": self.fill_page.get() if not is_multipage else False,
            "is_multipage": is_multipage,
            "title_every_page": title_every_page,
            
            "stroke_rest_mode": rest_code,
            
            "has_title": self.has_title.get(),
            "custom_title": title_content,
            "align_mode": align_code,
            "custom_rows": self.custom_rows.get(),
            "custom_cols": self.custom_cols.get(),
            
            "grid_size_type": grid_size_type,
            "grid_size_val": grid_size_val
        }
        
        default_name = f"字帖_{params['paper_size']}.pdf"
        f = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile=default_name)
        
        if f:
            try:
                params['output_file'] = f
                self.generator.generate_pdf(params)
                messagebox.showinfo("成功", f"文件已保存:\n{f}")
                try: os.startfile(f)
                except: pass
            except Exception as e:
                import traceback
                traceback.print_exc() 
                messagebox.showerror("生成失败", f"错误信息:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    try: 
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    app = App(root)
    root.mainloop()