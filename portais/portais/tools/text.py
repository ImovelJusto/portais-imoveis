# -*- coding: utf-8 -*-
import re
import unicodedata


def normalize_string(text):
    u"""
    Método para remover caracteres especiais do texto
    """
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')


def maiorTextoFromList(texto):
    u""" Maior string da lista

    Captura o maior pedaco da lista que é gerada
    pela função de retirar acentuacao
    """
    textos = retirar_acentuacao(texto)
    tamanhos = [len(palavra) for palavra in textos]
    return textos[tamanhos.index(max(tamanhos))]


def retirar_acentuacao(texto):
    return re.findall('([\x00-\x7F]+)', texto)
