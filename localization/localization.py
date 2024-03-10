import os
import requests
import json

deepl_key = os.getenv('DEEPL_KEY')
properties_directory = "../src/main/resources/messages/"


def extract_properties(text):
    properties = {}

    for line in text:
        line = line.strip()

        if line and not line.startswith('#') and '=' in line:
            key_value = line.split('=')
            key = key_value[0].strip()
            value = key_value[1].strip()
            if key and value:
                properties[key] = value

    return properties


def missing_properties(properties_file, properties_checklist):
    with open(properties_file, 'r') as f:
        text = f.readlines()

    present_properties = extract_properties(text)
    missing = {k: v for k, v in properties_checklist.items() if k not in present_properties.keys()}
    return missing


def translate_property(value, target_lang):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'DeepL-Auth-Key {deepl_key}',
        'User-Agent': 'LocalizationScript/1.0'

    }
    url = 'https://api-free.deepl.com/v2/translate'
    data = {
        'text': [value],
        'source_lang': 'EN',
        'target_lang': target_lang,
        'preserve_formatting': True
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    return response.json()["translations"][0]["text"]


def populate_properties(file_path, properties_checklist, target_lang):
    with open(file_path, 'a+') as file:
        properties_to_translate = missing_properties(file_path, properties_checklist)
        for key, value in properties_to_translate.items():
            new_value = translate_property(value, target_lang)
            property_line = f"{key}={new_value}\n"
            print(property_line)
            file.write(property_line)


with open(properties_directory + 'messages.properties') as base_properties_file:
    base_properties = extract_properties(base_properties_file)

languages = [
    # configure languages here
    "nl", "es", "fr", "de", "it", "pt", "ru", "ja", "zh", "fi"
]

for language in languages:
    populate_properties(properties_directory + f"messages_{language}.properties", base_properties, language)
