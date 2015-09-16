from subprocess import PIPE, Popen
import re


def manpage(file):
    """
    Read a manfile into a string

    Parameters
    ----------
    file : str
        Path to the file to read

    Returns
    -------
    The formatted manpage
    """
    p = Popen(['nroff', '-man', '-Tascii', file], stdout=PIPE)
    p.wait()
    result = p.stdout.read()
    # remove backspaces
    result = re.sub('.\x08', '', result)
    return result


def parse_sections(manpage):
    """
    Parse a manpage into section header -> section text pairs

    Parameters
    ----------
    manpage : str
        The manpage content

    Returns
    -------
    A dict mapping section headers to section contents

    Notes
    -----
    This parses the Detailed Description subsection
    """

    # Extract the Detailed Description section
    manpage = re.split('\nDetailed Description', manpage)[1]
    manpage = re.split('\n\w', manpage)[0]

    # convert bullet points from o to -
    manpage = re.sub(' o ', ' - ', manpage)

    # extract sub-section titles
    section_re = '(?<=\n       )\w[\w ]+?(?=:)'
    headers = re.findall(section_re, manpage)
    sections = re.split(section_re, manpage)

    replace = {"Output": "Output Array"}
    for i, h in enumerate(headers):
        headers[i] = replace.get(h, h).title()

    # first character of section is an unwanted colon.
    return dict((h, s[1:].rstrip()) for
                h, s in zip(headers, sections[1:]))


def build_docstring(sections):
    """
    Build a numpydoc-style docstring from a section dict

    Parameters
    ----------
    sections : dict
       A dictionary returned from parse_sections

    Returns
    -------
    docstring : str
        A numpy-formatted docstring
    """
    headers = ['Input', 'Output array',
               'Examples', 'Notes']
    labels = ['Parameters', 'Returns', 'Examples', 'Notes']

    result = []

    if 'Synopsis' in sections:
        result.append(sections['Synopsis'].strip())

    if 'Summary' in sections:
        sec = sections['Summary']
        summary = re.sub('\n +', ' ', sec).strip()
        result.append(summary.strip())

    for hdr, lbl in zip(headers, labels):
        if hdr not in sections:
            continue
        sec = sections[hdr]

        sec = collapse_newlines(sec)
        sec = trim_indentation(sec)
        if empty(sec):
            continue

        sec = labeled_section(lbl, sec)

        result.append(sec)
    return '\n\n'.join(result)


def indent(text, level):
    """Indent a block of text by a `level` of 4 spaces"""
    try:  # text is str
        text = text.split('\n')
    except AttributeError:  # list
        pass
    return '\n'.join('    ' * level + line for line in text)


def build_rst(sections):
    """
    Build a sphinx documentation directive from a section dict

    Parameters
    ----------
    sections : dict
        A dictionary returned from parse_sections

    Returns
    -------
    entry : str
       A sphinx description of the operator
    """
    headers = ['Input', 'Output array',
               'Examples', 'Notes']
    labels = ['Parameters', 'Returns', 'Examples', 'Notes']

    result = ['']

    if 'Summary' in sections:
        sec = sections['Summary']
        summary = re.sub('\n +', ' ', sec).strip()
        summary = summary.replace(':\n -', ':\n\n -')
        summary = summary.replace('\n -', '\n    *')
        result.extend(['', summary, ''])

    if 'Synopsis' in sections:
        result.append('::')
        result.append(indent(['', sections['Synopsis'].strip(), ''], 2))

    for hdr, lbl in zip(headers, labels):
        if hdr not in sections:
            continue
        lbl = lbl.lower()
        sec = sections[hdr]
        sec = collapse_newlines(sec)
        sec = trim_indentation(sec)
        if empty(sec):
            continue
        sec = indent(sec, 1)

        if lbl == 'examples':
            result.extend(['', ':%s:' % lbl, '', '::'])
            result.append(sec)
        else:
            result.extend(['', ':%s:' % lbl, sec, ''])

    return ".. function:: %s" + indent(result, 1)


def man2doc(pth):
    """
    Parse a numpy-style docstring from a SciDB manpage

    Parameters
    ----------
    pth : str
        The path to a SciDB Operator docstring

    Returns
    -------
    docstring : str
        The numpy-style docstring
    """
    return build_docstring(parse_sections(manpage(pth)))


