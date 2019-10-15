"""
fortran namelist IO.
Authors: Wang Fei
History: 2018.03.22
"""
from collections import OrderedDict
import os
import re


class NameList(OrderedDict):
    """
    class for Fortran namelist.
    keys are used as section names.
    values are groups of dictionaries which hold key-values for
    arguments under each section separately.
    """

    @staticmethod
    def _extract_section(section_content):
        """
        extract the content of a section to a dictionary.
        :param section_content: <str>
        :return: section_dict: <OrderedDict>
        """
        lines = section_content.split("\n")

        section_dict = OrderedDict()
        for line in lines:
            # drop the comment
            if "!" in line:
                st_comment = line.find("!")
                line = line[:st_comment]

            exps = line.strip().split("=")
            if len(exps) != 2:
                continue

            arg_name = exps[0].strip()
            arg_values = [v.strip() for v in exps[1].split(",") if v.strip()]

            section_dict[arg_name] = arg_values
        return section_dict

    def load(self, namelist):
        """
        load a fortran namelist file.
        :param namelist:
        :return:
        """
        with open(namelist, "r") as nl_fin:
            lines = nl_fin.read()
        # print repr(lines)

        sections = [s.strip() for s in re.findall("&(.+)", lines)]
        print sections

        for section in sections:
            # don't know why non-greedy characters not work in wrf namelist:
            # fixed: there should be a "+" following "\s"
            # cannot tell the empty sections in WRF namelist
            # fixed: use re.S model
            # mat_obj = re.search("&%s.*\s((.*\s+)*?)/" % section, lines,)
            mat_obj = re.search("&%s(.*?)\n+\s*/" % section, lines, re.S)
            sect_content = mat_obj.group(1)

            # sect_content = lines.split("&%s" % section)[1].split("\n/")[0]
            # if section == "grib2":
            #     print lines.split("&%s" % section)[1]
            #     print repr(mat_obj.group())
            #     print repr(sect_content)
            #     print sect_content
            sect_dict = self._extract_section(sect_content)
            self.update({section: sect_dict})

    def dump(self, nl_path):
        """
        save this NameList dictionary as a fortran namelist.
        :param nl_path: <str> path of output namelist file.
        :return:
        """
        nl_dir = os.path.dirname(nl_path)
        if nl_dir:
            if not os.path.exists(nl_dir):
                os.makedirs(nl_dir)

        with open(nl_path, "w") as nl_fout:
            for section in self.keys():
                nl_fout.write("&%s\n" % section)
                sect_dict = self[section]
                for arg_name in sect_dict:
                    nl_fout.write("%s = %s\n" % (arg_name, ",".join(sect_dict[arg_name])))
                nl_fout.write("/\n\n")


if __name__ == "__main__":
    nl = NameList()
    # nl.load(r"template_namelist.wps")
    # nl.dump(r"/Users/feiwang/Downloads/template_namelist.wps.output")
    nl.load(r"template_namelist.input")
    # print nl
    print nl.keys()
