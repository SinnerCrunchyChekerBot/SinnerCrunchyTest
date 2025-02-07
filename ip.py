import httpx
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Updater
from others import require_registration
from others import store_user_id
from ban import is_user_banned
# API Key for ipinfo.io
IPINFO_API_KEY = "e24069fe00cdb8"  # Replace with your ipinfo.io API key

def get_ip_info(ip_address):
    """Fetches IP details from freeipapi.com and ipinfo.io."""
    try:
        with httpx.Client() as session:
            # FreeIPAPI Lookup
            freeip_response = session.get(f"https://freeipapi.com/api/json/{ip_address}")
            if freeip_response.status_code != 200:
                return None
            
            freeip_data = freeip_response.json()

            # IPInfo.io Lookup
            ipinfo_response = session.get(f"https://ipinfo.io/{ip_address}/json?token={IPINFO_API_KEY}")
            ipinfo_data = ipinfo_response.json()

        return freeip_data, ipinfo_data

    except Exception:
        return None
@require_registration
def ip_lookup(update: Update, context: CallbackContext):
    """Handles the /ip command."""

    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    # print(f"User {user_id} triggered single")
    chat_type = update.message.chat.type
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return
    try:
        if context.args:
            ip_address = context.args[0]
        else:
            update.message.reply_text("⚠️ Please provide an IP address. Example: `/ip 8.8.8.8`", parse_mode="Markdown")
            return

        ip_data = get_ip_info(ip_address)
        if not ip_data:
            update.message.reply_text("❌ Invalid or Unreachable IP Address.")
            return

        freeip_data, ipinfo_data = ip_data
        IpVersion = freeip_data.get('ipVersion', 'N/A')
        IpAddress = freeip_data.get('ipAddress', 'N/A')
        Country = freeip_data.get('countryName', 'N/A')
        CountryCode = freeip_data.get('countryCode', 'N/A')
        ZipCode = freeip_data.get('zipCode', 'N/A')
        CityName = freeip_data.get('cityName', 'N/A')
        RegionName = freeip_data.get('regionName', 'N/A')
        ProxyCheck = "Yes" if freeip_data.get('isProxy') else "No"
        Continent = freeip_data.get('continent', 'N/A')
        TimeZone = ipinfo_data.get('timezone', 'N/A')

        response = f"""💻 **IP Address Lookup**
━━━━━━━━━━━━━━
🌐 **IP:** `{IpAddress}`
🆔 **IP Version:** `{IpVersion}`
🌍 **Country:** `{Country}` (`{CountryCode}`)
🕰 **Time Zone:** `{TimeZone}`
📮 **Zip Code:** `{ZipCode}`
🏙 **City Name:** `{CityName}`
🌎 **Region Name:** `{RegionName}`
🛡 **Proxy Check:** `{ProxyCheck}`
🌏 **Continent:** `{Continent}`
━━━━━━━━━━━━━━
👤 **Checked By:** [{update.message.from_user.first_name}](tg://user?id={update.message.from_user.id})
"""
        update.message.reply_text(response, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        update.message.reply_text("⚠️ Error processing the request.")
        print(f"Error: {e}")


