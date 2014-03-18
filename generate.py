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
    section_re = '\n       \w[\w ]+?:'
    headers = re.findall(section_re, manpage)
    sections = re.split(section_re, manpage)

    replace = {"Output:": "Output Array:"}
    for i, h in enumerate(headers):
        headers[i] = replace.get(h.strip(), h)
        headers[i] = headers[i].replace(':', '')

    return dict((h.strip().title(), s.rstrip()) for
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

    params = re.findall('(?<=ADD_PARAM_)[A-Z_]+', data)

    results = {
        'input': 'array',
        'in_array_name': 'array',
        'out_array_name': 'array',
        'out_dimension_name': 'dimname',
        'out_attribute_name': 'attribute',
        'expression': 'expression',
        'schema': 'schema',
        'aggregate_call': 'aggregate',
        'in_array_name_2': 'array',
        'in_attribute_name': 'attribute',
        'in_dimension_name': 'dimname',
        'varies': 'args',
        'constant': 'constant',
    }

    return [results[p.lower()] for p in params]


def main(manbase, srcbase, outpath=None):
    import json
    from glob import glob

    outpath = outpath or 'afl.json'
    result = {}
    for path in glob(manbase + 'scidb_Logical*'):
        name = path.split('scidb_Logical')[1].split('.')[0]
        try:
            doc = man2doc(path)
        except IndexError:
            doc = manpage(path)

        src = glob(srcbase + 'query/ops/*/Logical' + name + '.cpp')
        sig = signature(src[0]) if len(src) == 1 else ['args']

        result[name] = dict(doc=doc, signature=sig)

    with open(outpath, 'w') as outfile:
        json.dump(result, outfile, indent=2)


if __name__ == "__main__":
    import os
    manpath = os.environ.get('SCIDB_MANPATH', 'man/')
    srcpath = os.environ.get('SCIDB_SRCPATH', 'src/')
    main(manpath, srcpath)
