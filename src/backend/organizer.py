import os
import time
import shutil
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ai_classifier import AIClassifier

class FileOrganizer(FileSystemEventHandler):
    def __init__(self):
        # Main folders
        self.desktop_path = os.path.expanduser("~/Desktop")
        self.paths = {
            'root': os.path.join(self.desktop_path, "Magic Hand"),
            'ai_library': os.path.join(self.desktop_path, "Magic Hand", "AI Library"),
            'manual_library': os.path.join(self.desktop_path, "Magic Hand", "Manual Library")
        }
        
        # Create folders
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)
        
        # Create base folders
        # All folders are already created above
        
        # Track file states
        self.file_states = {}
        
        # AI classifier
        self.classifier = AIClassifier()
        
    def is_file_stable(self, file_path):
        """Check if the file is stable"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False
                
            if os.path.basename(file_path).startswith('.'):
                print(f"ℹ️ Hidden file ignored: {file_path}")
                return False
                
            current_time = datetime.now()
            current_size = os.path.getsize(file_path)
            
            print(f"📄 Checking file: {file_path} (Size: {current_size} bytes)")
            
            # Update or create file status
            if file_path not in self.file_states:
                print(f"🆕 New file: {file_path}")
                self.file_states[file_path] = {
                    'size': current_size,
                    'last_modified': current_time,
                    'stable_since': current_time
                }
                return True  # Process new files immediately
                
            state = self.file_states[file_path]
            
            # If size changed, reset status
            if current_size != state['size']:
                print(f"📈 File size changed: {file_path}")
                state.update({
                    'size': current_size,
                    'last_modified': current_time,
                    'stable_since': current_time
                })
                return False
                
            # File is stable
            time_stable = (current_time - state['stable_since']).total_seconds()
            print(f"⏳ File stability duration: {time_stable:.1f} seconds")
            return True
            
        except Exception as e:
            print(f"❌ File check error: {e}")
            return False
    
    def organize_file(self, file_path):
        """Organize the file"""
        try:
            # Ignore hidden and temporary files
            filename = os.path.basename(file_path)
            if filename.startswith('.') or '.tmp' in filename.lower():
                return
                
            # Classify the file
            category = self.classifier.classify_file(file_path)
            
            # Create target folder
            target_dir = os.path.join(self.paths['ai_library'], category)
            Path(target_dir).mkdir(exist_ok=True)
            
            # Target file path
            target_path = os.path.join(target_dir, filename)
            
            # If a file with same name exists, add a number to the end
            if os.path.exists(target_path):
                name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(target_path):
                    new_name = f"{name} {counter}{ext}"
                    target_path = os.path.join(target_dir, new_name)
                    counter += 1
            
            # Move the file
            shutil.move(file_path, target_path)
            print(f"✨ File organized: {filename} -> AI Library/{category}")
            
        except Exception as e:
            print(f"❌ Organization error: {e}")
            
    def on_created(self, event):
        """When a new file is created"""
        if event.is_directory or self.paths['root'] in event.src_path:
            return
            
        # Start monitoring the file
        self.watch_file(event.src_path)
        
    def on_modified(self, event):
        """When a file is modified"""
        if event.is_directory or self.paths['root'] in event.src_path:
            return
            
        # Continue monitoring the file
        self.watch_file(event.src_path)
        
    def watch_file(self, file_path):
        """Monitor the file and organize when ready"""
        print(f"📥 Examining file: {file_path}")
        if self.is_file_stable(file_path):
            print(f"✅ File is stable: {file_path}")
            self.organize_file(file_path)
        else:
            print(f"⏳ File is not stable yet: {file_path}")
            
    def _scan_existing_files(self):
        """Scan existing files on the desktop"""
        for item in os.listdir(self.desktop_path):
            file_path = os.path.join(self.desktop_path, item)
            if os.path.isfile(file_path) and not item.startswith('.'):
                self.watch_file(file_path)

def start_organizer():
    """Start file organization"""
    observer = Observer()
    organizer = FileOrganizer()
    
    # Monitor desktop
    observer.schedule(organizer, organizer.desktop_path, recursive=False)
    observer.start()
    return observer

if __name__ == "__main__":
    print("🤲 Starting Magic Hand...")
    organizer = FileOrganizer()
    print("📂 Scanning existing files...")
    organizer._scan_existing_files()
    
    print("👀 Monitoring desktop...")
    observer = Observer()
    observer.schedule(organizer, organizer.desktop_path, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
