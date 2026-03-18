import os
import re

whatsapp_block = """
                        <a href="https://wa.me/447346739722" target="_blank" rel="noopener" title="WhatsApp" aria-label="WhatsApp">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
                            </svg>
                        </a>"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the closing tag of the Instagram link
    # The Instagram link looks like this:
    # <a href="https://www.instagram.com/sbproperties.uk?igsh=MWRvNWh0ZXk4MHVubA==" target="_blank" rel="noopener" title="Instagram" aria-label="Instagram">
    #     ... SVG ...
    # </a>
    # We want to insert the WhatsApp block immediately after this </a>.

    if 'aria-label="WhatsApp"' in content:
        print(f"WhatsApp already exists in {filepath}")
        return

    # Regular expression to find the Instagram anchor block based on aria-label
    insta_regex = r'(<a [^>]*aria-label="Instagram"[^>]*>.*?</a>)'
    
    match = re.search(insta_regex, content, re.DOTALL | re.IGNORECASE)
    if not match:
        print(f"Instagram link not found in {filepath}")
        return
        
    insta_block = match.group(1)
    
    # Replace the insta_block with insta_block + whatsapp_block
    new_content = content.replace(insta_block, insta_block + whatsapp_block)

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
