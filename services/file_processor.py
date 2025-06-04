"""
AITON-RAG File Processor Service
Konvertiert verschiedene Dateiformate zu Markdown mit Metadaten
"""

import os
import hashlib
import logging
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid

# File processing imports
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    from markdownify import markdownify
except ImportError:
    markdownify = None

try:
    import chardet
except ImportError:
    chardet = None

from config import Config

class FileProcessor:
    """Intelligente Dateiverarbeitung für verschiedene Formate"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        self.processed_hashes = set()
        
    def process_file(self, file_path: Path) -> Optional[Dict]:
        """
        Verarbeitet eine einzelne Datei zu Markdown
        
        Args:
            file_path: Pfad zur zu verarbeitenden Datei
            
        Returns:
            Dict mit verarbeiteten Daten oder None bei Fehler
        """
        try:
            # File validation
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}")
                return None
                
            if file_path.stat().st_size > self.config.MAX_FILE_SIZE:
                self.logger.error(f"File too large: {file_path}")
                return None
            
            # Generate file hash for duplicate detection
            file_hash = self._generate_file_hash(file_path)
            if file_hash in self.processed_hashes:
                self.logger.info(f"File already processed: {file_path}")
                return None
                
            # Extract metadata
            metadata = self._extract_metadata(file_path)
            
            # Convert to markdown based on file type
            markdown_content = self._convert_to_markdown(file_path)
            
            if markdown_content is None:
                return None
                
            # Store hash to prevent reprocessing
            self.processed_hashes.add(file_hash)
            
            return {
                'file_path': str(file_path),
                'file_hash': file_hash,
                'metadata': metadata,
                'markdown_content': markdown_content,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            return None
    
    def process_batch(self, upload_dir: Path) -> List[Dict]:
        """
        Verarbeitet alle Dateien in einem Verzeichnis
        
        Args:
            upload_dir: Verzeichnis mit zu verarbeitenden Dateien
            
        Returns:
            Liste der verarbeiteten Dateien
        """
        processed_files = []
        
        if not upload_dir.exists():
            self.logger.error(f"Upload directory not found: {upload_dir}")
            return processed_files
            
        for file_path in upload_dir.rglob('*'):
            if file_path.is_file():
                result = self.process_file(file_path)
                if result:
                    processed_files.append(result)
                    
        return processed_files
    
    def save_to_rag(self, processed_data: Dict) -> Optional[Path]:
        """
        Speichert verarbeitete Daten im RAG-Verzeichnis
        
        Args:
            processed_data: Verarbeitete Dateidaten
            
        Returns:
            Pfad zur gespeicherten Datei oder None bei Fehler
        """
        try:
            # Generate unique filename
            original_name = Path(processed_data['file_path']).stem
            unique_id = str(uuid.uuid4())[:8]
            rag_filename = f"{original_name}_{unique_id}.md"
            rag_path = self.config.RAG_DIR / rag_filename
            
            # Prepare content with metadata
            content = self._format_markdown_with_metadata(processed_data)
            
            # Save to file
            with open(rag_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.logger.info(f"Saved to RAG: {rag_path}")
            return rag_path
            
        except Exception as e:
            self.logger.error(f"Error saving to RAG: {str(e)}")
            return None
    
    def _generate_file_hash(self, file_path: Path) -> str:
        """Generiert SHA-256 Hash einer Datei"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
                
        return hash_sha256.hexdigest()
    
    def _extract_metadata(self, file_path: Path) -> Dict:
        """Extrahiert Metadaten aus einer Datei"""
        stat = file_path.stat()
        
        metadata = {
            'filename': file_path.name,
            'file_extension': file_path.suffix.lower(),
            'file_size': stat.st_size,
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'mime_type': mimetypes.guess_type(file_path)[0] or 'unknown'
        }
        
        return metadata
    
    def _convert_to_markdown(self, file_path: Path) -> Optional[str]:
        """Konvertiert Datei zu Markdown basierend auf Dateityp"""
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.pdf':
                return self._convert_pdf_to_markdown(file_path)
            elif file_extension == '.docx':
                return self._convert_docx_to_markdown(file_path)
            elif file_extension in ['.txt', '.md']:
                return self._convert_text_to_markdown(file_path)
            elif file_extension in ['.html', '.htm']:
                return self._convert_html_to_markdown(file_path)
            else:
                self.logger.warning(f"Unsupported file type: {file_extension}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error converting {file_path}: {str(e)}")
            return None
    
    def _convert_pdf_to_markdown(self, file_path: Path) -> Optional[str]:
        """Konvertiert PDF zu Markdown"""
        if PyPDF2 is None:
            self.logger.error("PyPDF2 not installed")
            return None
            
        try:
            text_content = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(f"## Seite {page_num + 1}\n\n{text}\n")
                        
            return '\n'.join(text_content)
            
        except Exception as e:
            self.logger.error(f"Error converting PDF {file_path}: {str(e)}")
            return None
    
    def _convert_docx_to_markdown(self, file_path: Path) -> Optional[str]:
        """Konvertiert DOCX zu Markdown"""
        if Document is None:
            self.logger.error("python-docx not installed")
            return None
            
        try:
            doc = Document(file_path)
            markdown_content = []
            
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    # Simple heading detection
                    if paragraph.style.name.startswith('Heading'):
                        level = int(paragraph.style.name[-1]) if paragraph.style.name[-1].isdigit() else 1
                        markdown_content.append(f"{'#' * level} {text}\n")
                    else:
                        markdown_content.append(f"{text}\n")
                        
            return '\n'.join(markdown_content)
            
        except Exception as e:
            self.logger.error(f"Error converting DOCX {file_path}: {str(e)}")
            return None
    
    def _convert_text_to_markdown(self, file_path: Path) -> Optional[str]:
        """Konvertiert Textdatei zu Markdown"""
        try:
            # Detect encoding
            encoding = 'utf-8'
            if chardet:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    detected = chardet.detect(raw_data)
                    if detected['encoding']:
                        encoding = detected['encoding']
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                
            # If already markdown, return as is
            if file_path.suffix.lower() == '.md':
                return content
                
            # Convert plain text to markdown
            lines = content.split('\n')
            markdown_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    # Simple heuristics for structure
                    if line.isupper() and len(line) < 100:
                        markdown_lines.append(f"## {line}\n")
                    else:
                        markdown_lines.append(f"{line}\n")
                else:
                    markdown_lines.append("\n")
                    
            return ''.join(markdown_lines)
            
        except Exception as e:
            self.logger.error(f"Error converting text {file_path}: {str(e)}")
            return None
    
    def _convert_html_to_markdown(self, file_path: Path) -> Optional[str]:
        """Konvertiert HTML zu Markdown"""
        if markdownify is None:
            self.logger.error("markdownify not installed")
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            markdown_content = markdownify(html_content, heading_style="ATX")
            return markdown_content
            
        except Exception as e:
            self.logger.error(f"Error converting HTML {file_path}: {str(e)}")
            return None
    
    def _format_markdown_with_metadata(self, processed_data: Dict) -> str:
        """Formatiert Markdown mit Metadaten Header"""
        metadata = processed_data['metadata']
        content = processed_data['markdown_content']
        
        header = f"""---
filename: {metadata['filename']}
file_hash: {processed_data['file_hash']}
file_size: {metadata['file_size']}
mime_type: {metadata['mime_type']}
created_at: {metadata['created_at']}
processed_at: {processed_data['processed_at']}
---

# {metadata['filename']}

{content}
"""
        return header
