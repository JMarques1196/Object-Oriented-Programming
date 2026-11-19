"""LISKOV SUBSTITUTION PRINCIPLE (LSP)
   Objects of a superclass should be replaceable with objects of its subclasses without breaking the 
   application or changing the expected behavior of the program.
   In our case, Dose and it's subclasses (DoseGHL and DoseGHA) respect the LSP, since the contract and promisses are constant
   If we were to add a subclass for a dosage interval, that would violate LSP, since 
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


class Regulacao:
    def __init__(self, bico: str, pressao_bar: float, litros_por_ha: float):
        if litros_por_ha <= 0:
            raise ValueError("L/ha tem de ser > 0")
        self._bico = bico
        self._pressao_bar = pressao_bar
        self._litros_por_ha = litros_por_ha

    @property
    def bico(self):
        return self._bico

    @property
    def pressao_bar(self):
        return self._pressao_bar

    @property
    def litros_por_ha(self):
        return self._litros_por_ha


class Dose(ABC):
    """Abstract superclass -> The contract all subclasses must abide by"""
    unidade = ""

    def __init__(self, valor: float):
        if valor <= 0:
            raise ValueError("Dosage must be > 0")
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    @abstractmethod
    def converter_dose(self, regulacao: Regulacao) -> float:
        """Contrcat. Pre-Condition: regulacao.litros_por_ha > 0. After: devolve g/HL > 0"""
        pass


class DoseGHL(Dose):
    unidade = "g/HL"

    def converter_dose(self, regulacao: Regulacao) -> float:  # OVERRIDE
        """Converted to g/HL: returns the value. regulacao does not enter the formula, but stays
        as a parameter to keep the signature of the superclass(Liskov)"""
        return self._valor


class DoseGHa(Dose):
    unidade = "g/ha"

    def converter_dose(self, regulacao: Regulacao) -> float:  # OVERRIDE: g/ha -> g/HL
        return self._valor / regulacao.litros_por_ha * 100


class Produto:
    def __init__(self, nome: str, dose: Dose):
        self._nome = nome
        self._dose = dose

    @property
    def nome(self):
        return self._nome

    @property
    def dose(self):
        return self._dose


class Pulverizador:
    def __init__(self, nome: str, capacidade_L: float):
        if capacidade_L <= 0:
            raise ValueError("capacidade inválida")
        self._nome = nome
        self._capacidade = capacidade_L
        self._regulacoes: list = []

    @property
    def capacidade_L(self):
        return self._capacidade

    def adicionar_regulacao(self, bico: str, pressao_bar: float, litros_por_ha: float) -> Regulacao:
        r = Regulacao(bico, pressao_bar, litros_por_ha)
        self._regulacoes.append(r)
        return r

    def regulacoes(self) -> list:
        return list(self._regulacoes)


@dataclass(frozen=True)
class Tratamento:
    data: str
    produto: str
    parcela_id: str
    parcela_nome: str
    volumes_depositos: tuple
    gramas_por_deposito: tuple
    gramas_total: float
    dose_valor: float
    dose_unidade: str
    bico: str
    pressao_bar: float
    litros_por_ha: float


class Parcela:
    """Composition. Contains the list of treatements"""
    def __init__(self, id: str, nome: str, area_ha: float):
        if area_ha <= 0:
            raise ValueError("área inválida")
        self._id = id
        self._nome = nome
        self._area = area_ha
        self._trat: list = []

    id = property(lambda s: s._id)  # Estável: sem setter

    @property
    def nome(self):
        return self._nome

    @property
    def area_ha(self):
        return self._area

    def renomear(self, novo: str):
        self._nome = novo  # O id não muda

    def adicionar_tratamento(self, t: Tratamento):
        self._trat.append(t)  # Só acrescenta

    def historico(self) -> list:
        return list(self._trat)  # Cópia de objetos imutáveis


class PlanoDeTratamento:
    def __init__(self, produto, pulverizador, regulacao, parcela):
        if regulacao not in pulverizador.regulacoes():
            raise ValueError("regulação não pertence ao pulverizador")
        self._prod = produto
        self._pulv = pulverizador
        self._reg = regulacao
        self._parc = parcela

    def calcular_volume_total(self) -> float:
        return self._parc.area_ha * self._reg.litros_por_ha

    def calcular_depositos(self) -> list:
        total = self.calcular_volume_total()
        cap = self._pulv.capacidade_L
        volumes = [cap] * int(total // cap)
        resto = round(total % cap, 6)
        if resto:
            volumes.append(resto)  # Último depósito parcial
        return volumes

    def gramas_por_deposito(self) -> list:
        # POLIMORFISMO: não sabe que subclasse concreta de Dose é
        g_hl = self._prod.dose.converter_dose(self._reg)
        return [round(g_hl * v / 100) for v in self.calcular_depositos()]

    def registar(self, data: str) -> Tratamento:
        datetime.strptime(data, "%d/%m/%Y")  # ValueError ANTES de alterar estado
        g = self.gramas_por_deposito()
        d = self._prod.dose
        r = self._reg
        t = Tratamento(
            data,
            self._prod.nome,
            self._parc.id,
            self._parc.nome,
            tuple(self.calcular_depositos()),
            tuple(g),
            sum(g),
            d.valor,
            d.unidade,
            r.bico,
            r.pressao_bar,
            r.litros_por_ha
        )
        self._parc.adicionar_tratamento(t)
        return t


pulv = Pulverizador("Costal 200 L", 200)
amarelo, vermelho = pulv.adicionar_regulacao("amarelo", 3, 400), pulv.adicionar_regulacao("vermelho", 3, 600)
olival, vinha = Parcela("p1", "Olival", 2.5), Parcela("p2", "Vinha", 1.3)
print(PlanoDeTratamento(Produto("Cobre", DoseGHL(150)), pulv, amarelo, olival).gramas_por_deposito())
print(PlanoDeTratamento(Produto("Enxofre", DoseGHa(600)), pulv, vermelho, vinha).gramas_por_deposito())
# -> [300, 300, 300, 300, 300]
# -> [200, 200, 200, 180]