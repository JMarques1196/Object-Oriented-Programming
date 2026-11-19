# Primeiras Classes do Projeto AgroDose em Python (AF 3.1 + AF 3.2)

# Classes and Candidates to Classes:

# Regulation needs pressure and Tip
class Regulacao:
    """ When using __init__ , self links the method to a specific instance
        Private atributes use "_" (underscore). Does the same thing as private in C
        Public ones do not need it
    """
    def __init__(self, bico, pressao, litros_por_ha):
        if litros_por_ha <= 0:
            raise ValueError("Liters per Ha Needs to be greater than 0")
        self._bico = bico
        self._pressao = pressao
        self._litros_por_ha = litros_por_ha


    @property
    def litros_por_ha(self):
        return self._litros_por_ha

    @property
    def bico(self): 
        return self._bico

    @property
    def pressao_bar(self): 
        return self._pressao


""" Dose violates OCP (does not support expansion without modifying existing code) 
    Solution: Dose becomes a superclass
    By making Dose a superclass, Dose becomes abstract:
    That means variables like unidade become a class atribute. 
    Despite Not being used in Dose itself it will be used in subclasses like DoseGHL.
    The same goes for converter_dose as it also forces the subclasses to implement methods
    If the method is missing in any subclass a NotImplementedError is thrown
 """
class Dose:
    unidade = None

    def __init__ (self, valor): 

        if valor <= 0:
            raise ValueError("Dose value invalid")
        self._valor = valor

    @property  
    def valor(self):
        return self._valor
    @property
    def converter_dose(self, regulacao):
        raise NotImplementedError


""" Dose Subclasses
    Subclasses do not need a __init__, as it inherits the constructor from the superclass
    unless there are new atribtes to be added.
    - OVERRIDE: overrides the methods declared in the superclass, in this case converter_dose. We used a generic 
    implementaton/contract in the superclass.
"""
class DoseGHL(Dose):
    unidade = "g/HL"
    def converter_dose(self, regulacao):
        return self._valor  # Usa o _valor diretamente[cite: 6]

class DoseGHa(Dose):
    unidade = "g/HA"
    def converter_dose(self, regulacao): 
        return self._valor / regulacao.litros_por_ha * 100

class Produto:
    def __init__(self, nome, dose): self.nome, self.dose = nome, dose

""" 
    Composition: A class that has its own instances of objects
    In this case, Pulverizador has it's own instance of Regulacao
"""
class Pulverizador: # COMPOSIÇÃO: cria e possui as suas Regulacao
    def __init__(self, nome, capacidade_L):
        if capacidade_L <= 0: raise ValueError("capacidade inválida")
        self._nome, self._capacidade, self._regulacoes = nome, capacidade_L, []
    @property
    def capacidade_L(self): return self._capacidade
    def adicionar_regulacao(self, bico, pressao_bar, litros_por_ha):
        r = Regulacao(bico, pressao_bar, litros_por_ha)
        self._regulacoes.append(r)
        return r
    def regulacoes(self): return list(self._regulacoes)

class Tratamento: # fotografia: valores copiados, sem métodos de edição
    def __init__(self, data, produto, parcela_id, parcela_nome, gramas, dose, lha):
        self.data, self.produto, self.gramas = data, produto, gramas
        self.parcela_id, self.parcela_nome = parcela_id, parcela_nome
        self.dose, self.litros_por_ha = dose, lha

""" Parcela is also a Composition """
class Parcela: 
    def __init__(self, id, nome, area_ha):
        if area_ha <= 0: 
            raise ValueError("área inválida")
        self.id = id
        self.nome = nome
        self._area = area_ha
        self._trat = []

    @property
    def area_ha(self): 
        return self._area

    def adicionar_tratamento(self, t): 
        self._trat.append(t)

    def historico(self): 
        return list(self._trat)


"""
    Agregation: A class that references and modifies other objects without creating its own.
    In this case PlanoDeTratamento
"""
class PlanoDeTratamento: # AGREGAÇÃO: junta referências de instâncias existentes
    def __init__(self, produto, pulverizador, regulacao, parcela):
        if regulacao not in pulverizador.regulacoes():
            raise ValueError("regulação não pertence ao pulverizador")
        self._prod = produto
        self._pulv = pulverizador
        self._reg = regulacao
        self._parc = parcela

    def calcular_volume_total(self):
        return self._parc.area_ha * self._reg.litros_por_ha

    def calcular_depositos(self):
        total, cap = self.calcular_volume_total(), self._pulv.capacidade_L
        volumes = [cap] * int(total // cap)
        if total % cap:
            volumes.append(total % cap)
        return volumes

    def gramas_por_deposito(self):
        # POLIMORFISMO: chama converter_dose sem saber se é DoseGHL ou DoseGHa
        g_hl = self._prod.dose.converter_dose(self._reg)
        return [round(g_hl * v / 100) for v in self.calcular_depositos()]

    def registar(self, data):
        g = self.gramas_por_deposito()
        d = self._prod.dose
        t = Tratamento(data, self._prod.nome, self._parc.id, self._parc.nome,
                       sum(g), d.valor, self._reg.litros_por_ha)
        self._parc.adicionar_tratamento(t)
        return t




""" Creation and Usage (Also Work as Integration Tests) """

pulv = Pulverizador("Costal 200 L", 200)
amarelo = pulv.adicionar_regulacao("amarelo", 3, 400)
vermelho = pulv.adicionar_regulacao("vermelho", 3, 600)
cobre = Produto("Cobre", DoseGHL(150))
enxofre = Produto("Enxofre", DoseGHa(600))
olival, vinha = Parcela("p1", "Olival", 2.5), Parcela("p2", "Vinha", 1.3)
plano_olival = PlanoDeTratamento(cobre, pulv, amarelo, olival)
plano_vinha = PlanoDeTratamento(enxofre, pulv, vermelho, vinha)
print(plano_olival.gramas_por_deposito()) # [300, 300, 300, 300, 300]
print(plano_vinha.gramas_por_deposito()) # [200, 200, 200, 180]
# Teste unitário do override: 600 g/ha com 400 L/ha = 150 g/HL
assert DoseGHa(600).converter_dose(amarelo) == 150
assert DoseGHL(150).converter_dose(amarelo) == 150
t = plano_olival.registar("07/10/2026") # integração: Plano cria Tratamento
assert olival.historico() == [t] and t.gramas == 1500