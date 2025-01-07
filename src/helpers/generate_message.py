 

def generate_config_message(bot_config):
    if not bot_config:
        return "No configuration found for this user."

    config_message = "📊 *Bot Configuration Details* 📊\n\n"
    for key, value in bot_config.items():
        if key in ["API_KEY", "SECRET_KEY"]:
            # Mask API_KEY and SECRET_KEY
            config_message += f"  🔑 *{key}*: `{mask_key(value)}`\n"
        elif isinstance(value, dict):
            config_message += f"  🛠 *{key}*:\n"
            for sub_key, sub_value in value.items():
                config_message += f"      🔹 *{sub_key}*: `{sub_value}`\n"
        else:
            config_message += f"  🔹 *{key}*: `{value}`\n"

    return config_message


def mask_key(key):
    """Masks the key, showing only the first and last 4 characters."""
    if not key:
        return "Not Configured ❌"
    return f"{key[:4]}*****{key[-4:]} ✅"
