#!/usr/bin/env python3

import argparse
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os
import requests
import random
import shutil


@dataclass
class DocumentData:
    mixed_doc_uuid: str
    mixed_doc_page_number: int
    mixed_doc_name: str
    uploaded_doc_uuid: str
    uploaded_doc_page_number: int
    uploaded_doc_name: str
    description: str
    datetime: str
    doc_type: str

def get_random_name():
    words = requests.get('https://www.mit.edu/~ecprice/wordlist.10000').content.splitlines()
    return str(random.choice(words))

def make_text_file(filename, data):
    with open('%s.txt' % filename, 'w') as f:
        f.write(json.dumps(asdict(data), indent=4))

def convert_text_file_to_pdf_file(filename):
    os.system('convert TEXT:%s.txt -page Letter %s.pdf' % (filename, filename))

def join_pdf_files(filenames, uuid):
    os.system('pdftk %s cat output %s.pdf' % (' '.join(['%s.pdf' % f for f in filenames]), uuid))

def cleanup(filenames):
    for f in filenames:
        os.system('rm %s.txt' % f)
        os.system('rm %s.pdf' % f)

# Check Support

imagemagick_path = shutil.which('convert')
if imagemagick_path == None:
    raise Exception('Imagemagick not found.')

pdftk_path = shutil.which('pdftk')
if pdftk_path == None:
    raise Exception('PDF-Toolkit not found.')

# Execution
parser = argparse.ArgumentParser(description='Generate a PDF.')

parser.add_argument('--description', type=str, help='Document description.')

parser.add_argument('--docs', type=str, nargs='+', help='Document builder (bs, ps, fm).')

args = parser.parse_args()

mixed_doc_uuid = str(uuid.uuid4())
mixed_doc_page_number = 1
mixed_doc_name = get_random_name()
datetime = str(datetime.now())
description = args.description

doc_type_map = {
    'bs': 'Bank Statement',
    'ps': 'Paystub',
    'fm': 'Form',
}

filenames = []
for doc in args.docs:
    doc_type, page_count = doc.split(':')
    uploaded_doc_uuid = str(uuid.uuid4())
    uploaded_doc_page_number = 1
    uploaded_doc_name = get_random_name()
    for _ in range(int(page_count)):
        doc_data = DocumentData(
            mixed_doc_uuid = mixed_doc_uuid,
            mixed_doc_page_number = mixed_doc_page_number,
            mixed_doc_name = mixed_doc_name,
            uploaded_doc_uuid = uploaded_doc_uuid,
            uploaded_doc_page_number = uploaded_doc_page_number,
            uploaded_doc_name = uploaded_doc_name,
            description = description,
            datetime = datetime,
            doc_type = doc_type_map[doc_type],
        )

        filename = '%s_%d' % (mixed_doc_uuid, mixed_doc_page_number)
        make_text_file(filename, doc_data)
        convert_text_file_to_pdf_file(filename)
        filenames.append(filename)

        uploaded_doc_page_number += 1
        mixed_doc_page_number += 1

join_pdf_files(filenames, mixed_doc_uuid)
cleanup(filenames)
