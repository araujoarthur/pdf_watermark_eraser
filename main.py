import pymupdf
import argparse
from pathlib import Path
import json
from consts import get_help_text
from plan import RedactionPlan

parser = argparse.ArgumentParser(
    prog="PDF Watermark Eraser",
    description="Aims to remove specific Watermark Strings from PDFs")

parser.add_argument('-p', '--plan', type=str, help="path for the 'plan.json' file")

def old_main():
    """
    @Deprecated
    """
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

    redact_str(
        inp,
        outp,
        lic_text
    )

def main():
    args = parser.parse_args()
    
    plan_path = Path(args.plan).resolve() if (args.plan and Path(args.plan).exists()) else Path.cwd() / 'plan.json'

    if not plan_path.exists():
        print(f"FAILED: no path plan was given and there's no plan.json in the current working folder{get_help_text}")
        exit()

    plan = RedactionPlan(plan_path)

    # Yes, the excludedFolderNames expect only the name of the folders.
    # Do I really need to (or even CAN) do this HERE?
    #folders = [p for p in root_input_path.iterdir() if (p.is_dir() and p.name not in disallowed_folders)]

    redaction = select_redact_strategy(plan)
    redaction()
    #redact_strategy(...) # Run the strat

    # ... I believe the code below is to be discarded as the redact_strategy
    # must implement the file redaction.
    # The code below describes a Root with multiple folders (rootMode: Multi)
    # where each folder has multiple files

    #for folder in folders:
    #    pdfs = [p for p in folder.iterdir() if (p.is_file() and p.suffix.lower() == ".pdf")]
    #    if len(pdfs) > 1:
    #        print(f"Something is wrong, {folder.name} has more than one PDF file inside")
    #        continue
        
    #    if len(pdfs) == 0:
    #        print(f"Something is wrong, {folder.name} has no PDF files inside")
    #        continue
            
    #    pdf_file = pdfs.pop()

    #    subpath = folder / pdf_file.stem
    #    subpath.mkdir()

    #    output_redacted_file = subpath / (pdf_file.stem + "_r.pdf")

    #    multiredact(pdf_file.resolve(), output_redacted_file.resolve(), redaction_texts)
    #    pdf_file.unlink()

    #    print(f"File {pdf_file.stem} redacted and removed.")


def multiredact(in_pdf, out_pdf, texts):
    """
    Redacts all occurrences of multiple different strings
    in a PDF file and saves it to a new PDF file.

    :param in_pdf: Name/path of the input pdf
    :param out_pdf: Name/path of the output pdf
    :param texts: Strings to look for and redact
    """
    doc = pymupdf.open(in_pdf)

    for page in doc.pages():
        for text in texts:
            occurences = page.search_for(text)
            for occ in occurences:
                page.add_redact_annot(occ.quad, fill=None)

        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
    
    doc.save(out_pdf, garbage=4, deflate=True)
    doc.close()


def redact_str(in_pdf, out_pdf, txt):
    """
    Redacts all occurences of a single string in a PDF file
    and saves the output to a new PDF file.

    :param in_pdf: Description
    :param out_pdf: Description
    :param txt: Description
    """
    doc = pymupdf.open(in_pdf)
    for page in doc.pages():
        occurences = page.search_for(txt)
        for occ in occurences:
            page.add_redact_annot(occ.quad, fill=None)
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
    
    doc.save(out_pdf)
    doc.close()
    print("Successful!")


def strategy_single_file(popts: RedactionPlan):
    """
    This strategy assumes the root input path refers to a file.
    """
    def strategy():
        file_path = popts.root_input_path()
        if file_path == None:
            raise TypeError('invalid argument for the selected strategy; could not get file path')

        if not file_path.exists():
            raise FileNotFoundError(f"the file '{file_path}' was not found.")
        
        output_path = popts.output_path()
        if output_path == None:
            raise TypeError("invalid argument for the selected strategy; could not get output path")
        
        multiredact(file_path, output_path, popts.redaction_texts())

    return strategy



STRATEGIES = {
    "single:single": strategy_single_file,
    "multi:list": None,
    "multi:parenting": None,
    "multi:recursive": None
}

def select_redact_strategy(popts: RedactionPlan):
    """
    Selects the right builder for the strategy and dispatch the correct strategy as function

    Possible strategies are
        - root_mode == "single" && folder_mode == "single" -> strategy_single_file(...)
        - root_mode == "multi" && folder_mode == "list" -> strategy_multi_file(...)
        - root_mode == "multi" && folder_mode == "parenting" -> strategy_multi_folder_files(...)
        - root_mode == "multi" && folder_mode == "recursive" -> strategy_recursive(...)
    
    :param popts: Plan Options

    """

    qualified_strategy = f"{popts.root_mode()}:{popts.folder_mode()}"

    if qualified_strategy in STRATEGIES:
        return STRATEGIES[qualified_strategy](popts)
    else:
        raise RuntimeError("no strategy found for the given plan")


if __name__ == "__main__":
    main()