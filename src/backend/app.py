import sys
import os
import webbrowser
import shutil
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QInputDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject
from watchdog.observers import Observer
from organizer import FileOrganizer

# Set up logging
log_file = os.path.expanduser('~/Desktop/magichand.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class MagicHandApp(QObject):
    def __init__(self):
        logging.info("Starting MagicHandApp initialization...")
        super().__init__()
        
        # Initialize application
        logging.info("Creating QApplication...")
        self.app = QApplication(sys.argv)
        
        # Initialize paths
        self.paths = {
            'desktop': os.path.expanduser("~/Desktop"),
            'root': os.path.join(os.path.expanduser("~/Desktop"), "Magic Hand"),
            'ai_library': os.path.join(os.path.expanduser("~/Desktop"), "Magic Hand", "AI Library"),
            'manual_library': os.path.join(os.path.expanduser("~/Desktop"), "Magic Hand", "Manual Library")
        }
        
        # Create directories
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)
        
        # Initialize components
        self.init_tray()
        self.init_monitoring()
        
        # State
        self.is_paused = False
    
    def init_tray(self):
        """Initialize system tray icon and menu"""
        try:
            logging.info("Creating QSystemTrayIcon...")
            self.tray = QSystemTrayIcon()
            
            # Set icon
            if getattr(sys, '_MEIPASS', False):
                # Running as bundled app
                menu_icon_path = os.path.join(sys._MEIPASS, 'assets', 'menu-icon.png')
            else:
                # Running as script
                menu_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'menu-icon.png')
            
            logging.info(f"Looking for menu icon at: {menu_icon_path}")
            if os.path.exists(menu_icon_path):
                logging.info("Menu icon found, setting icon...")
                self.tray.setIcon(QIcon(menu_icon_path))
                logging.info("Icon set successfully")
            else:
                logging.error(f"Menu icon not found at: {menu_icon_path}")
            
            # Set menu and show
            self.tray.setContextMenu(self.create_menu())
            self.tray.show()
            logging.info("System tray icon initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize system tray: {str(e)}")
            raise
    
    def init_monitoring(self):
        """Initialize file system monitoring"""
        try:
            logging.info("Initializing file monitoring...")
            self.organizer = FileOrganizer()
            self.observer = None
            self.start_monitoring()
            logging.info("File monitoring initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize file monitoring: {str(e)}")
            raise
    
    def create_menu(self):
        menu = QMenu()
        
        # Add title (disabled item)
        title_action = menu.addAction("Magic Hand")
        title_action.setEnabled(False)
        menu.addSeparator()
        
        # Add other menu items
        organize_action = menu.addAction("Organize Now")
        self.pause_action = menu.addAction("Pause Organizing")
        menu.addSeparator()
        
        ai_lib_action = menu.addAction("Open AI Library")
        manual_lib_action = menu.addAction("Open Manual Library")
        menu.addSeparator()
        
        settings_menu = menu.addMenu("Settings")
        
        # API Key status and action
        api_key = os.getenv('OPENAI_API_KEY', '')
        api_key_status = "✓ API Key Set" if api_key else "✗ API Key Not Set"
        api_key_menu = settings_menu.addMenu(api_key_status)
        api_key_menu.addAction("Change API Key").triggered.connect(self.set_api_key)
        if api_key:
            # Show last 4 characters of API key
            masked_key = f"...{api_key[-4:]}" if len(api_key) > 4 else api_key
            api_key_info = api_key_menu.addAction(f"Current: {masked_key}")
            api_key_info.setEnabled(False)
        
        settings_menu.addSeparator()
        startup_status = "✓ Run at Startup (Enabled)" if self.is_startup_enabled() else "Run at Startup (Disabled)"
        self.startup_action = settings_menu.addAction(startup_status)
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(self.is_startup_enabled())
        menu.addSeparator()
        
        about_action = menu.addAction("About")
        quit_action = menu.addAction("Quit Magic Hand")
        
        # Connect signals
        organize_action.triggered.connect(self.organize_now)
        self.pause_action.triggered.connect(self.toggle_pause)
        ai_lib_action.triggered.connect(self.open_ai_library)
        manual_lib_action.triggered.connect(self.open_manual_library)
        self.startup_action.triggered.connect(self.toggle_startup)
        about_action.triggered.connect(self.show_about)
        quit_action.triggered.connect(self.quit_app)
        
        return menu
    
    def organize_now(self):
        try:
            self.organizer._scan_existing_files()
            self.tray.showMessage(
                "Magic Hand",
                "All files have been organized!",
                QSystemTrayIcon.Information
            )
        except Exception as e:
            self.tray.showMessage(
                "Magic Hand",
                f"Organization Error: {str(e)}",
                QSystemTrayIcon.Warning
            )
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_action.setText("Resume Organizing")
            self.observer.stop()
        else:
            self.pause_action.setText("Pause Organizing")
            self.observer.start()
    
    def open_ai_library(self):
        webbrowser.open(f"file://{self.paths['ai_library']}")
    
    def open_manual_library(self):
        webbrowser.open(f"file://{self.paths['manual_library']}")
    
    def stop_monitoring(self):
        """Stop the file system observer safely"""
        logging.info("Stopping file system monitoring")
        try:
            if hasattr(self, 'observer') and self.observer is not None:
                self.observer.stop()
                self.observer.join()
                logging.info("File system monitoring stopped successfully")
        except Exception as e:
            logging.error(f"Error stopping file system monitoring: {str(e)}")

    def start_monitoring(self):
        """Start the file system observer safely"""
        logging.info("Starting file system monitoring")
        try:
            # Always create a new observer
            self.observer = Observer()
            self.observer.schedule(self.organizer, self.paths['desktop'], recursive=False)
            self.observer.start()
            logging.info("File system monitoring started successfully")
        except Exception as e:
            logging.error(f"Error starting file system monitoring: {str(e)}")
            self.observer = None

    def set_api_key(self):
        logging.info("Starting API key update process")
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        current_key = os.getenv('OPENAI_API_KEY', '')
        api_key, ok = QInputDialog.getText(
            None,
            "API Key Settings",
            "Enter your OpenAI API key:",
            text=current_key
        )
        
        if ok:
            try:
                # Stop monitoring before making changes
                self.stop_monitoring()
                
                if not api_key.strip():
                    logging.info("Removing API key")
                    if os.path.exists(env_path):
                        os.remove(env_path)
                else:
                    logging.info("Saving new API key to .env file")
                    # Save API key
                    with open(env_path, 'w') as f:
                        f.write(f"OPENAI_API_KEY={api_key.strip()}")
                
                logging.info("Reloading environment variables")
                # Reload environment variables
                load_dotenv(override=True)
                
                # Restart monitoring with new API key
                self.start_monitoring()
                
                logging.info("Showing success message")
                # Show success message
                self.tray.showMessage(
                    "Magic Hand",
                    "API key has been successfully " + ("removed" if not api_key.strip() else "updated") + "!",
                    QSystemTrayIcon.Information,
                    2000  # Show for 2 seconds
                )
                
                logging.info("Updating menu")
                # Recreate the menu to update API key status
                self.tray.setContextMenu(self.create_menu())
                
                logging.info("API key update completed successfully")
                
            except Exception as e:
                logging.error(f"Error during API key update: {str(e)}")
                self.tray.showMessage(
                    "Magic Hand",
                    f"Error setting API key: {str(e)}",
                    QSystemTrayIcon.Warning,
                    2000  # Show for 2 seconds
                )
                # Try to restart monitoring in case of error
                self.start_monitoring()
    
    def show_about(self):
        QMessageBox.about(
            None,
            "About Magic Hand",
            "Magic Hand v1.0\n\nAn AI-powered file organizer that helps keep your desktop clean and organized."
        )
    
    def quit_app(self):
        self.observer.stop()
        self.observer.join()
        self.app.quit()
    
    def run(self):
        print("Starting application event loop...")
        try:
            return self.app.exec_()
        except Exception as e:
            print(f"Error in event loop: {e}")
            return 1
    
    def show_about(self):
        about_text = (
            "An intelligent file organizer powered by AI.\n\n"
            "Created by Oguz Ates\n"
            "LinkedIn: https://www.linkedin.com/in/oguz-ates\n\n"
            "--\n\n"
            "To use this app, you need an OpenAI API key.\n"
            "Set your API key in Settings > Set API Key."
        )
        
        QMessageBox.about(None, "About Magic Hand", about_text)
        webbrowser.open("https://www.linkedin.com/in/oguz-ates")
    
    def is_startup_enabled(self):
        """Check if the app is set to run at startup"""
        launch_agent_path = os.path.expanduser('~/Library/LaunchAgents/com.magichand.app.plist')
        return os.path.exists(launch_agent_path)

    def toggle_startup(self):
        """Toggle startup setting"""
        logging.info("Toggling startup setting")
        launch_agent_path = os.path.expanduser('~/Library/LaunchAgents/com.magichand.app.plist')
        app_path = '/Applications/Magic Hand.app'
        
        # Create plist content
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.magichand.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>open</string>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>'''

        try:
            if self.startup_action.isChecked():
                logging.info("Enabling startup")
                # Create LaunchAgents directory if it doesn't exist
                os.makedirs(os.path.dirname(launch_agent_path), exist_ok=True)
                
                # Write plist file
                with open(launch_agent_path, 'w') as f:
                    f.write(plist_content)
                
                # Set correct permissions
                os.chmod(launch_agent_path, 0o644)
                
                # Load the launch agent
                os.system(f'launchctl load {launch_agent_path}')
                
                self.tray.showMessage(
                    "Magic Hand",
                    "Application will now run at startup!",
                    QSystemTrayIcon.Information,
                    2000
                )
            else:
                logging.info("Disabling startup")
                # Unload the launch agent if it exists
                if os.path.exists(launch_agent_path):
                    os.system(f'launchctl unload {launch_agent_path}')
                    os.remove(launch_agent_path)
                self.tray.showMessage(
                    "Magic Hand",
                    "Application will no longer run at startup.",
                    QSystemTrayIcon.Information,
                    2000
                )
            
            logging.info("Updating menu")
            # Update menu to reflect new startup status
            self.tray.setContextMenu(self.create_menu())
            
        except Exception as e:
            logging.error(f"Error toggling startup: {str(e)}")
            self.tray.showMessage(
                "Magic Hand",
                f"Error setting startup: {str(e)}",
                QSystemTrayIcon.Warning,
                2000
            )
            # Revert checkbox state
            self.startup_action.setChecked(not self.startup_action.isChecked())
            # Update menu
            self.tray.setContextMenu(self.create_menu())

    def quit_app(self):
        logging.info("Starting application shutdown")
        try:
            logging.info("Stopping observer")
            self.observer.stop()
            self.observer.join()
            logging.info("Observer stopped successfully")
        except Exception as e:
            logging.error(f"Error stopping observer: {str(e)}")
        
        logging.info("Quitting application")
        QApplication.quit()

if __name__ == "__main__":
    try:
        logging.info("Starting application...")
        app = MagicHandApp()
        logging.info("Running application...")
        app.run()
    except Exception as e:
        logging.error(f"Error running application: {e}", exc_info=True)
