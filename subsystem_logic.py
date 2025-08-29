import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# =============================================================================
# Definição do sistema fuzzy SIF1
# =============================================================================
COF_range = np.linspace(0, 80, 1000)
AED_range = np.linspace(0, 40, 1000)
SIF1_range = np.linspace(0, 100, 1000)

COF = ctrl.Antecedent(COF_range, 'COF')
AED = ctrl.Antecedent(AED_range, 'AED')
SIF1 = ctrl.Consequent(SIF1_range, 'SIF1', defuzzify_method='centroid')

COF['baixa'] = fuzz.trapmf(COF.universe, [-30, -3.333, 35, 45])
COF['média'] = fuzz.trimf(COF.universe, [35, 45, 55])
COF['alta'] = fuzz.trapmf(COF.universe, [45, 55, 100, 100])

AED['baixa'] = fuzz.trapmf(AED.universe, [-15, -1.667, 2, 11])
AED['média'] = fuzz.trimf(AED.universe, [2, 11, 18])
AED['alta'] = fuzz.trapmf(AED.universe, [11, 18, 100, 100])

SIF1['Muito baixa'] = fuzz.trapmf(SIF1.universe, [0, 0, 10, 30])
SIF1['baixa'] = fuzz.trimf(SIF1.universe, [10, 30, 50])
SIF1['médio'] = fuzz.trimf(SIF1.universe, [30, 50, 70])
SIF1['alta'] = fuzz.trimf(SIF1.universe, [50, 70, 90])
SIF1['muito alta'] = fuzz.trapmf(SIF1.universe, [70, 90, 100, 100])

rule1 = ctrl.Rule(COF['baixa'] & AED['baixa'], SIF1['Muito baixa'])
rule2 = ctrl.Rule(COF['baixa'] & AED['média'], SIF1['baixa'])
rule3 = ctrl.Rule(COF['baixa'] & AED['alta'], SIF1['alta'])
rule4 = ctrl.Rule(COF['média'] & AED['baixa'], SIF1['baixa'])
rule5 = ctrl.Rule(COF['média'] & AED['média'], SIF1['médio'])
rule6 = ctrl.Rule(COF['média'] & AED['alta'], SIF1['muito alta'])
rule7 = ctrl.Rule(COF['alta'] & AED['baixa'], SIF1['alta'])
rule8 = ctrl.Rule(COF['alta'] & AED['média'], SIF1['muito alta'])
rule9 = ctrl.Rule(COF['alta'] & AED['alta'], SIF1['muito alta'])

sif1_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
sif1_sim = ctrl.ControlSystemSimulation(sif1_ctrl)

def evaluate_subsystem(cof_value, aed_value):
    """Avalia o subsistema SIF1."""
    sif1_sim.input['COF'] = cof_value
    sif1_sim.input['AED'] = aed_value
    sif1_sim.compute()
    return sif1_sim.output['SIF1']