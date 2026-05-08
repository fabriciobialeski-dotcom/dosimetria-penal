import streamlit as st
from fractions import Fraction
import json
import datetime
import requests
if "calculo_penal" not in st.session_state:
    st.session_state.calculo_penal = {}
query_params = st.query_params

if "id" in query_params:
    calc_id = query_params["id"]

    response = requests.get(
        f"http://127.0.0.1:8000/calculos/{calc_id}"
    )

    if response.status_code == 200:
        data = response.json()

        if "dados" in data:
            st.session_state.calculo_penal = data["dados"]
            st.success("✅ Cálculo carregado do link")

from calculo import (
    calcular_pena_base,
    calcular_pena_intermediaria,
    calcular_pena_definitiva,
    calcular_dias_multa_base,
    calcular_dias_multa_definitivos,
    dias_para_amd,
    aplicar_fracao
)

# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(page_title="DOSIMETRIA DA PENA", page_icon="🧮")
st.title("🧮 DOSIMETRIA DA PENA")

# =====================================================
# ESTADO
# =====================================================

if "objetos" not in st.session_state:
    st.session_state.objetos = {
        "A": {
            "ativo": True,
            "tipo": "crime",
            "pena_minima": 12,
            "fracoes_1f": "",
            "fracoes_2f": "",
            "fracoes_3f": "",
            "cascata": False,
            "tem_multa": False,
            "dias_multa_min": 10,
            "fracoes_multa_1f": "",
            "fracoes_multa_3f": "",
            "cascata_multa": False,
            "descricao": ""
        },
        "B": {
            "ativo": True,
            "tipo": "crime",
            "pena_minima": 12,
            "fracoes_1f": "",
            "fracoes_2f": "",
            "fracoes_3f": "",
            "cascata": False,
            "tem_multa": False,
            "dias_multa_min": 10,
            "fracoes_multa_1f": "",
            "fracoes_multa_3f": "",
            "cascata_multa": False,
            "descricao": ""
        },
    }

# =====================================================
# MÚLTIPLOS RÉUS
# =====================================================

if "reus" not in st.session_state:
    st.session_state.reus = {
        "Réu 1": {
            "objetos": st.session_state.objetos.copy()
        }
    }

if "reu_ativo" not in st.session_state:
    st.session_state.reu_ativo = list(st.session_state.reus.keys())[0]

st.markdown("### 👥 Réus")

nomes_reus = list(st.session_state.reus.keys())
cols = st.columns(len(nomes_reus) + 1)

for i, nome in enumerate(nomes_reus):
    with cols[i]:
        label = f"✅ {nome}" if nome == st.session_state.reu_ativo else nome
        if st.button(label, key=f"reu_{nome}"):
            st.session_state.reu_ativo = nome
            st.rerun()

with cols[-1]:
    if st.button("➕", key="add_reu"):
        novo_nome = f"Réu {len(st.session_state.reus) + 1}"

        st.session_state.reus[novo_nome] = {
            "objetos": {
                "A": {
                    "ativo": True,
                    "tipo": "crime",
                    "pena_minima": 12,
                    "fracoes_1f": "",
                    "fracoes_2f": "",
                    "fracoes_3f": "",
                    "cascata": False,
                    "tem_multa": False,
                    "dias_multa_min": 10,
                    "fracoes_multa_1f": "",
                    "fracoes_multa_3f": "",
                    "cascata_multa": False,
                    "descricao": ""
                }
            }
        }

        st.session_state.reu_ativo = novo_nome
        st.rerun()

novo_nome = st.text_input(
    "Nome do réu",
    value=st.session_state.reu_ativo
)

if novo_nome != st.session_state.reu_ativo:
    st.session_state.reus[novo_nome] = st.session_state.reus.pop(
        st.session_state.reu_ativo
    )
    st.session_state.reu_ativo = novo_nome
    st.rerun()

st.session_state.objetos = st.session_state.reus[
    st.session_state.reu_ativo
]["objetos"]

if "contador_resultados" not in st.session_state:
    st.session_state.contador_resultados = 1

st.divider()

# =====================================================
# ABAS
# =====================================================

objetos_ativos = {
    k: v for k, v in st.session_state.objetos.items() if v["ativo"]
}

col1, col2 = st.columns([8, 1])

with col1:
    nomes_abas = list(objetos_ativos.keys()) + ["⚖️ Concurso"]
    abas = st.tabs(nomes_abas)

with col2:
    if st.button("➕", help="Adicionar crime"):
        letra = chr(ord("A") + len(st.session_state.objetos))
        st.session_state.objetos[letra] = {
            "ativo": True,
            "tipo": "crime",
            "pena_minima": 12,
            "fracoes_1f": "",
            "fracoes_2f": "",
            "fracoes_3f": "",
            "cascata": False,
            "tem_multa": False,
            "dias_multa_min": 10,
            "fracoes_multa_1f": "",
            "fracoes_multa_3f": "",
            "cascata_multa": False,
            "descricao": ""
        }
        st.rerun()

penas_finais = {}

# =====================================================
# CRIMES
# =====================================================

