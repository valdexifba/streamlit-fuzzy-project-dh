import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# =============================================================================
# Definição do sistema fuzzy principal
# =============================================================================

# Definindo os universos
DOP_range = np.linspace(0, 40, 1000)
OEA_range = np.linspace(0, 70, 1000)
SIF1_main_range = np.linspace(0, 100, 1000)
IFDH_range = np.linspace(0, 100, 1000)

# Variáveis fuzzy
DOP = ctrl.Antecedent(DOP_range, 'DOP')
OEA = ctrl.Antecedent(OEA_range, 'OEA')
SIF1_main = ctrl.Antecedent(SIF1_main_range, 'SIF1')
IFDH = ctrl.Consequent(IFDH_range, 'IFDH', defuzzify_method='centroid')

# Funções de pertinência
DOP['baixa'] = fuzz.trapmf(DOP.universe, [0, 0, 10, 25])
DOP['média'] = fuzz.trimf(DOP.universe, [10, 25, 40])
DOP['alta'] = fuzz.trapmf(DOP.universe, [25, 40, 40, 40])

OEA['baixa'] = fuzz.trapmf(OEA.universe, [0, 0, 15, 40])
OEA['média'] = fuzz.trimf(OEA.universe, [15, 40, 60])
OEA['alta'] = fuzz.trapmf(OEA.universe, [40, 60, 70, 70])

SIF1_main['baixa'] = fuzz.trapmf(SIF1_main.universe, [0, 0, 20, 50])
SIF1_main['médio'] = fuzz.trimf(SIF1_main.universe, [20, 50, 80])
SIF1_main['alta'] = fuzz.trapmf(SIF1_main.universe, [50, 80, 100, 100])

IFDH['muito baixa'] = fuzz.trapmf(IFDH.universe, [0, 0, 10, 30])
IFDH['baixa'] = fuzz.trimf(IFDH.universe, [10, 30, 50])
IFDH['médio'] = fuzz.trimf(IFDH.universe, [30, 50, 70])
IFDH['alta'] = fuzz.trimf(IFDH.universe, [50, 70, 90])
IFDH['muito alta'] = fuzz.trapmf(IFDH.universe, [70, 90, 100, 100])

# =============================================================================
# Definição das regras fuzzy (agora completas)
# =============================================================================
rules = []

# Regras para DOP = baixa
rules.append(ctrl.Rule(DOP['baixa'] & OEA['baixa'] & SIF1_main['baixa'], IFDH['muito baixa']))
rules.append(ctrl.Rule(DOP['baixa'] & OEA['baixa'] & SIF1_main['médio'], IFDH['muito baixa']))
rules.append(ctrl.Rule(DOP['baixa'] & OEA['baixa'] & SIF1_main['alta'], IFDH['baixa']))

rules.append(ctrl.Rule(DOP['baixa'] & OEA['média'] & SIF1_main['baixa'], IFDH['muito baixa']))
rules.append(ctrl.Rule(DOP['baixa'] & OEA['média'] & SIF1_main['médio'], IFDH['baixa']))
rules.append(ctrl.Rule(DOP['baixa'] & OEA['média'] & SIF1_main['alta'], IFDH['médio']))

rules.append(ctrl.Rule(DOP['baixa'] & OEA['alta'] & SIF1_main['baixa'], IFDH['médio']))
rules.append(ctrl.Rule(DOP['baixa'] & OEA['alta'] & SIF1_main['médio'], IFDH['alta']))
rules.append(ctrl.Rule(DOP['baixa'] & OEA['alta'] & SIF1_main['alta'], IFDH['muito alta']))

# Regras para DOP = média
rules.append(ctrl.Rule(DOP['média'] & OEA['baixa'] & SIF1_main['baixa'], IFDH['baixa']))
rules.append(ctrl.Rule(DOP['média'] & OEA['baixa'] & SIF1_main['médio'], IFDH['médio']))
rules.append(ctrl.Rule(DOP['média'] & OEA['baixa'] & SIF1_main['alta'], IFDH['alta']))

rules.append(ctrl.Rule(DOP['média'] & OEA['média'] & SIF1_main['baixa'], IFDH['médio']))
rules.append(ctrl.Rule(DOP['média'] & OEA['média'] & SIF1_main['médio'], IFDH['alta']))
rules.append(ctrl.Rule(DOP['média'] & OEA['média'] & SIF1_main['alta'], IFDH['muito alta']))

rules.append(ctrl.Rule(DOP['média'] & OEA['alta'] & SIF1_main['baixa'], IFDH['alta']))
rules.append(ctrl.Rule(DOP['média'] & OEA['alta'] & SIF1_main['médio'], IFDH['muito alta']))
rules.append(ctrl.Rule(DOP['média'] & OEA['alta'] & SIF1_main['alta'], IFDH['muito alta']))

# Regras para DOP = alta
rules.append(ctrl.Rule(DOP['alta'] & OEA['baixa'] & SIF1_main['baixa'], IFDH['alta']))
rules.append(ctrl.Rule(DOP['alta'] & OEA['baixa'] & SIF1_main['médio'], IFDH['muito alta']))
rules.append(ctrl.Rule(DOP['alta'] & OEA['baixa'] & SIF1_main['alta'], IFDH['muito alta']))

rules.append(ctrl.Rule(DOP['alta'] & OEA['média'] & SIF1_main['baixa'], IFDH['muito alta']))
rules.append(ctrl.Rule(DOP['alta'] & OEA['média'] & SIF1_main['médio'], IFDH['muito alta']))
rules.append(ctrl.Rule(DOP['alta'] & OEA['média'] & SIF1_main['alta'], IFDH['muito alta']))

rules.append(ctrl.Rule(DOP['alta'] & OEA['alta'] & SIF1_main['baixa'], IFDH['muito alta']))
rules.append(ctrl.Rule(DOP['alta'] & OEA['alta'] & SIF1_main['médio'], IFDH['muito alta']))
rules.append(ctrl.Rule(DOP['alta'] & OEA['alta'] & SIF1_main['alta'], IFDH['muito alta']))


# Montando o sistema de controle
ifdh_ctrl = ctrl.ControlSystem(rules)
ifdh_sim = ctrl.ControlSystemSimulation(ifdh_ctrl)

def evaluate_main_system(dop_value, oea_value, sif1_value):
    """Avalia o sistema fuzzy principal."""
    try:
        ifdh_sim.input['DOP'] = dop_value
        ifdh_sim.input['OEA'] = oea_value
        ifdh_sim.input['SIF1'] = sif1_value
        ifdh_sim.compute()
        return ifdh_sim.output['IFDH']
    except ValueError as e:
        print(f"Erro de cálculo: {e}. Verifique as entradas.")
        return 0.0
    except KeyError:
        print("Erro: O sistema não conseguiu calcular um valor para IFDH. Verifique as regras e os valores de entrada.")
        return 0.0