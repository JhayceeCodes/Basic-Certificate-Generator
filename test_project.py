import pytest, tempfile, os
from fpdf import FPDF
from project import (
    set_background,
    certify,
    set_position,
    set_type,
    get_font_size,
    convert_pdf_to_image,
    InvalidURL,
)


def set_background_with_new_page(cert_type, img_url=None):
    pdf = set_background(cert_type, img_url=img_url)
    pdf.add_page()
    return pdf


def create_non_empty_pdf(pdf_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="This is a non-empty PDF for testing.", ln=True, align="C")
    pdf.output(pdf_path)


def test_set_background(monkeypatch):
    user_input = iter([""])
    monkeypatch.setattr("builtins.input", lambda _: next(user_input))
    pdf = set_background_with_new_page("professional", img_url=None)
    assert pdf is not None


def test_set_background_with_provided_image(monkeypatch):
    user_input = (
        "https://i.pinimg.com/1200x/04/c1/2e/04c12e23ef79779a75bfd062df7dc920.jpg"
    )
    monkeypatch.setattr("builtins.input", lambda _: user_input)
    pdf = set_background_with_new_page("professional", img_url=user_input)
    assert pdf is not None


def test_set_background_with_invalid_image_url(monkeypatch):
    user_input = "https://www.example.com/invalid_image.jpg"
    monkeypatch.setattr("builtins.input", lambda _: user_input)
    with pytest.raises(InvalidURL) as exc_info:
        set_background_with_new_page("professional", img_url=user_input)
    assert (
        str(exc_info.value)
        == "Unable to load the image. Using the default background for the chosen certificate type."
    )


def test_set_background_with_invalid_image_format(monkeypatch, capsys):
    user_input = "https://www.google.com.ng/imgres?imgurl=https%3A%2F%2Fpng.pngtree.com%2Fthumb_back%2Ffh260%2Fback_pic%2F04%2F47%2F51%2F665858c95c31b60.jpg&tbnid=VscSRJxWWOKBNM&vet=12ahUKEwikt5fxq4eDAxXWmicCHU8_CjMQMygBegQIARBz..i&imgrefurl=https%3A%2F%2Fpngtree.com%2Ffree-backgrounds-photos%2Fcertificate&docid=I3XD7ROtYOuS3M&w=364&h=260&q=blank%20certificate%20background%20hd&ved=2ahUKEwikt5fxq4eDAxXWmicCHU8_CjMQMygBegQIARBz"
    monkeypatch.setattr("builtins.input", lambda _: user_input)
    with pytest.raises(SystemExit) as e:
        set_background_with_new_page("professional", img_url=user_input)

    captured = capsys.readouterr()
    assert "Error identifying image format:" in captured.out


def test_set_position(monkeypatch):
    user_inputs = ["100", "150", "50", "200"]
    monkeypatch.setattr("builtins.input", lambda _: user_inputs.pop(0))

    result = set_position()

    assert result == (100.0, 150.0, 50.0, 200.0)


def test_set_position_invalid_input(monkeypatch, capsys):
    user_inputs = ["100", "", "", ""]
    monkeypatch.setattr("builtins.input", lambda _: user_inputs.pop(0))

    result = set_position()

    assert result == None


def test_set_type(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")

    result = set_type()

    assert result == "professional"


def test_get_font_size(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "18")

    result = get_font_size("Enter the font size", 12)

    assert result == 18


def test_get_font_size_blank_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")

    result = get_font_size("Enter the font size", 12)

    assert result == 12


def test_get_font_size_empty_input_use_default(monkeypatch):
    user_input = ""
    monkeypatch.setattr("builtins.input", lambda _: user_input)

    result = get_font_size("Enter the font size", 24)

    assert result == 24


def test_convert_pdf_to_image():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
        pdf_path = pdf_file.name
        create_non_empty_pdf(pdf_path)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as image_file:
        image_path = image_file.name

    assert convert_pdf_to_image(pdf_path, image_path) is not None

    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    if os.path.exists(image_path):
        os.remove(image_path)


def test_certify():
    # Create a temporary PDF file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
        pdf_path = pdf_file.name
        create_non_empty_pdf(pdf_path)

    cert_type = "professional"
    header = "test header"
    body = "test body"
    font_size = None
    position = None

    with open(pdf_path, "wb") as pdf_file:
        pdf = FPDF()
        pdf.add_page()
        pdf_file.write(pdf.output(dest="S").encode("latin1"))

        pdf = certify(pdf, cert_type, header, body, font_size, position)

    assert pdf is not None
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
