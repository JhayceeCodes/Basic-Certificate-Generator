from fpdf import FPDF
from PIL import Image
import urllib.request, tempfile, os, io, sys, fitz

pdf = FPDF(orientation="landscape", format="A4")


class InvalidURL(Exception):
    pass


def set_background(cert_type, img_url=None):
    certTypesDefaultUrl = {
        "professional": "https://t3.ftcdn.net/jpg/01/89/21/08/360_F_189210844_HyfMEFOeXOSNvUBs3brT4lzVp5ox4NxC.jpg",
        "academic": "https://previews.123rf.com/images/andipanggeleng/andipanggeleng1706/andipanggeleng170600015/80860154-blank-certificate-template.jpg",
        "vocational": "https://e0.pxfuel.com/wallpapers/151/566/desktop-wallpaper-certificate-border-png-4-png-thumbnail.jpg",
        "other": "https://img.freepik.com/free-vector/decorative-frame-background-blue-vintage-flower-design-vector_53876-157569.jpg",
    }

    if pdf.page_no() == 0:
        pdf.add_page()

    if img_url is None:
        user_url = input(
            "Enter the path or URL of your desired background image (or leave blank for default): "
        )

        if not user_url:
            img_url = certTypesDefaultUrl[cert_type.lower()]
        elif user_url.startswith("http"):
            img_url = user_url
        else:
            img_url = os.path.abspath(user_url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        if img_url.startswith("http"):
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                img_data = response.read()
        else:
            with open(img_url, "rb") as local_img:
                img_data = local_img.read()
        try:
            img = Image.open(io.BytesIO(img_data))
        except Exception as e:
            print(f"Error identifying image format: {e}")
            sys.exit()
        converted_img_data = io.BytesIO()
        img.convert("RGB").save(converted_img_data, format="JPEG")
        img_data = converted_img_data.getvalue()
    except Exception:
        raise InvalidURL(
            "Unable to load the image. Using the default background for the chosen certificate type."
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
        temp_img.write(img_data)
        img_path = temp_img.name

    pdf.image(img_path, x=0, y=0, w=pdf.w, h=pdf.h)
    os.remove(img_path)
    return pdf


def certify(
    pdf,
    cert_type,
    header=None,
    body=None,
    font_size=None,
    position=None,
):
    fonts_n_size = {
        "professional": {"header_font": "times", "body_font": "times"},
        "academic": {"header_font": "courier", "body_font": "courier"},
        "vocational": {"header_font": "Helvetica", "body_font": "Helvetica"},
        "other": {"header_font": "arial", "body_font": "arial"},
    }

    default_size = 24

    header_font = fonts_n_size[cert_type]["header_font"]
    body_font = fonts_n_size[cert_type]["body_font"]

    header_size = font_size if font_size is not None else default_size
    body_size = font_size if font_size is not None else default_size

    pdf.set_font(header_font, size=header_size)

    while not header:
        header = input(
            "Certificate header required, please enter the header (e.g., Certificate of completion): "
        )

    pdf.set_font(body_font, size=body_size)

    while not body:
        body = input("Enter the certificate body: ")

    page_width = pdf.w

    text_width = pdf.get_string_width(header)
    text_height = pdf.font_size

    if position:
        x_header, y_header, x_body, y_body = position
    else:
        x_header = (page_width - text_width) / 2
        y_header = 40
        x_body = 20
        y_body = y_header + text_height + 10

    pdf.set_xy(x_header, y_header)
    pdf.cell(0, 10, header, ln=True, align="L")

    pdf.set_left_margin(20)
    pdf.set_right_margin(20)

    pdf.set_xy(x_body, y_body)
    pdf.multi_cell(page_width - 40, 10, body)

    return pdf


def set_position():
    try:
        x_header = float(input("Enter the x-coordinate position for the header: "))
        y_header = float(input("Enter the y-coordinate position for the header: "))
        x_body = float(input("Enter the x-coordinate position for the body: "))
        y_body = float(input("Enter the y-coordinate position for the body: "))
    except ValueError:
        print("Invalid input. Using default positions.")
        return

    return x_header, y_header, x_body, y_body


def set_type():
    print("Please select a certificate type:")
    print("1. Professional")
    print("2. Academic")
    print("3. Vocational")
    print("4. Other")
    user_input = int(input("Enter your choice: "))

    if user_input == 1:
        cert_type = "professional"
    elif user_input == 2:
        cert_type = "academic"
    elif user_input == 3:
        cert_type = "vocational"
    else:
        cert_type = "other"

    return cert_type


def get_font_size(prompt, default_size):
    user_input = input(f"{prompt} (or leave blank for default [{default_size}]): ")
    return int(user_input) if user_input else default_size


def convert_pdf_to_image(pdf_path, image_path):
    pdf_document = fitz.open(pdf_path)
    images_path = []

    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        image = page.get_pixmap()
        image.save(image_path.format(page_number + 1), "png")

    pdf_document.close()
    return images_path



def main():
    cert_type = set_type()
    pdf = set_background(cert_type)
    position = set_position()
    font_size = get_font_size("Enter the certificate font size", 24)
    certify(pdf, cert_type, position=position, font_size=font_size)

    pdf_path = "certificate.pdf"
    pdf.output(pdf_path)

    image_path = "certificate.png"
    convert_pdf_to_image(pdf_path, image_path)

    print(f"Certificate PDF saved to {pdf_path}")
    print(f"Certificate image saved to {image_path}")


if __name__ == "__main__":
    main()
