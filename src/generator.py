import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path
from matplotlib.transforms import Affine2D, Bbox
from matplotlib.backends.backend_pdf import PdfPages
import os
import math
import json
import numpy as np

# 检查依赖
try:
    from svgpath2mpl import parse_path
    HAS_SVG_LIB = True
except ImportError:
    HAS_SVG_LIB = False
    print("提示: 未安装 svgpath2mpl，无法显示笔顺")

# ==========================================
# 模块 1: 笔顺管理器 (保持不变)
# ==========================================
class StrokeManager:
    def __init__(self, resource_dir):
        self.data_path = os.path.join(resource_dir, 'strokes.txt')
        self.char_data = {}
        self.loaded = False
        self.has_lib = HAS_SVG_LIB

    def load_data(self):
        if self.loaded or not self.has_lib: return
        if not os.path.exists(self.data_path): return
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        self.char_data[entry['character']] = entry['strokes']
                    except: continue
            self.loaded = True
        except: pass

    def get_strokes(self, char):
        if not self.loaded: self.load_data()
        return self.char_data.get(char, [])

    def draw_char_strokes(self, ax, char, x, y, size, step_index=None, color='black', guide_color=None):
        if not self.has_lib: return False
        strokes = self.get_strokes(char)
        if not strokes: return False

        parsed_paths = []
        all_verts = []
        for svg_str in strokes:
            p = parse_path(svg_str)
            parsed_paths.append(p)
            if p.vertices is not None and len(p.vertices) > 0:
                all_verts.append(p.vertices)
        
        if all_verts:
            stacked = np.vstack(all_verts)
            min_x, min_y = np.min(stacked, axis=0)
            max_x, max_y = np.max(stacked, axis=0)
            actual_center_x = (min_x + max_x) / 2.0
            actual_center_y = (min_y + max_y) / 2.0
        else:
            actual_center_x = 512.0
            actual_center_y = 512.0

        scale_factor = 0.88 
        src_scale_base = 1024.0
        scale = (size * scale_factor) / src_scale_base
        target_cx = x + size / 2
        target_cy = y + size / 2

        transform = Affine2D().translate(-actual_center_x, -actual_center_y) \
                              .scale(scale, scale) \
                              .translate(target_cx, target_cy)
        
        final_transform = transform + ax.transData
        clip_rect = patches.Rectangle((x, y), size, size, transform=ax.transData)

        for i, path in enumerate(parsed_paths):
            should_draw = False
            fill_color = color
            if step_index is not None:
                if i <= step_index:
                    should_draw = True
                    fill_color = color 
                else:
                    if guide_color is not None:
                        should_draw = True
                        fill_color = guide_color
            else:
                should_draw = True
                fill_color = color
            
            if should_draw:
                patch = patches.PathPatch(path, facecolor=fill_color, edgecolor='none', lw=0, transform=final_transform)
                patch.set_clip_path(clip_rect)
                ax.add_patch(patch)
        return True

