# 汉字笔顺字帖生成器 (Chinese Calligraphy Generator)
# Chinese Character Stroke Order Practice Sheet Generator

一个基于 Python 的汉字字帖生成工具。支持生成米字格、田字格等多种练习纸，核心特色是支持**汉字笔顺分解**、**智能居中排版**、**支持左撇子**以及**多页 PDF 输出**。
A Python-based Chinese character practice sheet generator. Supports generating various practice papers like grid and square grids, with core features including **Chinese character stroke decomposition**, **intelligent centering layout**, **left-handed support**, and **multi-page PDF output**.

适用于书法练习、儿童识字教学、对外汉语教学等场景。
Suitable for calligraphy practice, children's literacy education, and Chinese language teaching scenarios.

---

## ✨ 核心特性 / Key Features

### 1. 强大的笔顺分解 / Powerful Stroke Order Decomposition

* **SVG 矢量笔顺 / SVG Vector Strokes**：基于 MakeMeHanzi 数据库，提供高质量的笔顺数据
  Based on MakeMeHanzi database, providing high-quality stroke order data

* **智能算法 / Intelligent Algorithms**：
  * **几何重心自动对齐 / Geometric Center Automatic Alignment**：自动计算汉字实际包围盒重心，解决部分汉字（如"饕"）在格子里位置偏下或偏上的问题
    Automatically calculates the actual bounding box center of Chinese characters, solving positioning issues for characters like "饕" that appear too high or low in the grid
  
  * **防溢出保护 / Overflow Protection**：统一缩放比例（0.88），既保证书写饱满，又防止长笔画（撇、捺、钩）戳出格子
    Unified scaling ratio (0.88) ensures full writing while preventing long strokes (horizontal, vertical, hook) from extending beyond the grid

* **逐笔描红 / Stroke-by-Stroke Tracing**：笔顺分解模式下，已写笔画为灰色，未写笔画隐藏，提供纯净的描红体验
  In stroke decomposition mode, completed strokes are gray, uncompleted strokes are hidden, providing a pure tracing experience

### 2. 高度可定制化 / Highly Customizable

* **版式设置 / Layout Settings**：支持 A4、A5 及自定义纸张尺寸；支持自定义行列数
  Supports A4, A5, and custom paper sizes; supports custom rows and columns

* **网格样式 / Grid Styles**：米字格、田字格、口字格；支持自定义颜色（粉、红、灰、黑）
  Grid, square grid, box grid; supports custom colors (pink, red, gray, black)

* **练习模式 / Practice Modes**：
  * **笔顺分解 / Stroke Order Decomposition**：范字 + 逐笔分解 + 剩余格子填充
    Reference character + stroke-by-stroke decomposition + remaining grid filling
  
  * **全描红 / Full Tracing**：所有格子均为浅灰色描红
    All grids are light gray tracing
  
  * **一半描红 / Half Tracing**：前一半描红，后一半留空
    First half tracing, second half blank
  
  * **临摹 / Copying Practice**：仅首字为范字，其余留空
    Only the first character is reference, others are blank

* **左手模式 / Left-Hand Mode**：专为左撇子设计，范字在最右侧，笔顺从右向左排列，防止手部遮挡范字
  Specifically designed for left-handed users, with reference characters on the right and stroke order flowing from right to left, preventing hand obstruction

### 3. 智能排版与输出 / Intelligent Layout and Output

* **多页 PDF 生成 / Multi-page PDF Generation**：支持长文本自动分页，一键生成完整的字帖文件
  Supports automatic pagination for long text, generating complete practice sheet files with one click

* **特殊占位符 / Special Placeholders**：输入 `#` 号可强制跳过当前行（留空），便于制作分割或留白
  Entering `#` can force skip the current line (leave blank), convenient for creating divisions or white space

