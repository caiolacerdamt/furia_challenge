def validar_cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calcular_digito(cpf_parcial):
        soma = sum(int(digito) * peso for digito, peso in zip(cpf_parcial, range(len(cpf_parcial)+1, 1, -1)))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    primeiro_digito = calcular_digito(cpf[:9])
    segundo_digito = calcular_digito(cpf[:9] + primeiro_digito)

    return cpf[-2:] == primeiro_digito + segundo_digito