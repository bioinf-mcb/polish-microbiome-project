from os import stat
from .odt_parser import ODTParser
from .rtf_parser import RTFParser

class ParserRouter:
    @staticmethod
    def route(fname):
        if '.rtf' in fname:
            return RTFParser
        if '.odt' in fname:
            return ODTParser