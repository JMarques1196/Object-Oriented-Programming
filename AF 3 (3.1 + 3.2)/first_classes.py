# Primeiras Classes do Projeto AgroDose em Python (AF 3.1 + AF 3.2)

# Classes and Candidates to Classes:

# Regulation needs pressure and Tip
class Regulacao:
    """ When using __init__ , self links the method to a specific instance
        Private atributes use "_" (underscore). Does the same thing as private in C
        Public ones do not need it
    """
    def __init__ (self, bico, pressao, litros_por_ha):

        if litros_por_ha <= 0:
            raise ValueError("Liters per Ha Needs to be greater than 0")
        
        self._bico, self._pressao, self._litros_por_ha = bico, pressao, litros_por_ha

        """ @property functions as a getter in C. Allows the class to expose private atributes."""
        @property
        def litros_por_ha(self):
            return self._litros_por_ha;



# Gets the parameters for the conversions
class Dose:
    unidades = ("g/HL", "g/ha")

    def __init__ (self, valor, unidade): # init method is used to assign values to object properties
        """ Using init we can simply initiate a object like dose = Dose(valor, unidade) instead of
            having to set each value individualy lile dose = Dose(), dose.valor = 10, dose.unidade = g/hl
            When creating a new instance, ie: amarelo = regulacao (...) , the self takes on amarelo (the name of the instance)
        """
        if unidade not in Dose.unidades:
            raise ValueError("Unidade Inválida");
        self._valor, self._unidade = valor, unidade

    def converter_dose(self, regulacao):
        # Regulation is received as a parameter and is not saved
        if self._unidade == "g/HL":
            return self._valor;
        return self._valor / regulacao._litros_por_ha * 100

"""
This class contains methods for the calculations
"""
class PlanoDeTratamento:

    def __init__ (self, dose, regulacao, capacidade_L, area_ha):
        self._dose, self._regulacao, self._capacidade_L, self._area = dose, regulacao, capacidade_L, area_ha

    """
        Volume total de calda + numero de depositos

    """
    def calcular_volume_total(self):
        return self._area * self._regulacao._litros_por_ha

    def gramas_por_deposito(self):
        total = self.calcular_volume_total()
        g_hl = self._dose.converter_dose(self._regulacao)

        volumes = [self._capacidade_L] * int(total // self._capacidade_L)
        if total % self._capacidade_L: # último depósito parcial
            volumes.append(total % self._capacidade_L)
        return [round(g_hl * v / 100) for v in volumes]


""" Testing the created classes """
# --- instâncias (objetos) e chamadas ---
amarelo = Regulacao("amarelo", 3, 400)
vermelho = Regulacao("vermelho", 3, 600)
cobre = Dose(150, "g/HL")
enxofre = Dose(600, "g/ha")
plano_olival = PlanoDeTratamento(cobre, amarelo, 200, 2.5)
plano_vinha = PlanoDeTratamento(enxofre, vermelho, 200, 1.3)
print(plano_olival.gramas_por_deposito()) # [300, 300, 300, 300, 300]
print(plano_vinha.gramas_por_deposito()) # [200, 200, 200, 180]
print(plano_olival is plano_vinha) # False: identidades distintas