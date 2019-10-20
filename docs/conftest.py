from doctest import ELLIPSIS

from sybil import Sybil
from sybil.parsers.codeblock import CodeBlockParser
from sybil.parsers.doctest import DocTestParser, FIX_BYTE_UNICODE_REPR
from sybil.parsers.skip import skip

pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS|FIX_BYTE_UNICODE_REPR),
        CodeBlockParser(),
        skip,
    ],
    fixtures=["tmpdir"],
    pattern='*.rst',
).pytest()
