#!/usr/bin/python

import argparse
import os
import osc.conf
import osc.core
from optparse import OptionParser
import re
import tempfile
import traceback

try:
    from xml.etree import cElementTree as ET
except ImportError:
    import cElementTree as ET

project = 'Cloud:OpenStack:Pike'

SPEC_VERSION_PATTERN=re.compile(r"""Version:\s+(.*)""")

def show_package_info(project, package):
    """retrieve list of all packages for a project and for
    each package get the version from the spec file"""
    # initialize osc configuration
    osc.conf.get_config()
    packages = osc.core.meta_get_packagelist(osc.conf.config['apiurl'],
                                             project)
    package_version_dict = {}
    for package in packages:
        m = osc.core.show_files_meta(osc.conf.config['apiurl'],
                                     project, package)
        root = ET.fromstring(m)
        spec_filename = [entry_elem.attrib.get("name") \
                         for entry_elem in root.findall('.//entry') \
                         if '.spec' in entry_elem.attrib.get("name")][0]
        tmpfile = None
        try:
            (fd, tmpfile) = tempfile.mkstemp(prefix='temp_spec')
            osc.core.get_source_file(osc.conf.config['apiurl'],
                                     project, package, spec_filename,
                                     tmpfile)
            with open(tmpfile) as f:
                for line in f:
                    m = re.match(SPEC_VERSION_PATTERN, line)
                    if m:
                        spec_version = m.group(1)
                        package_version_dict[package] = spec_version
                        break
        finally:
            if tmpfile is not None:
                os.close(fd)
                os.unlink(tmpfile)

    return package_version_dict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="Project")
    parser.add_argument("package", help="Package")
    parser.add_argument("-l", "--list_packages",
                        action="store_true",
                        help=("list all packages and versions"
                              "and their versions"))
    args = parser.parse_args()
    try:
        if args.list_packages:
            package_version_dict = show_package_info(args.project, args.package)
            for package in package_version_dict:
                print "%s: %s" % (package, package_version_dict[package])
    except:
        traceback.print_exc()

if __name__ == """__main__""":
    main()
