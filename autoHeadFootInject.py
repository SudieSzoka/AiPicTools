import os
import re
import shutil

# 配置路径
ORIGIN_DIR = "toolsOrigin"    # 原始HTML文件目录
OUTPUT_DIR = "tools"          # 输出目录
HEADER_PATH = "header.html"   # 头部模板文件
FOOTER_PATH = "footer.html"   # 脚部模板文件
COMMON_CSS_PATH = "common.css" # 公共样式文件
THEMES_DIR = "themes"         # 主题目录

def inject_templates(theme="default", add_css=True, add_favicon=True, add_password_protection=False):
    """
    从源目录读取HTML文件，注入模板后保存到输出目录
    
    参数:
    theme: 使用的主题名称 (default, dark, minimal 等)
    add_css: 是否自动添加公共CSS链接
    add_favicon: 是否自动添加favicon链接
    add_password_protection: 是否添加密码保护功能
    """
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 读取模板文件
    with open(HEADER_PATH, 'r', encoding='utf-8') as f:
        header_content = f.read().strip()
    with open(FOOTER_PATH, 'r', encoding='utf-8') as f:
        footer_content = f.read().strip()
    
    # 为模板添加主题类名
    header_content = header_content.replace('<header>', f'<header class="common-header theme-{theme}">', 1)
    footer_content = footer_content.replace('<footer>', f'<footer class="common-footer theme-{theme}">', 1)
    
    # 处理所有HTML文件
    processed_count = 0
    for filename in os.listdir(ORIGIN_DIR):
        if not filename.lower().endswith(('.html', '.htm')):
            continue
            
        input_path = os.path.join(ORIGIN_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # 读取文件内容
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除旧模板标记（如果存在）
        content = re.sub(r'<!--\s*COMMON_HEADER\s*-->.*?<!--\s*END_COMMON_HEADER\s*-->', 
                        '', content, flags=re.DOTALL)
        content = re.sub(r'<!--\s*COMMON_FOOTER\s*-->.*?<!--\s*END_COMMON_FOOTER\s*-->', 
                        '', content, flags=re.DOTALL)
        
        # 注入新模板
        header_injection = f"<!-- COMMON_HEADER -->\n{header_content}\n<!-- END_COMMON_HEADER -->"
        footer_injection = f"<!-- COMMON_FOOTER -->\n{footer_content}\n<!-- END_COMMON_FOOTER -->"
        
        # 在<body>标签后注入头部
        body_match = re.search(r'(<body[^>]*>)', content, re.IGNORECASE)
        if body_match:
            content = content.replace(
                body_match.group(0), 
                body_match.group(0) + '\n' + header_injection
            )
        else:
            # 如果没有<body>标签，在开头注入
            content = header_injection + '\n' + content
        
        # 在</body>标签前注入脚部
        body_close_match = re.search(r'(</body>)', content, re.IGNORECASE)
        if body_close_match:
            content = content.replace(
                body_close_match.group(0), 
                footer_injection + '\n' + body_close_match.group(0)
            )
        else:
            # 如果没有</body>标签，在结尾注入
            content = content + '\n' + footer_injection
        
        # 添加公共CSS链接
        if add_css:
            head_match = re.search(r'(<head[^>]*>)', content, re.IGNORECASE)
            if head_match:
                css_link = f'\n  <link rel="stylesheet" href="styles/common.css">'
                css_link += f'\n  <link rel="stylesheet" href="themes/{theme}.css">'
                content = content.replace(
                    head_match.group(0), 
                    head_match.group(0) + css_link
                )
        
        # 添加favicon链接
        if add_favicon:
            head_match = re.search(r'(<head[^>]*>)', content, re.IGNORECASE)
            if head_match:
                favicon_link = '\n  <link rel="icon" type="image/png" href="/icon/aipictools.png">'
                content = content.replace(
                    head_match.group(0), 
                    head_match.group(0) + favicon_link
                )
        
        # 添加密码保护功能
        if add_password_protection:
            # 在head中添加密码验证脚本
            head_match = re.search(r'(<head[^>]*>)', content, re.IGNORECASE)
            if head_match:
                password_script = '\n  <script src="/password-check.js"></script>'
                content = content.replace(
                    head_match.group(0), 
                    head_match.group(0) + password_script
                )
            
            # 包装body内容到websiteContent div中
            body_match = re.search(r'(<body[^>]*>)(.*?)(</body>)', content, re.IGNORECASE | re.DOTALL)
            if body_match:
                body_open = body_match.group(1)
                body_content = body_match.group(2)
                body_close = body_match.group(3)
                
                # 包装内容到websiteContent div
                wrapped_content = f'{body_open}\n  <div id="websiteContent" style="display: none;">\n{body_content}\n  </div>\n{body_close}'
                content = content.replace(body_match.group(0), wrapped_content)
        
        # 保存到输出目录
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已处理: {filename} (主题: {theme})" + (" [密码保护已启用]" if add_password_protection else ""))
        processed_count += 1
    
    # 复制公共资源
    copy_common_resources()
    
    return processed_count

def copy_common_resources():
    """复制公共资源文件到输出目录"""
    # 创建必要的目录结构
    os.makedirs(os.path.join(OUTPUT_DIR, "styles"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "themes"), exist_ok=True)
    
    # 复制公共CSS
    if os.path.exists(COMMON_CSS_PATH):
        shutil.copy2(COMMON_CSS_PATH, os.path.join(OUTPUT_DIR, "styles", "common.css"))
        print("已复制: 公共样式文件")
    
    # 复制主题文件
    if os.path.exists(THEMES_DIR):
        for theme_file in os.listdir(THEMES_DIR):
            if theme_file.endswith('.css'):
                shutil.copy2(
                    os.path.join(THEMES_DIR, theme_file),
                    os.path.join(OUTPUT_DIR, "themes", theme_file)
                )
                print(f"已复制: 主题文件 {theme_file}")
    

def create_theme(theme_name, primary_color="#3498db", secondary_color="#2ecc71"):
    """创建新主题文件"""
    theme_path = os.path.join(THEMES_DIR, f"{theme_name}.css")
    os.makedirs(THEMES_DIR, exist_ok=True)
    
    theme_css = f"""/* {theme_name} 主题 */
.theme-{theme_name} .common-header {{
    background-color: {primary_color};
    color: white;
}}

.theme-{theme_name} .common-footer {{
    background-color: #2c3e50;
    color: #ecf0f1;
}}

.theme-{theme_name} .common-nav a {{
    color: white;
    border-bottom: 2px solid {secondary_color};
}}

.theme-{theme_name} .common-nav a:hover {{
    background-color: {secondary_color};
}}
"""
    
    with open(theme_path, 'w', encoding='utf-8') as f:
        f.write(theme_css)
    
    print(f"已创建主题: {theme_name}.css")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='HTML模板注入工具')
    parser.add_argument('--theme', default='default', help='使用的主题名称')
    parser.add_argument('--no-css', action='store_true', help='不添加CSS链接')
    parser.add_argument('--no-favicon', action='store_true', help='不添加favicon链接')
    parser.add_argument('--create-theme', help='创建新主题，格式: 主题名,主色,辅色')
    parser.add_argument('--password-protection', action='store_true', help='为工具页面添加密码保护功能')
    
    args = parser.parse_args()
    
    if args.create_theme:
        theme_params = args.create_theme.split(',')
        theme_name = theme_params[0]
        primary = theme_params[1] if len(theme_params) > 1 else "#3498db"
        secondary = theme_params[2] if len(theme_params) > 2 else "#2ecc71"
        create_theme(theme_name, primary, secondary)
        exit()
    
    print("开始处理HTML文件...")
    processed = inject_templates(
        theme=args.theme, 
        add_css=not args.no_css, 
        add_favicon=not args.no_favicon,
        add_password_protection= False
    )
    print(f"\n操作完成! 已处理 {processed} 个HTML文件。")
    print(f"源目录: {ORIGIN_DIR} → 输出目录: {OUTPUT_DIR}")
    print(f"使用主题: {args.theme}")
    if args.password_protection:
        print("密码保护功能已启用")