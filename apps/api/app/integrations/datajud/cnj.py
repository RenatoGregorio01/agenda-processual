import re

CNJ_DIGITS = 20

TJ_ESTADUAL = {
    "01": "tjac",
    "02": "tjal",
    "03": "tjap",
    "04": "tjam",
    "05": "tjba",
    "06": "tjce",
    "07": "tjdft",
    "08": "tjes",
    "09": "tjgo",
    "10": "tjma",
    "11": "tjmt",
    "12": "tjms",
    "13": "tjmg",
    "14": "tjpa",
    "15": "tjpb",
    "16": "tjpr",
    "17": "tjpe",
    "18": "tjpi",
    "19": "tjrj",
    "20": "tjrn",
    "21": "tjrs",
    "22": "tjro",
    "23": "tjrr",
    "24": "tjsc",
    "25": "tjse",
    "26": "tjsp",
    "27": "tjto",
}

TRE = {
    "01": "tre-ac",
    "02": "tre-al",
    "03": "tre-ap",
    "04": "tre-am",
    "05": "tre-ba",
    "06": "tre-ce",
    "07": "tre-df",
    "08": "tre-es",
    "09": "tre-go",
    "10": "tre-ma",
    "11": "tre-mt",
    "12": "tre-ms",
    "13": "tre-mg",
    "14": "tre-pa",
    "15": "tre-pb",
    "16": "tre-pr",
    "17": "tre-pe",
    "18": "tre-pi",
    "19": "tre-rj",
    "20": "tre-rn",
    "21": "tre-rs",
    "22": "tre-ro",
    "23": "tre-rr",
    "24": "tre-sc",
    "25": "tre-se",
    "26": "tre-sp",
    "27": "tre-to",
}

TJM = {"13": "tjmmg", "21": "tjmrs", "26": "tjmsp"}


class CnjError(ValueError):
    pass


def so_digitos(numero: str) -> str:
    return re.sub(r"\D", "", numero or "")


def mascarar_cnj(numero: str) -> str:
    digitos = so_digitos(numero)
    if len(digitos) != CNJ_DIGITS:
        raise CnjError(f"Número CNJ deve ter 20 dígitos, veio {len(digitos)}.")
    return (
        f"{digitos[0:7]}-{digitos[7:9]}.{digitos[9:13]}."
        f"{digitos[13:14]}.{digitos[14:16]}.{digitos[16:20]}"
    )


def _dezoito_sem_dv(digitos: str) -> str:
    """NNNNNNN + AAAA + J + TR + OOOO (18 dígitos, sem o verificador)."""
    return digitos[0:7] + digitos[9:20]


def digito_verificador(dezoito: str) -> str:
    """Calcula DD pela ISO 7064 Mod 97-10 (Resolução CNJ 65/2008, Anexo VIII)."""
    digits = so_digitos(dezoito)
    if len(digits) != 18:
        raise CnjError("Informe 18 dígitos para calcular o verificador.")
    resto = (int(digits) * 100) % 97
    return f"{98 - resto:02d}"


def montar_cnj(
    sequencial: str,
    ano: str,
    ramo: str,
    tribunal: str,
    origem: str,
) -> str:
    nnn = so_digitos(sequencial).zfill(7)
    aaaa = so_digitos(ano).zfill(4)
    ramo_j = so_digitos(ramo)
    tr = so_digitos(tribunal).zfill(2)
    oooo = so_digitos(origem).zfill(4)
    dezoito = f"{nnn}{aaaa}{ramo_j}{tr}{oooo}"
    if len(dezoito) != 18:
        raise CnjError("Partes do número CNJ inválidas.")
    dv = digito_verificador(dezoito)
    return mascarar_cnj(f"{nnn}{dv}{aaaa}{ramo_j}{tr}{oooo}")


def verificar_dv(numero: str) -> bool:
    digitos = so_digitos(numero)
    if len(digitos) != CNJ_DIGITS:
        return False
    concatenado = _dezoito_sem_dv(digitos) + digitos[7:9]
    return int(concatenado) % 97 == 1


def validar_cnj(numero: str) -> str:
    """Valida tamanho, dígito verificador e tribunal. Retorna o número mascarado."""
    digitos = so_digitos(numero)
    if len(digitos) != CNJ_DIGITS:
        raise CnjError(f"Número CNJ deve ter 20 dígitos, veio {len(digitos)}.")
    if not verificar_dv(digitos):
        raise CnjError("Dígito verificador do número CNJ inválido.")
    alias_do_cnj(digitos)
    return mascarar_cnj(digitos)


def alias_do_cnj(numero: str) -> tuple[str, str]:
    """Retorna (digitos, alias Datajud) a partir do número CNJ."""
    digitos = so_digitos(numero)
    if len(digitos) != CNJ_DIGITS:
        raise CnjError(f"Número CNJ deve ter 20 dígitos, veio {len(digitos)}.")

    ramo = digitos[13]
    tr = digitos[14:16]

    if ramo == "1":
        # STF não tem endpoint na API pública do DataJud.
        raise CnjError("Consulta automática ao STF não está disponível na base pública.")
    if ramo == "3":
        return digitos, "stj"
    if ramo == "4":
        codigo = int(tr)
        if codigo < 1 or codigo > 6:
            raise CnjError(f"TRF desconhecido: {tr}")
        return digitos, f"trf{codigo}"
    if ramo == "5":
        if tr == "00":
            return digitos, "tst"
        codigo = int(tr)
        if codigo < 1 or codigo > 24:
            raise CnjError(f"TRT desconhecido: {tr}")
        return digitos, f"trt{codigo}"
    if ramo == "6":
        if tr == "00":
            return digitos, "tse"
        if tr not in TRE:
            raise CnjError(f"TRE desconhecido: {tr}")
        return digitos, TRE[tr]
    if ramo == "7":
        return digitos, "stm"
    if ramo == "8":
        if tr not in TJ_ESTADUAL:
            raise CnjError(f"Tribunal estadual desconhecido: {tr}")
        return digitos, TJ_ESTADUAL[tr]
    if ramo == "9":
        if tr not in TJM:
            raise CnjError(f"Justiça militar estadual não coberta para TR={tr}")
        return digitos, TJM[tr]

    raise CnjError(f"Ramo da Justiça não suportado: J={ramo}")
