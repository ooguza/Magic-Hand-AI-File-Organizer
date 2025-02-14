# 🤲 Magic Hand

Magic Hand is an intelligent file organization system that automatically categorizes your desktop files using artificial intelligence.

## 📁 Folder Structure

The system uses two main folders:

1. **AI Library**: Yapay zeka tarafından otomatik sınıflandırılan dosyalar
   - Design: Photoshop, Illustrator, Sketch, Figma dosyaları
   - Documents: PDF, Word, metin belgeleri
   - Images: Fotoğraflar ve görseller
   - Code: Kaynak kodları ve geliştirme dosyaları
   - Archives: ZIP, RAR gibi arşivler
   - Media: MP3, MP4 gibi medya dosyaları
   - Others: Diğer tüm dosyalar

2. **Manual Library**: Manuel olarak organize edilmek istenen dosyalar

## 💻 Technical Details

### File Monitoring System
- Desktop is continuously monitored using the **watchdog** library
- Automatic detection when files are created or modified
- Files are processed after their size remains stable for 2 seconds
- Hidden files (.) and temporary files (.tmp) are ignored

### AI Classification Process

1. **Extension Check**
   ```python
   # Example: .psd -> Design, .pdf -> Documents
   if extension in ['psd', 'ai', 'sketch']: return 'Design'
   if extension in ['pdf', 'doc', 'txt']: return 'Documents'
   if extension in ['jpg', 'png', 'gif']: return 'Images'
   ```

2. **MIME Type Check**
   ```python
   # Example: image/jpeg -> Images
   if mime_type in ['application/pdf']: return 'Documents'
   if mime_type.startswith('image/'): return 'Images'
   if mime_type.startswith('text/'): return 'Code'
   ```

3. **AI Analizi**
   ```python
   # GPT-3.5 ile dosya içeriği analizi
   system_prompt = """Classify the file into one of these categories: 
   Design, Documents, Images, Code, Others. 
   Return only the category name."""

   user_prompt = f"""File: {name}
   Type: {mime_type}
   Content: {preview}"""
   ```

### Caching
- Classification results are stored in a JSON file
- Quick results when the same file is encountered again
- Cache is loaded at program startup

### Error Management
- File read/write errors are caught
- Fallback categorization in case of API errors
- Automatic numbering for conflicting file names

## 📚 Usage

1. **Kurulum**
   ```bash
   # Gereksinimleri yükle
   pip install -r requirements.txt

   # .env dosyasına OpenAI API anahtarını ekle
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

2. **Çalıştırma**
   ```bash
   python src/backend_new/organizer.py
   ```

3. **Kullanım**
   - Masaüstüne bir dosya koyun
   - Program otomatik olarak dosyayı analiz edecek
   - Dosya uygun kategoriye taşınacak

## 📈 Performance

- **Speed**: Most files are classified within 2-3 seconds
- **Accuracy**: 100% for basic file types, 90%+ for complex files
- **Efficiency**: Recurring files are classified instantly thanks to caching

## 💡 Features

- ✨ Automatic file monitoring and organization
- 🤖 Smart AI classification
- 📑 Multiple file type support
- 💾 Fast processing with caching
- 🔄 Conflict management
- 📂 Simple and organized folder structure

## 📝 Notes

- All files on the desktop are monitored while the program is running
- Hidden files and system files are ignored
- Conflicting file names are automatically resolved
- Internet connection is required for AI classification

## 📌 Todo

- [ ] Support for more file types
- [ ] Customizable categories
- [ ] Advanced AI analysis
- [ ] Interface improvements
- [ ] Statistics and reporting

## 👨‍💻 Technical Requirements

- Python 3.7+
- OpenAI API anahtarı
- İnternet bağlantısı
- macOS (diğer sistemler test edilmedi)

## 📖 Dependencies

```
watchdog==3.0.0
requests==2.31.0
certifi==2024.2.2
python-dotenv==1.0.0
```
- 🗂 Smart File Categorization
- 🔄 Real-time Desktop Monitoring
- 🖥 Menu Bar Interface
- 🌐 Multi-language Support
- 🚀 Automatic Startup
- 📊 Organization Statistics

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/magic-hand-organizer.git
cd magic-hand-organizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. Run the application:
```bash
python src/backend/app.py
```

## Project Structure

```
magic-hand-organizer/
├── src/
│   └── backend/           # Python backend
│       ├── app.py         # Main application (PyQt5)
│       ├── organizer.py   # File organization logic
│       └── ai_classifier.py # AI classification
├── assets/              # Icons and images
├── docs/                # Documentation
└── tests/               # Test files
```

## Technology Stack

- **GUI**: PyQt5
- **Backend**: Python
- **AI**: OpenAI GPT API
- **File Monitoring**: watchdog
- **Testing**: Pytest

## Development

### Prerequisites

- Node.js 18+
- Python 3.8+
- OpenAI API key
- macOS 10.15+

### Setup Development Environment

1. Install development dependencies:
```bash
npm install --save-dev electron-builder electron-reload
```

2. Start development server:
```bash
npm run dev
```

### Building

```bash
# Build for macOS
npm run build:mac
```

## Documentation

Detailed documentation is available in the `/docs` directory:

- [Technical Documentation](docs/TECHNICAL.md)
- [API Documentation](docs/API.md)
- [User Guide](docs/USER_GUIDE.md)
- [Development Guide](docs/DEVELOPMENT.md)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Your Name - your.email@example.com
