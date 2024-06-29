# -*- coding:utf-8 -*-

from pathlib import Path
import argparse
import json


def converter(d, out_dir):
    filename = ".pages"
    for key, value in d.items():
        # skip site and blog 
        if int(key[:2]) == 0 or int(key[:2]) == 9:
            continue
        
        if isinstance(value, dict):
            converter(d=value, out_dir=out_dir)

        title = key.split("-")
        if len(title) > 1:
            content = "title: {}".format(title[1])
            target_dir = Path(out_dir).joinpath(d[key])
            if target_dir.exists():
                for i in target_dir.glob(filename):
                    i.unlink()
            else:
                Path(target_dir).mkdir(parents=True, exist_ok=True)
            
            pages_filepath = Path(target_dir).joinpath(filename)
            with open(pages_filepath, "w") as page_file:
                page_file.write(content)

def _main():
    parser = argparse.ArgumentParser()
    parser.description = "Convert the nav file to `.pages` file"
    parser.add_argument("-n", "--navigation", help="Navigation file", dest="navigation", required=True)
    parser.add_argument("-o", "--output", help="Markdown files directory", dest="output", required=True)
    args = parser.parse_args()

    nav_file_path = args.navigation
    out_dir = args.output
    
    with open(nav_file_path, "r", encoding="utf-8") as f:
        nav_data = json.load(f)
    
    if nav_data is None:
        assert "Navigation file null"
    
    converter(nav_data, out_dir)


if __name__ == "__main__":
    _main()