
from fractions import Fraction

# ===============================
# CONVENÇÕES
# ===============================
# 1 ano = 360 dias
# 1 mês = 30 dias
# Cálculo interno sempre em DIAS
# ===============================

def anos_para_dias(anos):
    return anos * 360


def dias_para_amd(dias):
    anos = dias // 360
    resto = dias % 360
    meses = resto // 30
    dias_finais = resto % 30
    return anos, meses, dias_finais


def aplicar_fracao(base, fracao_str):
    fracao = Fraction(fracao_str)
    return base * fracao.numerator // fracao.denominator


# ===============================
# PENA PRIVATIVA DE LIBERDADE
# ===============================

def calcular_pena_base(pena_minima_anos, fracoes):
    base = anos_para_dias(pena_minima_anos)
    aumento = 0
    for fr in fracoes:
        aumento += aplicar_fracao(base, fr)
    return base + aumento


def calcular_pena_intermediaria(pena_base_dias, fracoes):
    aumento = 0
    for fr in fracoes:
        aumento += aplicar_fracao(pena_base_dias, fr)
    return pena_base_dias + aumento


def calcular_pena_definitiva(pena_intermediaria_dias, fracoes, usar_cascata=False):
    pena = pena_intermediaria_dias

    if not usar_cascata:
        variacao = 0
        for fr in fracoes:
            variacao += aplicar_fracao(pena_intermediaria_dias, fr)
        pena += variacao
    else:
        for fr in fracoes:
            pena += aplicar_fracao(pena, fr)

    return pena


# ===============================
# PENA DE MULTA
# ===============================

def calcular_dias_multa_base(dias_multa_minimos, fracoes):
    aumento = 0
    for fr in fracoes:
        aumento += aplicar_fracao(dias_multa_minimos, fr)
    return dias_multa_minimos + aumento


def calcular_dias_multa_definitivos(dias_multa_base, fracoes, usar_cascata=False):
    multa = dias_multa_base

    if not usar_cascata:
        variacao = 0
        for fr in fracoes:
            variacao += aplicar_fracao(dias_multa_base, fr)
        multa += variacao
    else:
        for fr in fracoes:
            multa += aplicar_fracao(multa, fr)

    return multa
