#!/usr/bin/env python3
"""
pdf_ocr.py by Neil Grogan, 2020

A script to run convert PDFs from scanner to PDF/A with embedded text via OCR

Prerequisities:
===============
* Install Docker
* Install watchdog Python library: $ pip install watchdog
$ docker pull jbarlow83/ocrmypdf
$ docker tag jbarlow83/ocrmypdf ocrmypdf
"""
import sys
import os
import shutil
import tempfile
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

    def process(self, src_path):
        """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        if should_process(src_path):
            print('Processing: ', src_path)
            now = datetime.today().strftime('%y-%m-%d')
            file_name = str(Path(src_path).stem)
            par_dir = Path(src_path).parent.resolve()
            final_dir = str(par_dir.joinpath(now +'_{}.pdf'.format(file_name)))
            tmp_path = str(tempfile.NamedTemporaryFile().name)
            #ocrmypdf.ocr(event.src_path, new_path, force_ocr=True,)
            cur_path = str(Path(src_path).resolve())
            s = subprocess.run(["docker run --rm -i ocrmypdf --force-ocr --deskew - - <" + cur_path + " >"+tmp_path], shell=True)

            if s.returncode == 0:
                shutil.move(tmp_path,  final_dir)
        else:
            print('Noting to process', src_path)
        

    def on_moved(self, event):
        print('Moved: ', event)
        path = str(event.dest_path)
        if should_process(path):
            self.process(event.dest_path)

    def on_modified(self, event):
        print('Modified: ', event)
        if should_process(event.src_path):
            self.process(event.src_path)

    def on_created(self, event):
        print('Created: ', event)
        if should_process(event.src_path):
            self.process(event.src_path)

def should_process(path):
    p = str(Path(path).stem)
    if path.endswith('pdf') or path.endswith('PDF'):
        if p.startswith('Scan') or p.startswith('IMG'):
            return True
    return False

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
