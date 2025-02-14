import os
import json
import mimetypes
import urllib3
import certifi
from pathlib import Path

# Update MIME types
mimetypes.add_type('application/x-photoshop', '.psd')
mimetypes.add_type('application/x-photoshop', '.psb')
mimetypes.add_type('application/illustrator', '.ai')
mimetypes.add_type('application/x-sketch', '.sketch')
mimetypes.add_type('application/x-figma', '.fig')
mimetypes.add_type('application/x-adobe-xd', '.xd')

class AIClassifier:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY', '')
        self.cache_file = 'classification_cache.json'
        self.load_cache()
        
        # Category rules
        self.categories = {
            'Design': {
                'extensions': ['psd', 'ai', 'sketch', 'fig', 'xd'],
                'mime_types': ['application/x-photoshop', 'application/illustrator', 'application/x-sketch']
            },
            'Documents': {
                'extensions': ['pdf', 'doc', 'docx', 'txt', 'rtf'],
                'mime_types': ['application/pdf', 'application/msword', 'text/plain']
            },
            'Images': {
                'extensions': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
                'mime_types': ['image/jpeg', 'image/png', 'image/gif']
            },
            'Code': {
                'extensions': ['py', 'js', 'html', 'css', 'json'],
                'mime_types': ['text/x-python', 'application/javascript', 'text/html']
            },
            'Others': {
                'extensions': [],
                'mime_types': []
            }
        }
        
    def load_cache(self):
        """Load previous classifications from cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception:
            self.cache = {}
            
    def save_cache(self):
        """Save classification results to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception:
            pass
            
    def get_file_info(self, file_path):
        """Gather information about the file"""
        try:
            name = os.path.basename(file_path)
            size = os.path.getsize(file_path)
            
            # Content preview (first 1024 bytes)
            content_preview = ''
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content_preview = f.read(1024)
            except:
                pass
                
            return {
                'name': name,
                'size': size,
                'content_preview': content_preview
            }
        except Exception:
            return None
            
    def classify_file(self, file_path):
        """Classify the file"""
        print(f"🔍 Classifying file: {file_path}")
        
        # Check if exists in cache
        if file_path in self.cache:
            category = self.cache[file_path]
            print(f"💾 Retrieved from cache: {category}")
            return category
            
        # Get file information
        file_info = self.get_file_info(file_path)
        if not file_info:
            print(f"❌ Could not get file information: {file_path}")
            return 'Others'
            
        # Get extension and MIME type
        extension = os.path.splitext(file_path)[1].lower()
        mime_type = self._get_mime_type(file_path, extension)
        print(f"📁 File info - Extension: {extension}, MIME: {mime_type}")
        
        # Step 1: Extension check
        print("🔎 Step 1: Extension check")
        for category, rules in self.categories.items():
            if extension[1:] in rules['extensions']:
                self.cache[file_path] = category
                print(f"✅ Classified by extension: {category}")
                return category
                
        # Step 2: MIME type check
        print("🔎 Step 2: MIME type check")
        for category, rules in self.categories.items():
            if mime_type in rules['mime_types']:
                self.cache[file_path] = category
                print(f"✅ Classified by MIME type: {category}")
                return category
                
        # Step 3: AI analysis
        system_prompt = """Classify the file into one of these categories: Design, Documents, Images, Code, Others. Return only the category name."""
        
        user_prompt = f"""File: {file_info['name']}
Type: {mime_type}
Content: {file_info['content_preview']}"""
        
        try:
            http = urllib3.PoolManager(
                cert_reqs='CERT_REQUIRED',
                ca_certs=certifi.where()
            )
            
            response = http.request(
                'POST',
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                body=json.dumps({
                    'model': 'gpt-3.5-turbo',
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_prompt}
                    ],
                    'temperature': 0.3,
                    'max_tokens': 10
                })
            )
            
            if response.status == 200:
                data = json.loads(response.data.decode('utf-8'))
                ai_category = data['choices'][0]['message']['content'].strip()
                if ai_category in self.categories:
                    self.cache[file_path] = ai_category
                    return ai_category
                    
        except Exception as e:
            print(f"❌ AI classification error: {e}")
            
        # If no match is found
        self.cache[file_path] = 'Others'
        return 'Others'
        
    def _get_mime_type(self, file_path, extension):
        """Determine MIME type"""
        mime_type, encoding = mimetypes.guess_type(file_path)
        
        if mime_type is None:
            # Default MIME types for known extensions
            if extension.lower() in ['.psd', '.psb']:
                return 'application/x-photoshop'
            elif extension.lower() == '.ai':
                return 'application/illustrator'
            elif extension.lower() == '.sketch':
                return 'application/x-sketch'
            elif extension.lower() == '.fig':
                return 'application/x-figma'
            elif extension.lower() == '.xd':
                return 'application/x-adobe-xd'
            else:
                return 'application/octet-stream'
        
        return mime_type.lower()
