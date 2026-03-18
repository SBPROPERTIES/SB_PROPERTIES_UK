import os
import re

css_to_add = """
        /* Mobile Header Icons CSS */
        .mobile-icons { display: none; }
        .desktop-phone { display: none; }
        @media (min-width: 721px) {
            .desktop-phone { display: inline-block !important; }
        }
        @media (max-width: 720px) {
            .mobile-icons { display: flex !important; gap: 16px; align-items: center; }
            .mobile-icons a { color: var(--black); display: flex; align-items: center; justify-content: center; }
        }
"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if '/* Mobile Header Icons CSS */' not in content:
        content = re.sub(r'(</style>)', css_to_add + r'\1', content, count=1, flags=re.IGNORECASE)

    # Extract blog path for the icon
    blog_path = "blog/"
    blog_match = re.search(r'<a href="([^"]+)"[^>]*>Blog</a>', content, re.IGNORECASE)
    if blog_match:
        blog_path = blog_match.group(1)

    # We want to replace the phone anchor tag.
    # It usually looks like: <a href="tel:07346739722"...>07346739722</a>
    # Or similarly. Let's find exactly that.
    phone_regex = r'(<a href="tel:07346739722"[^>]*>07346739722</a>)'
    
    match = re.search(phone_regex, content)
    if not match:
        # Maybe it doesn't have the phone number, or it's formatted differently.
        print(f"Phone number not found in {filepath}")
        return

    old_phone_tag = match.group(1)
    
    # Check if we already injected mobile icons
    if 'class="mobile-icons"' in content:
        print(f"Mobile icons already exist in {filepath}")
        return

    mobile_icons_html = f"""
            <!-- Mobile Icons -->
            <div class="mobile-icons">
                <a href="{blog_path}" aria-label="Blog">
                    <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
                </a>
                <a href="tel:07346739722" aria-label="Call Us">
                    <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                </a>
            </div>
"""
    
    # We replace the old phone tag with classes that actually work (desktop-phone)
    # The old tag might have style="...", class="phone-link", etc.
    # We will just rewrite the tag clean to ensure it works.
    new_phone_tag = f'<a href="tel:07346739722" class="desktop-phone" style="font-weight:900; color:black; text-decoration:none;">07346739722</a>'
    
    # Only replace the FIRST occurrence in the header (which is usually the only one but just in case)
    # Actually, we can just replace all occurrences of `old_phone_tag` in the `header-actions` block.
    # Better yet, replacing it globally is fine if it appears in the footer, but it shouldn't be hidden in the footer.
    # So let's only do it inside the header.
    
    header_regex = r'(<header>.*?</header>)'
    
    def replacer(m):
        header_content = m.group(1)
        new_header = header_content.replace(old_phone_tag, mobile_icons_html + new_phone_tag)
        return new_header

    new_content = re.sub(header_regex, replacer, content, count=1, flags=re.DOTALL | re.IGNORECASE)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated {filepath}")

def main():
    target_dir = r"c:\Users\Sean\Documents\Webisites\SB-Properties\SB_PROPERTIES_UK-Github"
    for root, dirs, files in os.walk(target_dir):
        if '.git' in root or '.gemini' in root:
            continue
        for file in files:
            if file.endswith(".html"):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
