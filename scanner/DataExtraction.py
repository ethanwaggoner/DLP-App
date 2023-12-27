import aiofiles
import PyPDF2
import pandas as pd
import docx
import mimetypes


class DataExtract:

    @staticmethod
    async def from_pdf(file_path):
        try:
            async with aiofiles.open(file_path, 'rb') as pdf_file:
                content = await pdf_file.read()
            pdf_reader = PyPDF2.PdfReader(content)
            text = ''.join(page.extract_text() for page in pdf_reader.pages)
            return text
        except (FileNotFoundError, PyPDF2.errors.PdfReadError) as e:
            return f"PDF Error: {e}"

    @staticmethod
    async def from_csv(file_path):
        try:
            data = pd.read_csv(file_path)
            return data.to_string()
        except (FileNotFoundError, pd.errors.ParserError) as e:
            return f"CSV Error: {e}"

    @staticmethod
    async def from_excel(file_path):
        try:
            data = pd.read_excel(file_path)
            return data.to_string()
        except (FileNotFoundError, ValueError) as e:
            return f"Excel Error: {e}"

    @staticmethod
    async def from_txt(file_path):
        try:
            async with aiofiles.open(file_path, 'r') as file:
                text = await file.read()
            return text
        except FileNotFoundError as e:
            return f"Text File Error: {e}"

    @staticmethod
    async def from_word(file_path):
        try:
            doc = docx.Document(file_path)
            text = '\n'.join(paragraph.text for paragraph in doc.paragraphs)
            return text
        except (FileNotFoundError, docx.opc.exceptions.PackageNotFoundError) as e:
            return f"Word File Error: {e}"

    @staticmethod
    async def determine_mime_type(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type

    @staticmethod
    async def from_file(file_path):
        mime_type = await DataExtract.determine_mime_type(file_path)
        if mime_type is None:
            return "Error: Unable to determine the file type."

        if mime_type == "application/pdf":
            return await DataExtract.from_pdf(file_path)
        elif mime_type == "text/csv":
            return await DataExtract.from_csv(file_path)
        elif mime_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            return await DataExtract.from_excel(file_path)
        elif mime_type == "text/plain":
            return await DataExtract.from_txt(file_path)
        elif mime_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            return await DataExtract.from_word(file_path)
        else:
            return f"Error: Unsupported file type '{mime_type}'."