* **自动换行 / Automatic Line Wrapping**：笔顺分解如果一行写不完，会自动顺延至下一行（支持从左向右和从右向左两种流向）
  If stroke decomposition doesn't fit in one line, it automatically continues to the next line (supporting both left-to-right and right-to-left flows)

---

## 🛠️ 环境依赖 / Environment Dependencies

### 系统要求 / System Requirements
* Python 3.8+
* Windows 操作系统 / Windows Operating System

### Python 库依赖 / Python Library Dependencies
* Matplotlib
* Numpy
* Tkinter（通常随 Python 安装 / Usually comes with Python installation）
* svgpath2mpl

---

## 🚀 快速开始 / Quick Start

### 1. 创建虚拟环境 / Create Virtual Environment

建议使用虚拟环境运行 / Recommend using virtual environment for running:

```bash
# 创建虚拟环境 (Windows) / Create virtual environment (Windows)
python -m venv venv

# 激活虚拟环境 / Activate virtual environment
.\venv\Scripts\activate
```

### 2. 安装依赖库 / Install Dependencies

```bash
# 安装项目依赖 / Install project dependencies
pip install -r requirements.txt
```

### 3. requirements.txt 内容 / requirements.txt Content

```txt
matplotlib>=3.5.0
numpy>=1.21.0
svgpath2mpl
```

### 4. 资源文件准备 / Resource File Preparation

确保项目根目录下有 `resources` 文件夹，并包含以下文件 / Ensure there's a `resources` folder in the project root directory with the following files:

* **strokes.txt**：笔顺数据文件（每行为 JSON 格式）
  Stroke order data file (each line in JSON format)
* **simkai.ttf**：楷体字体文件（或其他支持中文的 TTF 字体），用于显示范字和标题
  Kai style font file (or other Chinese-supported TTF font), used for displaying reference characters and titles

---

## 📖 使用指南 / User Guide

### 界面参数说明 / Interface Parameter Description

#### 基础设置 / Basic Settings
* **纸张 / Paper**：推荐使用 A4 / Recommend using A4
* **书写模式 / Writing Mode**：
  * 右手 / Right-handed：范字在左，从左向右写
    Reference character on the left, write from left to right
  * 左手 / Left-handed：范字在右，从右向左写
    Reference character on the right, write from right to left
* **字体 / Font**：点击浏览选择系统中的 .ttf 字体文件
  Click browse to select system .ttf font files

#### 样式外观 / Style Appearance
* **格子大小 / Grid Size**：推荐"自动"，程序会根据纸张大小和行列数自动计算最大合适的格子
  Recommend "Auto", the program will automatically calculate the most suitable grid size based on paper size and row/column count

* **模式 / Mode**：选择"笔顺分解"可生成带笔画步骤的字帖
  Select "Stroke Order Decomposition" to generate practice sheets with stroke steps

* **填充 / Fill**：在笔顺分解模式下，笔顺写完后，当行剩余格子可选择"剩余描红"或"剩余留空"
  In stroke decomposition mode, after completing stroke order, remaining grids in the line can choose "Remaining Tracing" or "Remaining Blank"

#### 分页设置 / Pagination Settings
* **单页模式 / Single Page Mode**：仅生成一页 PDF，适合生成样张。可勾选"单页循环填满"
  Generate only one PDF, suitable for creating samples. Can check "Single Page Loop Fill"

* **多页模式 / Multi-page Mode**：自动处理长文本，生成多页 PDF
  Automatically handle long text, generate multi-page PDF

### 输入框技巧 / Input Box Tips

#### 普通输入 / Regular Input
直接输入汉字，如 / Direct input of Chinese characters, such as:
```
天地玄黄
```

#### 空行控制 / Empty Line Control
输入 `#` 字符，该行将被留空（不画格子内容）。
Enter `#` character, the line will be left blank (no grid content drawn).

#### 示例输入 / Example Input
```
我爱你中国
#
汉字练习
```

