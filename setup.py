from setuptools import setup

setup(
    name='Magic Hand',
    version='1.0.0',
    description='AI-powered desktop file organizer with automatic classification',
    author='Oguz Ates',
    app=['src/backend/app.py'],
    data_files=[
        ('assets', ['assets/menu-icon.png', 'assets/app-icon.png']),
        ('', ['.env.example'])
    ],
    options={
        'py2app': {
            'argv_emulation': False,
            'packages': ['watchdog', 'urllib3', 'openai', 'PyQt5', 'dotenv', 'certifi'],
            'includes': ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
            'iconfile': 'assets/app-icon.png',
            'resources': ['assets'],
            'plist': {
                'LSUIElement': True,
                'CFBundleName': 'Magic Hand',
                'CFBundleDisplayName': 'Magic Hand',
                'CFBundleIdentifier': 'com.magichand.app',
                'CFBundleVersion': '1.0.0',
                'NSHighResolutionCapable': True
            }
        }
    },
    setup_requires=['py2app']
)
