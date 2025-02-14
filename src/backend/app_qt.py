import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from watchdog.observers import Observer
from organizer import FileOrganizer

class MagicHandApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # Paths
        self.desktop_path = os.path.expanduser("~/Desktop")
        self.paths = {
            'root': os.path.join(self.desktop_path, "Magic Hand"),
            'ai_library': os.path.join(self.desktop_path, "Magic Hand", "AI Library"),
            'manual_library': os.path.join(self.desktop_path, "Magic Hand", "Manual Library")
        }
        
        # Create directories
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)
        
        # Initialize organizer and observer
        self.organizer = FileOrganizer()
        self.observer = Observer()
        self.observer.schedule(self.organizer, self.desktop_path, recursive=False)
        
        # Create tray icon
        self.tray = QSystemTrayIcon()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'menu-icon.png')
        self.tray.setIcon(QIcon(icon_path))
        
        # Create menu
        self.menu = QMenu()
        
        # Add menu items
        organize_action = QAction("Organize Now", self.menu)
        organize_action.triggered.connect(self.organize_now)
        self.menu.addAction(organize_action)
        
        self.pause_action = QAction("Pause Organizing", self.menu)
        self.pause_action.triggered.connect(self.toggle_pause)
        self.menu.addAction(self.pause_action)
        
        self.menu.addSeparator()
        
        open_ai_action = QAction("Open AI Library", self.menu)
        open_ai_action.triggered.connect(lambda: os.system(f"open {self.paths['ai_library']}"))
        self.menu.addAction(open_ai_action)
        
        open_manual_action = QAction("Open Manual Library", self.menu)
        open_manual_action.triggered.connect(lambda: os.system(f"open {self.paths['manual_library']}"))
        self.menu.addAction(open_manual_action)
        
        self.menu.addSeparator()
        
        quit_action = QAction("Quit", self.menu)
        quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(quit_action)
        
        # Set the menu
        self.tray.setContextMenu(self.menu)
        
        # Show the tray icon
        self.tray.show()
        
        # Start file watching
        self.observer.start()
    
    def organize_now(self):
        """Manually trigger organization"""
        self.organizer._scan_existing_files()
    
    def toggle_pause(self):
        """Toggle pause/resume organizing"""
        if self.observer.is_alive():
            self.observer.stop()
            self.pause_action.setText("Resume Organizing")
        else:
            self.observer.start()
            self.pause_action.setText("Pause Organizing")
    
    def quit_app(self):
        """Quit the application"""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        self.app.quit()
    
    def run(self):
        """Run the application"""
        return self.app.exec_()

if __name__ == "__main__":
    app = MagicHandApp()
    sys.exit(app.run())
