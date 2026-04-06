import os

# New registration number
OLD_REG = "SC671234"
NEW_REG = "SC884935"

def update_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if OLD_REG in content:
        new_content = content.replace(OLD_REG, NEW_REG)
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(new_content)
        return True
    return False

def main():
    root_dir = r"c:\Users\Sean\Documents\Webisites\SB-Properties\SB_PROPERTIES_UK-Github"
    count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(('.html', '.xml', '.json')):
                file_path = os.path.join(root, file)
                if update_file(file_path):
                    print(f"Updated: {file_path}")
                    count += 1
    
    print(f"\nTotal files updated: {count}")

if __name__ == "__main__":
    main()
