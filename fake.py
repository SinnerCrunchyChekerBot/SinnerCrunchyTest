import random
from faker import Faker
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

fake = Faker("en_US")

def generate_fake_details():
    name = fake.name()
    street_address = fake.street_address()
    city = fake.city()
    state = fake.state()
    province = state  # In the US, states function similarly to provinces
    country = "United States"
    zip_code = fake.zipcode()
    phone = fake.phone_number()
    email = fake.email()
    dob = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d")

    # Generating a fake SSN
    ssn = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

    return (
        "🆔 <b>𝗙𝗮𝗸𝗲 𝗨𝗦 𝗔𝗱𝗱𝗿𝗲𝘀𝘀 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱:</b>\n\n"
        f"👤 <b>Name:</b> <code>{name}</code>\n"
        f"🏠 <b>Street Address:</b> <code>{street_address}</code>\n"
        f"🏙 <b>City:</b> <code>{city}</code>\n"
        f"🌆 <b>State:</b> <code>{state}</code>\n"
        f"🏢 <b>Province:</b> <code>{province}</code>\n"
        f"🌍 <b>Country:</b> <code>{country}</code>\n"
        f"📮 <b>Zip Code:</b> <code>{zip_code}</code>\n"
        f"📞 <b>Phone:</b> <code>{phone}</code>\n"
        f"📧 <b>Email:</b> <code>{email}</code>\n"
        f"🎂 <b>Date of Birth:</b> <code>{dob}</code>\n"
        f"🆔 <b>SSN:</b> <code>{ssn}</code>\n\n"
        "<b>Bot ~ 𝗦𝓲𝓷𝓷𝓮𝓻✘Checker</b>"
    )

def fake_command(update: Update, context: CallbackContext):
    fake_details = generate_fake_details()
    update.message.reply_text(fake_details, parse_mode="HTML")