# ==========================================
# 模块 2: 字帖生成器 (支持多页与特殊占位符)
# ==========================================
class CopybookGenerator:
    def __init__(self):
        self.DPI = 300
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resource_dir = os.path.join(os.path.dirname(current_dir), 'resources')
        self.stroke_mgr = StrokeManager(resource_dir)

    def get_layout_config(self, params):
        paper_type = params.get('paper_size', 'A4')
        if paper_type == "A5":
            phy_width, phy_height = 5.83, 8.27
            default_cols, default_rows = 8, 10
            title_size = 14
        else: 
            phy_width, phy_height = 8.27, 11.69
            default_cols, default_rows = 12, 15
            title_size = 18

        if paper_type == "自定义":
            try:
                cols = int(params.get('custom_cols', 12))
                rows = int(params.get('custom_rows', 15))
            except: cols, rows = 12, 15
        else:
            cols, rows = default_cols, default_rows

        has_title = params.get('has_title', True)
        title_space = 0.8 if has_title else 0.0
        margin_x, margin_y = 0.4, 0.5 

        return {
            "width": phy_width, "height": phy_height,
            "cols": cols, "rows": rows,
            "margin_x": margin_x, "margin_y": margin_y,
            "title_space": title_space, "title_size": title_size,
            "has_title": has_title
        }

    def generate_pdf(self, params):
        config = self.get_layout_config(params)
        is_stroke_mode = (params.get('practice_mode') == "笔顺分解")
        if is_stroke_mode: self.stroke_mgr.load_data()

        # --- 文本预处理 ---
        # 将输入文本转换为字符队列
        # 清除换行符，保留 # 作为空行标记
        raw_text = params['text'].replace('\r', '').replace('\n', '')
        
        # 核心：构建处理队列
        # 队列中的元素要么是普通字符，要么是 '#'
        text_queue = list(raw_text)
        
        # 如果是单页模式且要求填满，且没字了，需要预先扩充队列
        if not params['is_multipage'] and params['fill_page'] and raw_text:
            # 简单处理：如果没 # 号，直接乘；如果有 # 号，逻辑比较复杂
            # 为了兼容性，这里仅当无特殊格式时重复。
            # 如果有 # 号，通常意味着用户想精确控制布局，不建议自动循环。
            if '#' not in raw_text:
                 repeat_count = math.ceil(config['rows'] / len(raw_text))
                 text_queue = list(raw_text * repeat_count)

        # 打开 PDF 多页上下文
        with PdfPages(params['output_file']) as pdf:
            page_num = 1
            
            # 只要队列还有内容，或者至少要生成一页
            while True:
                # ================= 计算本页布局 =================
                rows, cols = config['rows'], config['cols']
                grid_map = [[None for _ in range(cols)] for _ in range(rows)]
                
                curr_row = 0
                
                # 填充当前页
                while curr_row < rows and text_queue:
                    char = text_queue[0] # 预览下一个字符
                    
                    # --- 情况 1: 空行占位符 # ---
                    if char == '#':
                        text_queue.pop(0) # 消耗掉
                        curr_row += 1     # 跳过这一行
                        continue
                    
                    # --- 情况 2: 笔顺分解模式 ---
                    if is_stroke_mode:
                        hand_mode = params['hand_mode']
                        fill_rest = params.get('stroke_rest_mode', 'trace')
                        strokes = self.stroke_mgr.get_strokes(char)
                        total_strokes = len(strokes) if strokes else 1
                        
                        # 预计算需要的行数 (粗略估计，只为多页逻辑服务)
                        # 精确计算比较复杂，这里采用“试探性填充”逻辑
                        # 如果这个字需要跨行，且当前页剩下行数不足以写完它的大部分？
                        # 简化策略：只要当前行是可用的，就开始写。写不完就换页的逻辑由下面的 grid_map 填充控制
                        
                        # 消耗字符
                        text_queue.pop(0)
                        
                        # 确定方向
                        if hand_mode == 'right':
                            tpl_col, direction = 0, 1
                        else:
                            tpl_col, direction = cols - 1, -1
                            
                        # 放置范字
                        grid_map[curr_row][tpl_col] = {'type': 'template', 'char': char}
                        
                        # 游标
                        curr_write_r = curr_row
                        curr_write_c = tpl_col + direction
                        
                        steps_done = 0
                        
                        # 笔顺填充循环
                        stroke_finished_on_this_page = True
                        
                        while steps_done < total_strokes:
                            # 换行/越界检测
                            need_wrap = False
                            if hand_mode == 'right' and curr_write_c >= cols: need_wrap = True
                            if hand_mode == 'left' and curr_write_c < 0: need_wrap = True
                            
                            if need_wrap:
                                curr_write_r += 1
                                curr_write_c = 0 if hand_mode == 'right' else (cols - 1)
                            
                            # 如果写着写着，超出了当前页的行数
                            if curr_write_r >= rows:
                                # 这里的处理比较棘手。如果一个字跨页了，这在字帖里通常是不被接受的。
                                # 理想情况：如果当前页写不下这个字，就应该回滚，把这个字放到下一页。
                                # 但为了代码简洁，且考虑到“跨页笔顺”极少见（除非字特别复杂且到了页尾），
                                # 这里我们选择：截断。剩下的笔画不显示了（因为下一页会重头开始新字）。
                                # 或者，如果这是该字的“刚开始”就跨页了，说明上一行刚结束，这一行不够写。
                                # 改进：如果 text_queue 还有很多，可以接受截断。
                                stroke_finished_on_this_page = False
                                break 
                            
                            grid_map[curr_write_r][curr_write_c] = {'type': 'step', 'char': char, 'step': steps_done}
                            curr_write_c += direction
                            steps_done += 1
                        
                        # 填充剩余
                        if stroke_finished_on_this_page and curr_write_r < rows:
                            while 0 <= curr_write_c < cols:
                                grid_map[curr_write_r][curr_write_c] = {'type': fill_rest, 'char': char}
                                curr_write_c += direction
                        
                        # 更新大循环的行索引
                        curr_row = curr_write_r + 1
                    
                    # --- 情况 3: 普通练习模式 ---
                    else:
                        text_queue.pop(0) # 消耗
                        
                        if params['hand_mode'] == 'left':
                            tpl_col = cols - 1
                            practice_range = range(cols - 2, -1, -1)
                        else:
                            tpl_col = 0
                            practice_range = range(1, cols)
                        
                        # 范字
                        grid_map[curr_row][tpl_col] = {'type': 'template', 'char': char}
                        
                        # 练习格
                        for c in practice_range:
                            p_mode = params['practice_mode']
                            is_trace = True
                            dist = abs(c - tpl_col) - 1
                            if p_mode == "一半描红" and dist >= (cols-1)//2: is_trace = False
                            if p_mode == "临摹": is_trace = False
                            
                            grid_map[curr_row][c] = {'type': 'trace' if is_trace else 'empty', 'char': char}
                        
                        curr_row += 1

                # ================= 开始绘图 (生成单页) =================
                fig = self._render_page(config, params, grid_map, page_num)
                pdf.savefig(fig, bbox_inches='tight', pad_inches=0)
                plt.close(fig)
                
                page_num += 1
                
                # 退出条件
                if not text_queue:
                    break
                # 保护：如果是单页模式，强制退出（只生成一页，多余截断）
                if not params['is_multipage']:
                    break

    def _render_page(self, config, params, grid_map, page_num):
        """
        渲染单页内容的辅助函数
        """
        # 重新计算可用区域
        top_limit = config['height'] - config['margin_y'] - config['title_space']
        bottom_limit = config['margin_y'] + 0.3
        available_h = top_limit - bottom_limit
        available_w = config['width'] - (2 * config['margin_x'])
        
        # 格子大小计算
        size_type = params.get('grid_size_type', 'auto')
        if size_type == 'fixed':
            try: cell_size = float(params.get('grid_size_val')) / 2.54
            except: cell_size = 1.5 / 2.54
        else:
            cell_w = available_w / config['cols']
            cell_h = available_h / config['rows']
            cell_size = min(cell_w, cell_h)

        real_grid_width = cell_size * config['cols']
        real_grid_height = cell_size * config['rows']
        actual_margin_x = (config['width'] - real_grid_width) / 2
        
        # 对齐
        align_mode = params.get('align_mode', 'center')
        if align_mode == 'top': start_y = top_limit - real_grid_height
        else: start_y = bottom_limit + (available_h - real_grid_height) / 2
        if start_y < bottom_limit: start_y = top_limit - real_grid_height

        # 初始化绘图
        plt.rcParams['font.sans-serif'] = ['SimHei'] 
        fig, ax = plt.subplots(figsize=(config['width'], config['height']), dpi=self.DPI)
        ax.axis('off')
        ax.set_xlim(0, config['width'])
        ax.set_ylim(0, config['height'])

        try:
            if params.get('font_path') and os.path.exists(params['font_path']):
                my_font = FontProperties(fname=params['font_path'])
            else: my_font = FontProperties(family='sans-serif')
        except: my_font = FontProperties(family='sans-serif')

        TRACE_COLOR = '#D3D3D3'
        rows, cols = config['rows'], config['cols']

        for r in range(rows):
            y = start_y + (rows - 1 - r) * cell_size
            for c in range(cols):
                x = actual_margin_x + c * cell_size
                
                # 背景
                rect = patches.Rectangle((x, y), cell_size, cell_size, linewidth=0.8, 
                                       edgecolor=params['grid_color'], facecolor='none')
                ax.add_patch(rect)
                
                cx, cy = x + cell_size/2, y + cell_size/2
                style = {'color': params['grid_color'], 'linestyle': ':', 'linewidth': 0.5, 'alpha': 0.6}
                if params['grid_style'] in ["米字格", "田字格"]:
                    ax.plot([x, x+cell_size], [cy, cy], **style)
                    ax.plot([cx, cx], [y, y+cell_size], **style)
                if params['grid_style'] == "米字格":
                    ax.plot([x, x+cell_size], [y, y+cell_size], **style)
                    ax.plot([x, x+cell_size], [y+cell_size, y], **style)

                cell_data = grid_map[r][c]
                if not cell_data: continue
                
                ctype = cell_data['type']
                char = cell_data.get('char', '')
                fontsize = (cell_size * 0.8) * 72
                
                # 绘图逻辑
                is_stroke_mode = (params.get('practice_mode') == "笔顺分解")
                
                if ctype == 'template':
                    success = False
                    if is_stroke_mode: 
                        success = self.stroke_mgr.draw_char_strokes(ax, char, x, y, cell_size, color='black')
                    if not success:
                        ax.text(cx, cy - cell_size*0.05, char, fontproperties=my_font, 
                                fontsize=fontsize, ha='center', va='center', color='black')
                
                elif ctype == 'step':
                    success = self.stroke_mgr.draw_char_strokes(ax, char, x, y, cell_size, 
                                                                step_index=cell_data['step'], 
                                                                color=TRACE_COLOR, guide_color=None)
                    if not success:
                        ax.text(cx, cy, "?", color='red', ha='center', va='center') 

                elif ctype == 'trace':
                    success = False
                    if is_stroke_mode:
                        success = self.stroke_mgr.draw_char_strokes(ax, char, x, y, cell_size, 
                                                                    step_index=None, color=TRACE_COLOR)
                    if not success:
                        ax.text(cx, cy - cell_size*0.05, char, fontproperties=my_font, 
                                fontsize=fontsize, ha='center', va='center', color=TRACE_COLOR)

        # 标题绘制逻辑
        should_draw_title = False
        if config['has_title']:
            if params['is_multipage']:
                if params['title_every_page']: should_draw_title = True
                elif page_num == 1: should_draw_title = True
            else:
                should_draw_title = True

        if should_draw_title:
            title = params['custom_title'] if params['custom_title'] else "标题"
            title_y = config['height'] - config['margin_y'] - (config['title_space'] / 2) + 0.1
            plt.text(config['width']/2, title_y, title, fontproperties=my_font, fontsize=config['title_size'], ha='center', va='center')
        
        # 页脚
        if size_type == 'fixed': size_str = f"{params.get('grid_size_val')}cm"
        else: size_str = f"约{cell_size * 2.54:.1f}cm"
        grid_info = f"{config['rows']}行×{config['cols']}列 ({size_str}/格)"
        
        # 多页页码
        page_info = f" - 第 {page_num} 页" if params['is_multipage'] else ""
        note = f"字帖生成器{page_info} - {grid_info}"
        plt.text(config['width']/2, 0.3, note, fontproperties=my_font, fontsize=10, ha='center', va='center', color='gray')

        return fig