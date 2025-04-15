import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from resume_parser import ResumeParser

app = FastAPI()
engine = ResumeParser()


@app.post("/scrape")
async def scrape_pdf(pdf_file: UploadFile = File(...)):
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF.")

    file_contents = await pdf_file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_contents)
        tmp_filepath = tmp.name

    try:
        result = engine.parse(tmp_filepath)
    finally:
        os.remove(tmp_filepath)

    return {"filename": pdf_file.filename, "result": result}