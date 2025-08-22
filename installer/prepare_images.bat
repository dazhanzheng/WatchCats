@echo off
REM 准备安装向导所需的图片资源
REM Prepare image resources for installer wizard

echo ==========================================
echo 准备安装向导图片资源
echo Preparing Installer Wizard Images
echo ==========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到 Python！
    echo Error: Python not found!
    echo 请先安装 Python 3.9 或更高版本。
    echo Please install Python 3.9 or higher.
    pause
    exit /b 1
)

echo 创建安装向导图片生成脚本...
echo Creating installer image generation script...

REM 创建 Python 脚本来生成图片
echo import os > generate_installer_images.py
echo from PIL import Image, ImageDraw, ImageFont >> generate_installer_images.py
echo. >> generate_installer_images.py
echo # 创建安装向导大图 (164x314 像素) >> generate_installer_images.py
echo wizard_img = Image.new('RGB', (164, 314), color='#2C2C2C') >> generate_installer_images.py
echo draw = ImageDraw.Draw(wizard_img) >> generate_installer_images.py
echo. >> generate_installer_images.py
echo # 绘制渐变背景 >> generate_installer_images.py
echo for i in range(314): >> generate_installer_images.py
echo     color_value = int(44 + (i / 314) * 30) >> generate_installer_images.py
echo     draw.rectangle([(0, i), (164, i+1)], fill=(color_value, color_value, color_value+5)) >> generate_installer_images.py
echo. >> generate_installer_images.py
echo # 添加猫咪剪影 >> generate_installer_images.py
echo cat_color = (255, 200, 0) >> generate_installer_images.py
echo # 头部 >> generate_installer_images.py
echo draw.ellipse([(52, 100), (112, 160)], fill=cat_color) >> generate_installer_images.py
echo # 耳朵 >> generate_installer_images.py
echo draw.polygon([(55, 120), (45, 90), (65, 110)], fill=cat_color) >> generate_installer_images.py
echo draw.polygon([(109, 120), (119, 90), (99, 110)], fill=cat_color) >> generate_installer_images.py
echo # 眼睛 >> generate_installer_images.py
echo draw.ellipse([(65, 120), (75, 130)], fill=(255, 255, 255)) >> generate_installer_images.py
echo draw.ellipse([(89, 120), (99, 130)], fill=(255, 255, 255)) >> generate_installer_images.py
echo draw.ellipse([(68, 123), (72, 127)], fill=(0, 0, 0)) >> generate_installer_images.py
echo draw.ellipse([(92, 123), (96, 127)], fill=(0, 0, 0)) >> generate_installer_images.py
echo. >> generate_installer_images.py
echo # 添加文字 >> generate_installer_images.py
echo try: >> generate_installer_images.py
echo     from PIL import ImageFont >> generate_installer_images.py
echo     font = ImageFont.truetype("arial.ttf", 14) >> generate_installer_images.py
echo except: >> generate_installer_images.py
echo     font = ImageFont.load_default() >> generate_installer_images.py
echo. >> generate_installer_images.py
echo text = "Baal Pet" >> generate_installer_images.py
echo text_bbox = draw.textbbox((0, 0), text, font=font) >> generate_installer_images.py
echo text_width = text_bbox[2] - text_bbox[0] >> generate_installer_images.py
echo text_x = (164 - text_width) // 2 >> generate_installer_images.py
echo draw.text((text_x, 200), text, fill=(255, 255, 255), font=font) >> generate_installer_images.py
echo. >> generate_installer_images.py
echo text2 = "Assistant" >> generate_installer_images.py
echo text2_bbox = draw.textbbox((0, 0), text2, font=font) >> generate_installer_images.py
echo text2_width = text2_bbox[2] - text2_bbox[0] >> generate_installer_images.py
echo text2_x = (164 - text2_width) // 2 >> generate_installer_images.py
echo draw.text((text2_x, 220), text2, fill=(255, 255, 255), font=font) >> generate_installer_images.py
echo. >> generate_installer_images.py
echo wizard_img.save('installer_wizard.bmp') >> generate_installer_images.py
echo print('Created installer_wizard.bmp') >> generate_installer_images.py
echo. >> generate_installer_images.py
echo # 创建安装向导小图 (55x58 像素) >> generate_installer_images.py
echo small_img = Image.new('RGB', (55, 58), color='#2C2C2C') >> generate_installer_images.py
echo draw_small = ImageDraw.Draw(small_img) >> generate_installer_images.py
echo. >> generate_installer_images.py
echo # 绘制小猫咪图标 >> generate_installer_images.py
echo draw_small.ellipse([(10, 10), (45, 45)], fill=cat_color) >> generate_installer_images.py
echo # 耳朵 >> generate_installer_images.py
echo draw_small.polygon([(15, 20), (10, 5), (20, 15)], fill=cat_color) >> generate_installer_images.py
echo draw_small.polygon([(40, 20), (45, 5), (35, 15)], fill=cat_color) >> generate_installer_images.py
echo # 眼睛 >> generate_installer_images.py
echo draw_small.ellipse([(20, 22), (24, 26)], fill=(0, 0, 0)) >> generate_installer_images.py
echo draw_small.ellipse([(31, 22), (35, 26)], fill=(0, 0, 0)) >> generate_installer_images.py
echo. >> generate_installer_images.py
echo small_img.save('installer_small.bmp') >> generate_installer_images.py
echo print('Created installer_small.bmp') >> generate_installer_images.py

echo.
echo 正在生成图片...
echo Generating images...

REM 安装 Pillow 如果需要
pip show pillow >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装 Pillow 库...
    echo Installing Pillow library...
    pip install pillow
)

REM 运行 Python 脚本
python generate_installer_images.py

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo 图片生成成功！
    echo Images generated successfully!
    echo ==========================================
    echo.
    echo 生成的文件 Generated files:
    echo   - installer_wizard.bmp (164x314)
    echo   - installer_small.bmp (55x58)
    echo.
    
    REM 清理临时脚本
    del /f /q generate_installer_images.py
) else (
    echo.
    echo ==========================================
    echo 错误：图片生成失败！
    echo Error: Failed to generate images!
    echo ==========================================
    echo.
)

pause