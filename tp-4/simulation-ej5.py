import random
import simpy

# Definir los parámetros del sistema
NUM_DIAS = 365
NUM_HORAS_DIA = 8

# Definir las estaciones y el número de máquinas en cada estación
NUM_MAQUINAS = [3, 2, 4, 3, 1]

# Definir los tiempos de servicio medios para cada tipo de trabajo y cada tarea
TIEMPOS_SERVICIO = {
    1: [0.5, 0.6, 0.85, 0.5],
    2: [1.1, 0.8, 0.75],
    3: [1.2, 0.25, 0.7, 0.9, 1.0],
}

# Definir la distribución de llegada de piezas
TIEMPO_ENTRE_ARRIBOS = 0.25  # Media en horas

# Variables para métricas
total_retraso = 0
total_utilizacion_maquinas = [0 for _ in range(len(NUM_MAQUINAS))]
total_piezas_en_cola = 0
total_piezas_procesadas = {1: 0, 2: 0, 3: 0}


# Clase para el sistema de fabricación
class SistemaFabricacion:
    def __init__(self, env):
        self.env = env
        self.colas = [simpy.Store(env) for _ in range(len(NUM_MAQUINAS))]
        self.utilizacion_maquinas = [0 for _ in range(len(NUM_MAQUINAS))]

    def procesar_pieza(self, tipo):
        estaciones = {1: [2, 0, 1, 4], 2: [3, 0, 2], 3: [1, 4, 0, 3, 2]}
        ruta = estaciones[tipo]
        retraso_inicial = self.env.now
        for idx, tarea in enumerate(ruta):
            yield self.env.timeout(random.expovariate(1 / TIEMPOS_SERVICIO[tipo][idx]))
            with self.colas[tarea].get() as maquina:
                yield maquina
        retraso_final = self.env.now - retraso_inicial
        global total_retraso
        total_retraso += retraso_final
        total_piezas_procesadas[tipo] += 1

    def llegada_pieza(self, tipo):
        while True:
            yield self.env.timeout(random.expovariate(1 / TIEMPO_ENTRE_ARRIBOS))
            self.env.process(self.procesar_pieza(tipo))


# Simulación
env = simpy.Environment()
sistema = SistemaFabricacion(env)

for i in range(len(NUM_MAQUINAS)):
    for j in range(NUM_MAQUINAS[i]):
        sistema.colas[i].put(env.event())

for tipo in range(1, 4):
    env.process(sistema.llegada_pieza(tipo))

env.run(until=NUM_DIAS * NUM_HORAS_DIA)

# Calcular métricas de desempeño
for i in range(len(NUM_MAQUINAS)):
    total_utilizacion_maquinas[i] = sistema.utilizacion_maquinas[i] / (
        NUM_DIAS * NUM_HORAS_DIA
    )
    total_piezas_en_cola += sum(len(cola.items) for cola in sistema.colas)

# Calcular retraso promedio en las colas
total_piezas_procesadas_sum = sum(total_piezas_procesadas.values())
retraso_promedio = (
    total_retraso / total_piezas_procesadas_sum
    if total_piezas_procesadas_sum > 0
    else 0
)

# Calcular número promedio de piezas en cola
promedio_piezas_en_cola = total_piezas_en_cola / (NUM_DIAS * NUM_HORAS_DIA)

# Mostrar resultados
print(f"Retraso promedio en las colas: {retraso_promedio:.2f} horas")
print(f"Utilización promedio de las máquinas: {total_utilizacion_maquinas}")
print(f"Número promedio de piezas en cola: {promedio_piezas_en_cola:.2f}")
print(f"Número total de piezas procesadas: {sum(total_piezas_procesadas.values())}")
