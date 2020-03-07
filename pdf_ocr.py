#!/usr/bin/env python3
"""
pdf_ocr.py by Neil Grogan, 2020

A script to run convert PDFs from scanner to PDF/A with embedded text via OCR
"""
import sys
from datetime import datetime
from pathlib import Path
import subprocess
import time
import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
#import ocrmypdf


class PDFHandler(PatternMatchingEventHandler):
    patterns = ["*.PDF", "*.pdf"]

    def process(self, event):
        """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        src_path = event.src_path
        if event.event_type is 'moved':
            print(src_path, event.dest_path)
            src_path = event.dest_path
            

        print(src_path, event.event_type)

        # the file will be processed there
        if "Scan" or "IMG" in event.src_path:
            now = datetime.today().strftime('%y-%m-%d')
            new_path = str(Path(src_path).parent) + '/' +now +'.pdf'
            #ocrmypdf.ocr(event.src_path, new_path, force_ocr=True,)
            cur_path = str(Path(src_path).resolve())
            subprocess.run(["docker run --rm -i ocrmypdf - - <" + cur_path + " >\""+new_path+"\""], shell=True)
        

    def on_moved(self, event):
        self.process(event)

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
