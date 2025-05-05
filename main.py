import os
from diff.config_diff import ConfigDiffer
from parser.xmi_parser import UMLParser


def ensure_out_dir():
    if not os.path.exists("out"):
        os.makedirs("out")


def main():
    ensure_out_dir()

    xmi_path = "input/impulse_test_input.xml"
    config_json = "input/config.json"
    patched_json = "input/patched_config.json"

    config_xml_out = "out/config.xml"
    meta_json_out = "out/meta.json"
    delta_json_out = "out/delta.json"
    res_patched_out = "out/res_patched_config.json"

    parser = UMLParser(xmi_path)
    parser.parse()
    parser.generate_config(config_xml_out)
    parser.generate_meta(meta_json_out)

    differ = ConfigDiffer(config_json, patched_json)
    delta = differ.generate_delta(delta_json_out)
    differ.apply_delta(delta, res_patched_out)


if __name__ == "__main__":
    main()
