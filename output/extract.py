import json
import re


def extract_links(json_file, output_file=None):
    pattern = re.compile(r"https?://[^\s]+?\.(?:png|jpg|gif)")

    ban = ["pixel", "inlinePlayer", "images/I/", "images/G/"]

    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    js = json.dumps(data)

    links = pattern.findall(js)

    filtered = [link for link in links if not any(keyword in link for keyword in ban)]

    if output_file != None:
        with open(output_file, "w", encoding="utf-8") as output:
            for link in filtered:
                output.write(link + "\n")

        return filtered