**效果 / Effect**：
* 第一行写"我爱你中国" / First line writes "我爱你中国"
* 第二行留空 / Second line is blank
* 第三行写"汉字练习" / Third line writes "汉字练习"

---

## 📂 项目结构 / Project Structure

```
字帖生成器v1/ / Chinese Calligraphy Generator v1/
├── resources/                     # 资源文件夹 / Resource folder
│   ├── strokes.txt               # 核心笔顺数据 / Core stroke order data
│   └── simkai.ttf                # 默认字体文件 / Default font file
├── src/                          # 源代码目录 / Source code directory
│   ├── main.py                   # GUI 入口与交互逻辑 / GUI entry and interaction logic
│   ├── generator.py              # 核心绘图与排版引擎 / Core drawing and layout engine
│   └── __pycache__/              # Python 缓存目录 / Python cache directory
├── venv/                         # 虚拟环境 / Virtual environment
├── requirements.txt              # 依赖列表 / Dependency list
├── 1.一键配置环境.bat             # Windows 环境配置脚本 / Windows environment setup script
├── 2.启动字帖生成器.bat            # Windows 启动脚本 / Windows startup script
├── launcher_basic.bat            # 基础启动脚本-备用 / Basic startup script - backup
└── README.md                     # 项目说明文档 / Project documentation
```

---

## ⚠️ 常见问题 / FAQ

### Q: 生成的字帖里有些字显示为红色的 "?" / Q: Some characters in generated practice sheets show as red "?"

**A**: 这说明 strokes.txt 数据文件中缺少该字的笔顺数据。程序会尝试用字体文件显示黑色的范字，但无法进行笔顺分解。
**A**: This means the strokes.txt data file lacks stroke order data for this character. The program will attempt to display a black reference character using the font file, but cannot perform stroke order decomposition.

**解决方案 / Solutions**：
1. 检查 strokes.txt 文件是否完整 / Check if strokes.txt file is complete
2. 确认输入的字符是否在笔顺数据库中 / Confirm if input characters are in the stroke order database
3. 联系开发者添加缺失字符的笔顺数据 / Contact developer to add missing character stroke data

### Q: 笔顺分解模式下，字的大小和范字不一样？ / Q: In stroke decomposition mode, character sizes don't match the reference character?

**A**: 我们在最新版本中使用了统一的缩放算法（0.88）和几何重心对齐，理论上笔顺字和描红字的大小、位置应完全一致。如果出现偏差，请检查是否修改了 padding_factor 参数。
**A**: We use unified scaling algorithm (0.88) and geometric center alignment in the latest version. Theoretically, stroke order characters and tracing characters should have identical size and position. If deviations occur, check if the padding_factor parameter was modified.

**解决方案 / Solutions**：
1. 确认使用的是默认的 0.88 缩放比例 / Confirm using default 0.88 scaling ratio
2. 检查几何重心对齐算法是否正常工作 / Check if geometric center alignment algorithm works properly
3. 重新生成字帖，看问题是否依然存在 / Regenerate practice sheet to see if problem persists

---

## 🎯 快速启动 / Quick Launch

### Windows 用户 / Windows Users
直接双击运行以下批处理文件 / Double-click to run the following batch files:

1. **配置环境 / Setup Environment**：`1.一键配置环境.bat`
2. **启动程序 / Launch Program**：`2.启动字帖生成器.bat`

### 手动启动 / Manual Launch
```bash
# 激活虚拟环境 / Activate virtual environment
.\venv\Scripts\activate

# 启动程序 / Launch program
python src/main.py
```

---

## 📞 技术支持 / Technical Support

如果您在使用过程中遇到问题，可以 / If you encounter issues during use:

1. 检查本文档的常见问题部分 / Check the FAQ section of this documentation
2. 确认所有依赖库版本符合要求 / Confirm all dependency library versions meet requirements
3. 验证资源文件路径和完整性 / Verify resource file paths and completeness

**祝您使用愉快！** 🎉 / **Enjoy using it!** 🎉