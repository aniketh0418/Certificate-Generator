import streamlit as st
from pymongo import MongoClient
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
from dotenv import load_dotenv
import os

# Set the app configuration
st.set_page_config(
    page_title="Certificates@GenAI",
    page_icon="icon.png", 
    layout="centered",    
    initial_sidebar_state="auto"
)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Loading the configurations
load_dotenv("config.env")

# MongoDB connection details
MONGO_URI = os.getenv('db_uri')
DB_NAME = os.getenv('db_name')
DB_COLLECTION = os.getenv('db_collection')
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[DB_COLLECTION]

# Getting collection data
NAME = os.getenv('col1')
EMAIL = os.getenv('col2')
URL = os.getenv('col3')
VALIDATION = os.getenv('col4')

# Function to generate PNG certificate in memory
def generate_certificate(user):
    template = Image.open("temp.png")
    draw = ImageDraw.Draw(template)
    
    user_name_with_password = f"{user[NAME]}"
    
    # Load the Tangerine font
    font_path = "Tangerine-Regular.ttf"
    font = ImageFont.truetype(font_path, 500)
    
    bbox = font.getbbox(user_name_with_password)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_x = (template.width - text_width) // 2
    text_y = 1950
    
    draw.text((text_x, text_y), user_name_with_password, fill="black", font=font)
    
    qr = qrcode.make(user[URL])
    qr = qr.resize((950, 950))
    
    qr_x = template.width - 1050
    qr_y = template.height - 1050
    template.paste(qr, (qr_x, qr_y))
    
    # Save image to a BytesIO object
    img_byte_arr = BytesIO()
    template.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    
    return img_byte_arr, template

# Function to convert PNG to PDF in memory
def convert_png_to_pdf(png_image):
    img = png_image.convert("RGB")
    if img.width < img.height:
        img = img.rotate(90, expand=True)

    pdf_buffer = BytesIO()
    img.save(pdf_buffer, "PDF", resolution=100.0)
    pdf_buffer.seek(0)
    return pdf_buffer
# Web App UI
st.title("Google Cloud Gen AI Study Jams")
st.write("Enter your Study Jams registered Email ID and Name to download your certificate. Your certificate will be available if you have successfully completed the Jams. Contact Team GDG on Campus HITAM for any issues.")

email = st.text_input("Email", placeholder="Enter your email")
name = st.text_input("Name", placeholder="Enter your name (Password)")

# Web App Functionality
if st.button("Generate Certificate"):
    user = collection.find_one({EMAIL: email, NAME: name})
    if user:
        # Check if the user has completed the Jams
        if user.get(VALIDATION) == "y":
            st.success("Credentials Verified! Your certificate preview here 👇🏻")
            
            # Generate certificate
            certificate_buffer, certificate_image = generate_certificate(user)
            st.image(certificate_image, caption="(If you have any issue related your to certificate contact to Team GDG - HITAM)")
            pdf_output = convert_png_to_pdf(certificate_image)
            
            # Download Certificate
            st.download_button(
                label="Download Certificate 📝",
                data=pdf_output,
                file_name="Certificate@GenAI.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("Credentials Verified, But you have not completed the Jams yet!")
    else:
        st.error("Invalid credentials! Please try again.")
st.markdown("""
## Join us 🙋🏻:
- [Global Community 🌐](https://gdg.community.dev/gdg-on-campus-hyderabad-institute-of-technology-and-management-hyderabad-india/)
- [Instagram 🤝](https://www.instagram.com/gdg.on.campus_hitam?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==)
- [WhatsApp 🔗](https://chat.whatsapp.com/HM6ZTfIHMBK1mIY8WXNIct)
""")
st.write("Made with ❤️ by GDG on Campus HITAM @AniR")
