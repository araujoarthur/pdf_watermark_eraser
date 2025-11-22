import pymupdf
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(
    prog="Manning PDF License Eraser",
    description="Aims to remove 'Licensed to John Doe <john@doe.com>' text from Manning True PDFs")

parser.add_argument('input', type=str)
parser.add_argument('output', type=str)
parser.add_argument('license_text', type=str)


def main():
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