for nome, aba in zip(objetos_ativos.keys(), abas[:-1]):
    obj = objetos_ativos[nome]

    with aba:

        if obj["tipo"] == "resultado":
            st.subheader(f"CONCURSO {nome}")
            pena_def = obj["pena_def"]
            a, m, d = dias_para_amd(pena_def)
            st.success(f"Resultado intermediário: {a}a {m}m {d}d")
            penas_finais[nome] = pena_def
            continue

        titulo = f"CRIME {nome}"
        if obj.get("descricao"):
            titulo += f" — {obj['descricao']}"

        st.subheader(titulo)

        obj["descricao"] = st.text_input(
            "Nome do crime",
            value=obj.get("descricao", ""),
            key=f"desc_{nome}"
        )

        obj["pena_minima"] = st.number_input(
            "Pena mínima abstrata (anos)",
            min_value=1,
            value=obj["pena_minima"],
            key=f"pm_{nome}"
        )

        st.markdown("### 🟦 Pena-base")
        obj["fracoes_1f"] = st.text_area("Frações", obj["fracoes_1f"], key=f"1f_{nome}")
        f1 = [f for f in obj["fracoes_1f"].splitlines() if f.strip()]
        pena_base = calcular_pena_base(obj["pena_minima"], f1)

        a, m, d = dias_para_amd(pena_base)
        st.info(f"Pena-base: {a}a {m}m {d}d")

        st.markdown("### 🟩 Pena intermediária")
        obj["fracoes_2f"] = st.text_area("Frações", obj["fracoes_2f"], key=f"2f_{nome}")
        f2 = [f for f in obj["fracoes_2f"].splitlines() if f.strip()]
        pena_inter = calcular_pena_intermediaria(pena_base, f2)

        a, m, d = dias_para_amd(pena_inter)
        st.info(f"Pena intermediária: {a}a {m}m {d}d")

        st.markdown("### 🟨 Pena definitiva")
        obj["fracoes_3f"] = st.text_area("Frações", obj["fracoes_3f"], key=f"3f_{nome}")
        obj["cascata"] = st.checkbox("Efeito cascata", value=obj["cascata"], key=f"casc_{nome}")
        f3 = [f for f in obj["fracoes_3f"].splitlines() if f.strip()]
        pena_def = calcular_pena_definitiva(pena_inter, f3, obj["cascata"])

        a, m, d = dias_para_amd(pena_def)
        st.success(f"Pena definitiva: {a}a {m}m {d}d")

        penas_finais[nome] = pena_def

# =====================================================
# CONCURSO
# =====================================================

with abas[-1]:
    st.header("⚖️ Concurso encadeado")

    selecionados = st.multiselect(
        "Selecionar objetos",
        options=list(penas_finais.keys())
    )

    if len(selecionados) >= 2:
        tipo = st.radio("Tipo de concurso", ["Material", "Formal", "Continuado"])

        penas_sel = [penas_finais[o] for o in selecionados]
        pena_material = sum(penas_sel)
        pena_base = max(penas_sel)

        if tipo == "Material":
            pena_result = pena_material
        else:
            fracao_txt = st.text_input("Fração", value="1/6")
            try:
                acrescimo = aplicar_fracao(pena_base, fracao_txt)
                pena_result = pena_base + acrescimo
            except:
                st.error("Fração inválida")
                pena_result = pena_base

        a, m, d = dias_para_amd(pena_result)
        st.success(f"Resultado do concurso: {a}a {m}m {d}d")

        if st.button("✅ Consolidar resultado"):
            nome_r = f"R{st.session_state.contador_resultados}"
            st.session_state.contador_resultados += 1

            st.session_state.objetos[nome_r] = {
                "ativo": True,
                "tipo": "resultado",
                "pena_def": pena_result
            }

            st.rerun()

    else:
        st.info("Selecione ao menos dois objetos.")

# =====================================================
# EXPORTAÇÃO
# =====================================================

def _serializar(obj):
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    elif isinstance(obj, (list, tuple)):
        return [_serializar(i) for i in obj]
    elif isinstance(obj, dict):
        return {str(k): _serializar(v) for k, v in obj.items()}
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    else:
        return str(obj)

def gerar_exportacao_completa():
    return {
        "metadata": {
            "tipo": "calculo_penal",
            "versao": "1.0",
            "data_exportacao": datetime.datetime.now().isoformat()
        },
        "state": _serializar(dict(st.session_state))
    }

st.divider()
st.subheader("📤 Exportar cálculo")

if st.button("Gerar arquivo do cálculo"):
    dados = gerar_exportacao_completa()

    json_str = json.dumps(
        dados,
        indent=4,
        ensure_ascii=False
    )

    st.download_button(
        label="📥 Baixar JSON",
        data=json_str,
        file_name="calculo_penal.json",
        mime="application/json"
    )
    st.subheader("🔗 Compartilhar cálculo")

if st.button("💾 Gerar link compartilhável"):

    response = requests.post(
        "https://dosimetria-penal.onrender.com/calculos",
        json={"dados": st.session_state.calculo_penal}
    )

    if response.status_code == 200:
        calc_id = response.json()["id"]

        link = f"https://SEU-APP.streamlit.app/?id={calc_id}"

        st.success("✅ Link gerado:")
        st.code(link)
    else:
        st.error("Erro ao gerar link")