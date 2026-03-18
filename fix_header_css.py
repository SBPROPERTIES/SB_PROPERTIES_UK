import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply the standard nav-flex gap
    content = re.sub(
        r'\.nav-flex\s*\{\s*display:\s*flex;\s*justify-content:\s*space-between;\s*align-items:\s*center;\s*\}',
        r'.nav-flex { display: flex; justify-content: space-between; align-items: center; gap: 14px; }',
        content
    )
    
    # Apply standard logo styles
    content = re.sub(
        r'\.logo\s*\{\s*font-weight:\s*950;\s*color:\s*var\(--black\);\s*display:\s*flex;\s*align-items:\s*center;\s*gap:\s*10px;\s*text-decoration:\s*none;\s*\}',
        r'.logo { font-size: 1.1rem; font-weight: 950; color: var(--black); display: flex; align-items: center; gap: 10px; white-space: nowrap; text-decoration: none; }',
        content
    )
    # Different blog page might lack text-decoration: none in its regex match, fallback replacer
    content = re.sub(
        r'\.logo\s*\{\s*font-weight:\s*950;\s*color:\s*var\(--black\);\s*display:\s*flex;\s*align-items:\s*center;\s*gap:\s*10px;\s*\}',
        r'.logo { font-size: 1.1rem; font-weight: 950; color: var(--black); display: flex; align-items: center; gap: 10px; white-space: nowrap; text-decoration: none; }',
        content
    )

    # Apply standard logo img styles
    content = re.sub(
        r'\.logo img\s*\{\s*height:\s*44px;\s*width:\s*auto;\s*\}',
        r'.logo img { height: 44px; width: auto; display: block; }',
        content
    )

    # Apply standard header-actions styles
    content = re.sub(
        r'\.header-actions\s*\{\s*display:\s*flex;\s*align-items:\s*center;\s*gap:\s*20px;\s*\}',
        r'.header-actions {\n            display: flex;\n            align-items: center;\n            gap: 14px;\n        }',
        content
    )
    # Single-line replace
    content = re.sub(
        r'\.header-actions\s*\{\s*display:\s*flex;\s*align-items:\s*center;\s*gap:\s*20px;\s*\}',
        r'.header-actions { display: flex; align-items: center; gap: 14px; }',
        content, flags=re.MULTILINE
    )
    
    # Standard btn missing properties
    if '.btn {' in content and 'font-size: 1rem;' not in content:
        content = content.replace(
            '.btn { display: inline-block; padding: 14px 32px; border-radius: var(--border-radius); font-weight: 800; text-decoration: none; transition: 0.2s; background: var(--primary); color: var(--white); }',
            '.btn { display: inline-block; padding: 14px 32px; border-radius: var(--border-radius); font-weight: 800; text-align: center; font-size: 1rem; border: none; line-height: 1; text-decoration: none; transition: 0.2s; background: var(--primary); color: var(--white); }'
        )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath}")

def main():
    target_dir = r"c:\Users\Sean\Documents\Webisites\SB-Properties\SB_PROPERTIES_UK-Github\blog"
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".html"):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
