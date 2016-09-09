"""
Compress imagery using lzma
"""

import lzma


class Compressor:
    """
    Compressor
    """

    def __init__(self, file_to_use, output_file):
        self.file = file_to_use
        self.output_file = output_file

    def compress(self):
        """
        Compress the file using lzma
        :return: None
        """

        with lzma.open(self.output_file, 'w') as f:
            f.write(self.file)

    def decompress(self):
        """
        Read a compressed file
        :return: a file object
        """

        with lzma.open(self.file) as f:
            file_content = f.read()

        return file_content
