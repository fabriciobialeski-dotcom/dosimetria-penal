
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from calculo import dias_para_amd


def amd_por_extenso(anos, meses, dias):
    partes = []

    if anos > 0:
        partes.append(f"{anos} ano" + ("s" if anos != 1 else ""))
    if meses > 0:
        partes.append(f"{meses} mês" + ("es" if meses != 1 else ""))
    if dias > 0:
        partes.append(f"{dias} dia" + ("s" if dias != 1 else ""))

    if not partes:
        return "0 dias"

    if len(partes) == 1:
        return partes[0]

    if len(partes) == 2:
        return " e ".join(partes)

    return ", ".join(partes[:-1]) + " e " + partes[-1]


# =====================================================
# TEXTO DO RELATÓRIO
# =====================================================

def gerar_texto(elementos):
    linhas = []

    linhas.append("DOSIMETRIA DA PENA")
    linhas.append("")
    linhas.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    linhas.append(
        "Relatório gerado por ferramenta de apoio à decisão judicial. "
        "Sem caráter vinculante."
    )
    linhas.append("=" * 70)
    linhas.append("")

    # ----------------------------
    # CRIMES INDIVIDUAIS
    # ----------------------------
    linhas.append("I – CRIMES INDIVIDUAIS")
    linhas.append("")

    for el in elementos.values():
        if el["tipo"] != "crime":
            continue

        linhas.append(f"Crime: {el['descricao']}")

        a, m, d = dias_para_amd(el["pena_base"])
        linhas.append(f"Pena-base: {amd_por_extenso(a, m, d)}")

        a, m, d = dias_para_amd(el["pena_inter"])
        linhas.append(f"Pena intermediária: {amd_por_extenso(a, m, d)}")

        a, m, d = dias_para_amd(el["pena_def"])
        linhas.append(f"Pena definitiva: {amd_por_extenso(a, m, d)}")

        if el.get("multa_def") is not None:
            linhas.append(f"Pena de multa: {el['multa_def']} dias-multa")

        linhas.append("-" * 70)

    # ----------------------------
    # CONCURSOS DE CRIMES
    # ----------------------------
    linhas.append("")
    linhas.append("II – CONCURSOS DE CRIMES")
    linhas.append("")

    for el in elementos.values():
        if el["tipo"] != "resultado":
            continue

        linhas.append(f"Concurso: {el['descricao']}")
        linhas.append("Elementos considerados:")

        for ref in el["origem"]:
            linhas.append(f"- {elementos[ref]['descricao']}")

        a, m, d = dias_para_amd(el["pena_def"])
        linhas.append(f"Pena resultante: {amd_por_extenso(a, m, d)}")
        linhas.append("-" * 70)

    return "\n".join(linhas)


def exportar_txt(elementos):
    return gerar_texto(elementos).encode("utf-8")


def exportar_pdf(elementos):
    texto = gerar_texto(elementos)
    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    x = 40
    y = altura - 40

    for linha in texto.split("\n"):
        if y < 40:
            c.showPage()
            y = altura - 40
        c.drawString(x, y, linha)
        y -= 14

    c.save()
    buffer.seek(0)
    return buffer.read()
