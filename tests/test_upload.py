
from routes.upload import allowed_file


def test_pdf_allowed():

    assert allowed_file("document.pdf") is True


def test_docx_allowed():

    assert allowed_file("report.docx") is True


def test_png_allowed():

    assert allowed_file("image.png") is True


def test_jpg_allowed():

    assert allowed_file("photo.jpg") is True


def test_zip_allowed():

    assert allowed_file("archive.zip") is True


def test_unsupported_extension():

    assert allowed_file("program.exe") is False


def test_missing_extension():

    assert allowed_file("document") is False


def test_empty_filename():

    assert allowed_file("") is False


def test_hidden_filename():

    assert allowed_file(".pdf") is False
