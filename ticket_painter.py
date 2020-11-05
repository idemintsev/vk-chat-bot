import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

PATH_TO_TICKET_TEMPLATE = os.path.join(os.path.dirname(__file__), 'files', 'ticket_template.jpg')
PATH_TO_FONT = os.path.join(os.path.dirname(__file__), 'files', 'Ubuntu-Regular.ttf')
FONT_SIZE = 20
BLACK = (0, 0, 0, 255)
NAME_POSITION = (370, 300)
EMAIL_POSITION = (370, 345)


def get_ticket(name: str, email: str):
    ticket_template = Image.open(PATH_TO_TICKET_TEMPLATE)
    font = ImageFont.truetype(PATH_TO_FONT, FONT_SIZE)
    text_drawer = ImageDraw.Draw(ticket_template)
    text_drawer.text(NAME_POSITION, name, font=font, fill=BLACK)
    text_drawer.text(EMAIL_POSITION, email, font=font, fill=BLACK)

    temp_file = BytesIO()
    ticket_template.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file
