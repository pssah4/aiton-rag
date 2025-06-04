"""
File Watcher Service for AITON-RAG

Monitors the upload directory for new files and automatically processes them
through the FileProcessor and Aggregator services.
"""

import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import Set, Optional
import threading

from .file_processor import FileProcessor
from .aggregator import Aggregator
from config import Config

class FileWatcherHandler(FileSystemEventHandler):
    """Handler for file system events in the upload directory."""
    
    def __init__(self, file_processor: FileProcessor, aggregator: Aggregator):
        self.file_processor = file_processor
        self.aggregator = aggregator
        self.processing_files: Set[str] = set()
        self.logger = logging.getLogger(__name__)
        
        # Supported file extensions
        self.supported_extensions = {'.pdf', '.docx', '.txt', '.html', '.md', '.htm'}
        
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            self._process_file(event.src_path)
    
    def on_moved(self, event):
        """Handle file move events."""
        if not event.is_directory:
            self._process_file(event.dest_path)
    
    def _process_file(self, file_path: str):
        """Process a new file if it's supported and not already being processed."""
        try:
            path = Path(file_path)
            
            # Check if file extension is supported
            if path.suffix.lower() not in self.supported_extensions:
                self.logger.debug(f"Skipping unsupported file: {file_path}")
                return
            
            # Check if file is already being processed
            if file_path in self.processing_files:
                self.logger.debug(f"File already being processed: {file_path}")
                return
            
            # Add to processing set
            self.processing_files.add(file_path)
            
            # Wait a moment to ensure file is fully written
            time.sleep(1)
            
            # Start processing in a separate thread
            thread = threading.Thread(
                target=self._process_file_async,
                args=(file_path,),
                daemon=True
            )
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Error handling file event for {file_path}: {e}")
            if file_path in self.processing_files:
                self.processing_files.remove(file_path)
    
    def _process_file_async(self, file_path: str):
        """Asynchronously process a file."""
        try:
            self.logger.info(f"Processing new file: {file_path}")
            
            # Process the file
            result = self.file_processor.process_file(file_path)
            
            if result['success']:
                self.logger.info(f"Successfully processed file: {file_path}")
                
                # Trigger aggregation update
                self.aggregator.update_knowledge_base()
                self.logger.info("Updated knowledge base after file processing")
                
                # Optionally remove the original file from uploads
                if Config.DELETE_AFTER_PROCESSING:
                    try:
                        os.remove(file_path)
                        self.logger.info(f"Removed processed file: {file_path}")
                    except Exception as e:
                        self.logger.warning(f"Could not remove processed file {file_path}: {e}")
            else:
                self.logger.error(f"Failed to process file {file_path}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
        finally:
            # Remove from processing set
            if file_path in self.processing_files:
                self.processing_files.remove(file_path)

class FileWatcher:
    """Main file watcher service."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.observer: Optional[Observer] = None
        self.file_processor = FileProcessor()
        self.aggregator = Aggregator()
        
        # Ensure upload directory exists
        Config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        self.handler = FileWatcherHandler(self.file_processor, self.aggregator)
        
    def start(self):
        """Start watching the upload directory."""
        try:
            if self.observer and self.observer.is_alive():
                self.logger.warning("File watcher is already running")
                return
            
            self.observer = Observer()
            self.observer.schedule(
                self.handler,
                str(Config.UPLOAD_DIR),
                recursive=False
            )
            
            self.observer.start()
            self.logger.info(f"Started file watcher on directory: {Config.UPLOAD_DIR}")
            
        except Exception as e:
            self.logger.error(f"Failed to start file watcher: {e}")
            raise
    
    def stop(self):
        """Stop the file watcher."""
        try:
            if self.observer and self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
                self.logger.info("Stopped file watcher")
            
        except Exception as e:
            self.logger.error(f"Error stopping file watcher: {e}")
    
    def is_running(self) -> bool:
        """Check if the file watcher is currently running."""
        return self.observer is not None and self.observer.is_alive()
    
    def process_existing_files(self):
        """Process any existing files in the upload directory."""
        try:
            upload_files = list(Config.UPLOAD_DIR.glob('*'))
            supported_files = [
                f for f in upload_files 
                if f.is_file() and f.suffix.lower() in self.handler.supported_extensions
            ]
            
            if not supported_files:
                self.logger.info("No existing files to process in upload directory")
                return
            
            self.logger.info(f"Processing {len(supported_files)} existing files")
            
            for file_path in supported_files:
                self.handler._process_file_async(str(file_path))
            
            # Wait for processing to complete
            time.sleep(2)
            while self.handler.processing_files:
                time.sleep(1)
            
            self.logger.info("Finished processing existing files")
            
        except Exception as e:
            self.logger.error(f"Error processing existing files: {e}")

def create_watcher() -> FileWatcher:
    """Factory function to create a FileWatcher instance."""
    return FileWatcher()

if __name__ == "__main__":
    # Configure logging for standalone testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start the watcher
    watcher = create_watcher()
    
    try:
        # Process existing files first
        watcher.process_existing_files()
        
        # Start watching
        watcher.start()
        
        print("File watcher started. Press Ctrl+C to stop...")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping file watcher...")
        watcher.stop()
    except Exception as e:
        print(f"Error: {e}")
        watcher.stop()
