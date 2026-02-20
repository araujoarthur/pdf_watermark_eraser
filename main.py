import pymupdf
import argparse
from pathlib import Path
import json

parser = argparse.ArgumentParser(
    prog="PDF Watermark Eraser",
    description="Aims to remove specific Watermark Strings from PDFs")

parser.add_argument('-p', '--plan', type=str, help="path for the 'plan.json' file")

def readPlan(plan: str):
    plan_path = Path(plan)
    if not (plan_path.exists() and plan_path.is_file()):
        raise FileNotFoundError(f"the path '{plan_path}' was not found.")
    
    plan_data = {}
    with open(plan_path, "r", encoding="utf-8") as f:
        plan_data = json.load(f)
    
    return plan_data


def old_main():
    args = parser.parse_args()
    

    inp, outp, lic = Path(args.input).resolve(), Path(args.output).resolve(), Path(args.license_text).resolve()

    if not Path(inp).exists():
        raise FileNotFoundError(f"the file '{inp}' was not found.")

    if not Path(outp).parent.exists():
        raise NotADirectoryError(f"the directory passed to the output '{outp}' is not valid.")
    
    if not Path(lic).exists():
        raise FileNotFoundError(f"the file containing license text '{lic}' was not found.")
    
    with open(lic, "r", encoding="utf8") as fd:
        lines = fd.readlines()
        if len(lines) > 1:
            raise ValueError(f"unexpectedly high number of lines in the license text file")
        lic_text = lines[0].strip().strip("\n")

    redact_lic(
        inp,
        outp,
        lic_text
    )

def main():
    args = parser.parse_args()
    
    plan_path = Path(args.plan).resolve() if (args.plan and Path(args.plan).exists()) else Path.cwd() / 'plan.json'

    if not plan_path.exists():
        print("FAILED: no path plan was given and there's no plan.json in the current working folder")
        exit()

    plan = readPlan(plan_path)

    planOptions = {}
    # single = root is a file directly; multi = root is a folder with multiple files/folders
    planOptions['running_mode'] = plan['rootMode'].lower() if ('rootMode' in plan) else 'single'
    # only useful if running_mode is 'multi'. 
    # folderMode can be:
    #  "list", meaning the root folder itself contains multiple files
    #  "parenting_singles", meaning the root folder is parent of other folders with one file each
    #  "parenting_multi", meaning the root folder is parent of other folders containing subfolders and files.
    planOptions['folder_mode'] = plan['folderMode'].lower() if ('folderMode' in plan) else 'parenting_multi'

    planOptions['delete_original'] = plan['deleteOriginal'] if ('deleteOriginal' in plan) else False

    planOptions['continue_even_if_exists'] = plan['ignoreOutputPathIntegrity'] if ('ignoreOutputPathIntegrity' in plan) else False

    root_input_path = Path(plan['rootInputPath']).resolve()
    if not root_input_path.exists():
        print("input root path not Found")
        exit()
    elif planOptions['running_mode'] == 'single' and (not root_input_path.is_file()):
        print("the running mode is set to 'SINGLE', but the rootInputPath is not a file")
        exit()
    elif planOptions['running_mode'] != 'single' and (not root_input_path.is_dir()):
        print("the running mode is set to 'MULTI', but the rootInputPath is not a folder")
        exit()

    output_path = Path(plan['outputPath']).resolve()
    if output_path.exists():
        if not planOptions['continue_even_if_exists']:
            print("the output path already exists, set the option 'ignoreOutputPathIntegrity' to true to continue anyways")
            exit()
        
        if planOptions['running_mode'] != 'single' and output_path.is_file():
            print("the output path is a file, but the running mode is not 'single'")
            exit()
    
    disallowed_folders = plan['excludedFolderNames'] if ('excludedFolderNames' in plan) else [] 
    redaction_texts = plan['redactionTexts'] if ('redactionTexts' in plan) else None
    if not redaction_texts:
        print("there are no texts to redact.")
        exit()
    
    # Yes, the excludedFolderNames expect only the name of the folders.
    folders = [p for p in root_input_path.iterdir() if (p.is_dir() and p.name not in disallowed_folders)]

    redact_strategy = select_redact_strategy(planOptions)
    redact_strategy(output_path, folders, root_input_path)

    ...

    for folder in folders:
        pdfs = [p for p in folder.iterdir() if (p.is_file() and p.suffix.lower() == ".pdf")]
        if len(pdfs) > 1:
            print(f"Something is wrong, {folder.name} has more than one PDF file inside")
            continue
        
        if len(pdfs) == 0:
            print(f"Something is wrong, {folder.name} has no PDF files inside")
            continue
            
        pdf_file = pdfs.pop()

        subpath = folder / pdf_file.stem
        subpath.mkdir()

        output_redacted_file = subpath / (pdf_file.stem + "_r.pdf")

        multiredact(pdf_file.resolve(), output_redacted_file.resolve(), redaction_texts)
        pdf_file.unlink()

        print(f"File {pdf_file.stem} redacted and removed.")


def select_redact_strategy(popts):
    pass

def strategy_single_file(output_path, **kwargs):
    """
    Docstring for strategy_single_file
    
    :param folders: Description
    :param output_path: Description

    This assumes the root input path refers to a file.
    """
    file_path = kwargs.get('root_input_path')
    if file_path == None:
        raise TypeError('invalid argument for the selected strategy; could not get file path')

    if not file_path.exists():
        raise FileNotFoundError(f"the file '{file_path}' was not found.")
    
    ...
    



def multiredact(in_pdf, out_pdf, texts):
    doc = pymupdf.open(in_pdf)

    for page in doc.pages():
        for text in texts:
            occurences = page.search_for(text)
            for occ in occurences:
                page.add_redact_annot(occ.quad, fill=None)

        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
    
    doc.save(out_pdf, garbage=4, deflate=True)
    doc.close()

def redact_lic(in_pdf, out_pdf, txt):
    doc = pymupdf.open(in_pdf)
    for page in doc.pages():
        occurences = page.search_for(txt)
        for occ in occurences:
            page.add_redact_annot(occ.quad, fill=None)
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
    
    doc.save(out_pdf)
    doc.close()
    print("Successful!")
main()