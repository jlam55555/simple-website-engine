#!/usr/bin/env python
import yaml
import os
import shutil
import re

OUT_DIR = "./out/"
ASSETS_DIR = "./assets/"


# Compiles a template. Returns the compiled template as a string.
def recursive_compile_template(template_file, params, data_file) -> str:
    # If absolute path, treat it as relative to this dir (repo root).
    while template_file[0] == "/":
        template_file = template_file[1:]
    if data_file is not None:
        while data_file[0] == "/":
            data_file = data_file[1:]

    print(
        f"Compiling template {template_file} with params {params} and data {data_file}"
    )

    # Read template file.
    with open(template_file, "r") as fd:
        template = fd.read()

    # Read data file.
    if data_file is not None:
        with open(data_file) as fd:
            data = fd.read()

    # Perform parameter substitutions.
    if params is not None:
        for key, val in params.items():
            template = template.replace(f"${key}", val)

    # Perform recursive template substitutions.
    # (Templates with no body.)
    rgx_template_nobody = r"<template-include(.*?)/>"
    rgx_attr = r' *(src|param-[a-zA-Z0-9]+)="(.*?)"'

    def on_match(match):
        src = None
        params = {}
        for attr in re.finditer(rgx_attr, match.group(1)):
            key = attr.group(1)
            val = attr.group(2)
            if key == "src":
                src = val
            else:
                params[key] = val

        # Adjust src if relative.
        if src[0] != "/":
            src = f"{os.path.dirname(template_file)}/{src}"

        return recursive_compile_template(src, params, None)

    template = re.sub(rgx_template_nobody, on_match, template)

    # Perform recursive template substitutions.
    # (Templates with a body.)
    rgx_template_body = re.compile(
        r"<template-include(.*?)>(.*)</template-include>", re.DOTALL
    )

    def on_match2(match):
        src = None
        params = {}
        for attr in re.finditer(rgx_attr, match.group(1)):
            key = attr.group(1)
            val = attr.group(2)
            if key == "src":
                src = val
            else:
                params[key[6:]] = val

        # Adjust src if relative.
        if src[0] != "/":
            src = f"{os.path.dirname(template_file)}/{src}"
        template_body_unsub = recursive_compile_template(src, params, None)

        # Substitute body.
        return template_body_unsub.replace("<template-body>", match.group(2))

    template = re.sub(rgx_template_body, on_match2, template)

    # Inject data. In Chrome 116 this causes some minor alignment issues.
    if data_file is not None:
        template = f"<script>const _data = {data};</script>{template}"

    return template


# Recursively compile pages in the page skeleton.
def recursive_compile(page, current_path=""):
    # Compile template for output file.
    current_path = f"{current_path}/{page['path']}"
    print(f"Compiling page at {current_path}...")
    compiled_template = recursive_compile_template(
        page["template"],
        page["params"] if "params" in page else None,
        page["data"] if "data" in page else None,
    )

    # Write output file.
    out_dir = f"{OUT_DIR}/{current_path}"
    out_file = f"{out_dir}/index.html"
    os.makedirs(out_dir)
    with open(out_file, "w") as fd:
        fd.write(compiled_template)
    print(f"Wrote template to {out_file}.")

    # Recurse.
    if "subpages" in page:
        for subpage in page["subpages"]:
            recursive_compile(subpage, current_path)


def main():
    # Remove old output directory.
    print("Removing old files...")
    shutil.rmtree(OUT_DIR, ignore_errors=True)

    # pyyaml example from https://stackoverflow.com/a/1774043
    with open("skeleton.yml", "r") as skeleton_stream:
        try:
            for page in yaml.safe_load(skeleton_stream):
                recursive_compile(page)
        except yaml.YAMLError as exc:
            print(exc)

    # Copy the assets directory.
    print("Copying assets...")
    shutil.copytree(ASSETS_DIR, f"{OUT_DIR}/{ASSETS_DIR}")


if __name__ == "__main__":
    main()