def man2rst(pth):
    return build_rst(parse_sections(manpage(pth)))


def collapse_newlines(str):
    return re.sub('\n+', '\n', str)


def trim_indentation(str):
    return re.sub('           ', '    ', str)


def empty(str):
    return str.strip() in ['', 'n/a']


def labeled_section(title, contents):
    result = [title, '-' * len(title), contents]
    return '\n'.join(result)


def signature(srcpth):
    """
    Return signature information for an operator, given its source

    Parameters
    ----------
    srcpath : str
        Path to a SciDB operator C++ source file

    Returns
    -------
    signature: list of strs
        Each entry is one of
         - array
         - aggregate
         - attribute
         - constant
         - dimanme
         - expression
         - schema
         - args
       args indicates 0 or more positional arguments
       The other keywords refer to SciDB data types

    Notes
    -----
    This just scans for ADD_PARAM_* macro occurances,
    which seem to spell out the operator schema in order.
    I don't know how brittle this is.
    """
    with open(srcpth) as infile:
        data = infile.read()

    params = re.findall('(?<=ADD_PARAM_)[A-Z_0-9]+', data)

    results = {
        'input': 'array',
        'in_array_name': 'array',
        'out_array_name': 'array',
        'out_dimension_name': 'dimname',
        'out_attribute_name': 'attribute',
        'expression': 'expression',
        'schema': 'schema',
        'aggregate_call': 'aggregate',
        'in_array_name2': 'array',
        'in_attribute_name': 'attribute',
        'in_dimension_name': 'dimname',
        'varies': 'args',
        'constant': 'constant',
    }

    return [results[p.lower()] for p in params]


def operator_name(srcpath):
    """
    Parse source file to discover the AFL operator declared

    Parameters
    ----------
    srcpath: str
        path to a SciDB operator source .cpp file

    Returns
    -------
    operator_name : str
    """
    with open(srcpath) as infile:
        data = infile.read()

    regex = r'DECLARE_LOGICAL_OPERATOR_FACTORY\(.*, *"(.*)" *\)'
    result = re.findall(regex, data)
    assert len(result) == 1
    return result[0]


def discover_operators(srcbase):
    """
    Determine which operators are installed in SciDB by
    scanning src/query/ops/BuildInOps.inc

    Parameters
    ----------
    srcbase : str
       Path to src of SciDB source tree

    Returns
    -------
    ops : set
       A set of operator names like LogicalProject

    Notes
    -----
    Not all operator files are actually installed (e.g.,
    deprecated operators are still present in the source,
    but commented out of BuildInOps.inc)
    """
    pth = os.path.join(srcbase, 'query', 'ops', 'BuildInOps.inc')
    data = open(pth).readlines()
    lines = [line for line in data if line.startswith('LOGICAL_BUILDIN')]
    return set(l.split('(')[1].split(')')[0] for l in lines)


def main(manbase, srcbase, outpath=None):
    import json
    from glob import glob

    outpath = outpath or 'afldb.py'
    result = []
    rst = []
    ops = discover_operators(srcbase)

    for path in glob(srcbase + '/query/ops/*/Logical*cpp'):
        sig = signature(path)
        name = operator_name(path)

        if path.split('/')[-1].split('.')[0] not in ops:
            # these operators are likely deprecated and removed
            print '%s not installed. Skipping' % name
            continue

        print '...%s' % name

        manpattern = path.split('/')[-1].split('.cpp')[0]
        manpath = manbase + 'scidb_' + manpattern + '.3'

        try:
            doc = man2doc(manpath)
            rst.append(man2rst(manpath) % name)
        except IndexError:
            doc = manpage(manpath)

        result.append(dict(name=name, doc=doc, signature=sig))

    with open(outpath, 'w') as outfile:
        outfile.write("# Automatically generated by scidbpy-aflgen\n")
        outfile.write("# DO NOT EDIT -- changes will be overwritten!\n")
        outfile.write("operators = ")
        outfile.write(json.dumps(result, indent=2))

    with open(outpath.strip('.py') + '.rst', 'w') as outfile:
        outfile.write('\n\n'.join(rst))


if __name__ == "__main__":
    import os
    manpath = os.environ.get('SCIDB_MANPATH', 'man/')
    srcpath = os.environ.get('SCIDB_SRCPATH', 'src/')
    main(manpath, srcpath)
