import argparse
import json
import re
from xml.etree import ElementTree as ET
from xml.dom import minidom


def create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Gem5 to McPAT parser"
    )
    parser.add_argument(
        '--config', '-c', type=str, required=True,
        metavar='PATH',
        help="Input config.json from Gem5 output."
    )
    parser.add_argument(
        '--stats', '-s', type=str, required=True,
        metavar='PATH',
        help="Input stats.txt from Gem5 output."
    )
    parser.add_argument(
        '--template', '-t', type=str, required=True,
        metavar='PATH',
        help="Template XML file"
    )
    parser.add_argument(
        '--output', '-o', type=str, default="mcpat-out.xml",
        metavar='PATH',
        help="Output file for McPAT input in XML format (default: mcpat-out.xml)"
    )
    return parser


def read_stats_file(stats_file):
    with open(stats_file, 'r') as f:
        stats = {}
        for line in f:
            if line.startswith("stats."):
                key, value = line.split()
                stats[key] = value
    return stats


def read_mcpat_template(template_file):
    tree = ET.parse(template_file)
    return tree


def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent=" ")


def prepare_template(output_file, template_tree, stats):
    root = template_tree.getroot()

    # Replace placeholders in the template with actual stats values
    for stat in root.iter('stat'):
        expr = stat.attrib.get('value', '')
        if expr:
            for key in stats.keys():
                expr = re.sub(f'stats.{key}', stats[key], expr)
            stat.attrib['value'] = str(eval(expr))

    with open(output_file, 'w') as outFile:
        outFile.write(prettify(root))


def main():
    parser = create_parser()
    args = parser.parse_args()

    stats = read_stats_file(args.stats)
    template_tree = read_mcpat_template(args.template)
    prepare_template(args.output, template_tree, stats)


if __name__ == '__main__':
    main()
