import simpy
import random

# Definir los tiempos de servicio para cada tipo de pieza y estación
TIEMPOS_SERVICIO = [
    [
        [0.50, 0.60, 0.85, 0.50],  # Estación 1 para tipo 1, 2, 5
        [1.10, 0.80],  # Estación 1 para tipo 2
        [1.20, 0.25, 0.70, 0.90, 1.00],  # Estación 1 para tipo 3
    ],
    [
        [0.70, 0.80, 0.95, 1.00],  # Estación 2 para tipo 1, 2, 5
        [1.10, 0.90],  # Estación 2 para tipo 2
        [1.25, 1.30, 1.35, 1.40, 1.45],  # Estación 2 para tipo 3
    ],
    # ... Definir tiempos de servicio para las demás estaciones
]


class Pieza:
    def __init__(self, env, tipo):
        self.env = env
        self.tipo = tipo


class Estacion:
    def __init__(self, env, id, num_maquinas):
        self.env = env
        self.id = id
        self.maquinas = simpy.Resource(env, capacity=num_maquinas)
        self.cola = simpy.Store(env)  # Usar simpy.Store para representar una cola

    def procesar_pieza(self, pieza):
        tiempo_servicio = random.choice(TIEMPOS_SERVICIO[self.id - 1][pieza.tipo - 1])
        yield self.env.timeout(tiempo_servicio)


def llegada_piezas(env, estaciones):
    while True:
        tipo_pieza = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
        pieza = Pieza(env, tipo_pieza)
        estacion_id = random.choice([0, 1, 2])
        env.process(procesar_en_estacion(env, pieza, estacion_id, estaciones))
        tiempo_entre_llegadas = random.expovariate(1 / 0.25)
        yield env.timeout(tiempo_entre_llegadas)


def procesar_en_estacion(env, pieza, estacion_id, estaciones):
    estacion = estaciones[estacion_id]
    with estacion.maquinas.request() as req:
        yield req
        if len(estacion.cola.items) > 0:
            print(
                f"Tiempo {env.now}: Pieza de tipo {pieza.tipo} en cola de estación {estacion_id + 1}"
            )
        yield env.process(estacion.procesar_pieza(pieza))
        print(
            f"Tiempo {env.now}: Pieza de tipo {pieza.tipo} terminada en estación {estacion_id + 1}"
        )


env = simpy.Environment()
num_maquinas_por_estacion = [3, 2, 4]  # Número de máquinas por estación
estaciones = [
    Estacion(env, i, num_maquinas_por_estacion[i])
    for i in range(len(num_maquinas_por_estacion))
]

env.process(llegada_piezas(env, estaciones))
env.run(until=365 * 24)
