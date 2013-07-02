#!/usr/bin/env python3
# coding: utf-8

""" Fileorganizer Rhythmbox database operations

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""


class UrlData():
    """ Operations to alter values based on RhythmDB style """
    def __init__(self):
        self.urlascii = ('%', "#", ';', ' ', '"', '<', '>', '?', '[', '\\',
                          "]", '^', '`', '{', '|', '}', '€', '‚', 'ƒ', '„',
                          '…', '†', '‡', 'ˆ', '‰', 'Š', '‹', 'Œ', 'Ž', '‘',
                          '’', '“', '”', '•', '–', '—', '˜', '™', 'š', '›',
                          'œ', 'ž', 'Ÿ', '¡', '¢', '£', '¥', '|', '§', '¨',
                          '©', 'ª', '«', '¬', '¯', '®', '¯', '°', '±', '²',
                          '³', '´', 'µ', '¶', '·', '¸', '¹', 'º', '»', '¼',
                          '½', '¾', '¿', 'À', 'Á', 'Â', 'Ã', 'Ä', 'Å', 'Æ',
                          'Ç', 'È', 'É', 'Ê', 'Ë', 'Ì', 'Í', 'Î', 'Ï', 'Ð',
                          'Ñ', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö', 'Ø', 'Ù', 'Ú', 'Û',
                          'Ü', 'Ý', 'Þ', 'ß', 'à', 'á', 'â', 'ã', 'ä', 'å',
                          'æ', 'ç', 'è', 'é', 'ê', 'ë', 'ì', 'í', 'î', 'ï',
                          'ð', 'ñ', 'ò', 'ó', 'ô', 'õ', 'ö', '÷', 'ø', 'ù',
                          'ú', 'û', 'ü', 'ý', 'þ', 'ÿ', '¦')
        self.urlcode = ('%25', '%23', '%3B', '%20', '%22', '%3C', '%3E', '%3F',
                        '%5B', '%5C', '%5D', '%5E', '%60', '%7B', '%7C', '%7D',
                        '%E2%82%AC', '%E2%80%9A', '%C6%92', '%E2%80%9E',
                        '%E2%80%A6', '%E2%80%A0', '%E2%80%A1', '%CB%86',
                        '%E2%80%B0', '%C5%A0', '%E2%80%B9', '%C5%92', '%C5%BD',
                        '%E2%80%98', '%E2%80%99', '%E2%80%9C', '%E2%80%9D',
                        '%E2%80%A2', '%E2%80%93', '%E2%80%94', '%CB%9C',
                        '%E2%84%A2', '%C5%A1', '%E2%80%BA', '%C5%93', '%C5%BE',
                        '%C5%B8', '%C2%A1', '%C2%A2', '%C2%A3', '%C2%A5',
                        '%7C', '%C2%A7', '%C2%A8', '%C2%A9', '%C2%AA',
                        '%C2%AB', '%C2%AC', '%C2%AF', '%C2%AE', '%C2%AF',
                        '%C2%B0', '%C2%B1', '%C2%B2', '%C2%B3', '%C2%B4',
                        '%C2%B5', '%C2%B6', '%C2%B7', '%C2%B8', '%C2%B9',
                        '%C2%BA', '%C2%BB', '%C2%BC', '%C2%BD', '%C2%BE',
                        '%C2%BF', '%C3%80', '%C3%81', '%C3%82', '%C3%83',
                        '%C3%84', '%C3%85', '%C3%86', '%C3%87', '%C3%88',
                        '%C3%89', '%C3%8A', '%C3%8B', '%C3%8C', '%C3%8D',
                        '%C3%8E', '%C3%8F', '%C3%90', '%C3%91', '%C3%92',
                        '%C3%93', '%C3%94', '%C3%95', '%C3%96', '%C3%98',
                        '%C3%99', '%C3%9A', '%C3%9B', '%C3%9C', '%C3%9D',
                        '%C3%9E', '%C3%9F', '%C3%A0', '%C3%A1', '%C3%A2',
                        '%C3%A3', '%C3%A4', '%C3%A5', '%C3%A6', '%C3%A7',
                        '%C3%A8', '%C3%A9', '%C3%AA', '%C3%AB', '%C3%AC',
                        '%C3%AD', '%C3%AE', '%C3%AF', '%C3%B0', '%C3%B1',
                        '%C3%B2', '%C3%B3', '%C3%B4', '%C3%B5', '%C3%B6',
                        '%C3%B7', '%C3%B8', '%C3%B9', '%C3%BA', '%C3%BB',
                        '%C3%BC', '%C3%BD', '%C3%BE', '%C3%BF', '%C2%A6')

        self.rbdb_rep = ('%28', '%29', '%2B', '%27', '%2C', '%3A', '%21',
                          '%24', '%26', '%2A', '%2C', '%2D', '%2E', '%3D',
                          '%40', '%5F', '%7E')
        self.rbdb_itm = ('(', ')', '+', "'", ',', ':', '!', '$', '&', '*',
                          ',', '-', '.', '=', '@', '_', '~')

    # Replace Characters with UTF code value
    def set_url(self, string):
        """ Set RhythmDB style string """
        count = 0
        while count < len(self.urlascii):
            string = string.replace(self.urlascii[count], self.urlcode[count])
            count = count + 1
        return string

    # Replace UTF code vales with Characters
    def set_ascii(self, string):
        """ Change unicode codes back to assci for RhythmDB """
        count = 0
        while count < len(self.rbdb_rep):
            string = string.replace(self.rbdb_rep[count],
                                    self.rbdb_itm[count])
            count = count + 1
        return string
