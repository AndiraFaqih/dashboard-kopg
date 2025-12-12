import re
import os

# Color palette - Merah dan Putih
colors = {
    'primary': '#c41e3a',           # Merah cerah
    'primary-dark': '#8b0000',       # Merah gelap (Dark Red)
    'primary-light': '#e74c3c',      # Merah terang (Light Red)
    'primary-lightest': '#fadbd8',   # Merah super terang
    'accent': '#ff6b6b',             # Merah accent
    'light-bg': '#ffffff',           # Putih background
    'card-bg': '#f8f9fa',            # Abu-abu sangat terang (almost white)
    'text-dark': '#1a1a1a',          # Teks gelap
    'text-light': '#666666',         # Teks abu-abu
    'border-color': '#e0e0e0',       # Border terang
}

templates = [
    "dashboard_main.html",
    "dashboard_perbankan.html",
    "dashboard_asuransi.html",
    "dashboard_komoditas.html",
    "dashboard_dana_pensiun.html",
    "dashboard_nonbank.html",
    "input_data.html",
]

base_path = "/Users/960072/Downloads/dashboard_keuangan 3/templates/"

def update_css_variables(content):
    """Update CSS color variables"""
    css_var_pattern = r'--primary:\s*#[0-9a-fA-F]{6}|--primary-dark:\s*#[0-9a-fA-F]{6}|--primary-light:\s*#[0-9a-fA-F]{6}|--primary-lightest:\s*#[0-9a-fA-F]{6}|--accent:\s*#[0-9a-fA-F]{6}|--light-bg:\s*#[0-9a-fA-F]{6}|--card-bg:\s*#[0-9a-fA-F]{6}|--text-dark:\s*#[0-9a-fA-F]{6}|--text-light:\s*#[0-9a-fA-F]{6}|--border-color:\s*#[0-9a-fA-F]{6}'
    
    # Replace existing variables
    for key, value in colors.items():
        pattern = f'--{key}:\\s*#[0-9a-fA-F]{{6}}'
        content = re.sub(pattern, f'--{key}: {value}', content, flags=re.IGNORECASE)
    
    return content

def update_inline_colors(content):
    """Update inline colors and class references"""
    # Update old color references
    replacements = [
        # Old primary color references
        ('#994038', colors['primary']),
        ('#a94534', colors['primary']),
        ('#7a3229', colors['primary-dark']),
        ('#e8b4b0', colors['primary-light']),
        ('#f5f1ef', colors['light-bg']),
        
        # Ensure gradient sidebar uses new colors
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
        # Case insensitive
        content = re.sub(f'{re.escape(old)}', new, content, flags=re.IGNORECASE)
    
    return content

def add_missing_variables(content):
    """Ensure all CSS variables are defined"""
    if '--primary:' not in content:
        # Add variables if they don't exist
        style_pattern = r'(<style>)'
        
        variables_css = f"""
:root {{
    --primary: {colors['primary']};
    --primary-dark: {colors['primary-dark']};
    --primary-light: {colors['primary-light']};
    --primary-lightest: {colors['primary-lightest']};
    --accent: {colors['accent']};
    --light-bg: {colors['light-bg']};
    --card-bg: {colors['card-bg']};
    --text-dark: {colors['text-dark']};
    --text-light: {colors['text-light']};
    --border-color: {colors['border-color']};
}}
"""
        if '<style>' in content:
            content = re.sub(r'<style>', f'<style>\n{variables_css}', content)
    
    return content

def update_file(filepath):
    """Update single HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Processing: {filepath}")
        
        # Update CSS variables
        content = update_css_variables(content)
        
        # Update inline colors
        content = update_inline_colors(content)
        
        # Add missing variables
        content = add_missing_variables(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated: {os.path.basename(filepath)}")
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")

print("🎨 Updating all templates with merah-putih color scheme...\n")

for template in templates:
    filepath = os.path.join(base_path, template)
    if os.path.exists(filepath):
        update_file(filepath)
    else:
        print(f"⚠️  Not found: {template}")

print("\n✅ Semua template sudah diupdate dengan warna merah-putih!")
