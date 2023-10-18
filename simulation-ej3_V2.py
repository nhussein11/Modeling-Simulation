import random
import simpy


class Terminal:
    def __init__(self, env, id, thinking_time, service_mean, cpu, quantum):
        self.env = env
        self.id = id
        self.thinking_time = thinking_time
        self.service_mean = service_mean
        self.cpu = cpu
        self.quantum = quantum
        self.response_times = []  # Lista para almacenar los tiempos de respuesta

    def run(self):
        while True:
            arrival_time = self.env.now  # Registro del tiempo de llegada a la cola

            # Tiempo de pensamiento del terminal (llegada a la cola)
            yield self.env.timeout(random.expovariate(1.0 / self.thinking_time))

            # Tiempo de servicio del trabajo en la CPU
            service_time = random.expovariate(1.0 / self.service_mean)
            while service_time > 0:
                # Quantum de tiempo de CPU
                processing_time = min(service_time, self.quantum)

                # Solicitar el recurso de CPU
                with self.cpu.request() as req:
                    yield req
                    # Procesamiento del trabajo en la CPU
                    yield self.env.timeout(processing_time)
                    service_time -= processing_time

                    # Verificar si el trabajo ha terminado o si aún queda tiempo
                    if service_time > 0:
                        # Si aún queda tiempo, liberar la CPU y volver a la cola
                        yield self.env.timeout(0.015)  # Tiempo de intercambio fijo
                    else:
                        # Si el trabajo ha terminado, calcular el tiempo de respuesta y agregarlo a la lista
                        response_time = self.env.now - arrival_time
                        self.response_times.append(response_time)

            # Trabajo completado, vuelve al terminal


# Configuración de la simulación
random.seed(42)  # Semilla para reproducibilidad
num_terminals = 5  # Número inicial de terminales
service_mean = 0.8  # Media del tiempo de servicio (en segundos)
quantum = 0.1  # Quantum de tiempo de CPU (en segundos)

env = simpy.Environment()
cpu = simpy.Resource(env, capacity=1)

terminals = [
    Terminal(env, i, 25, service_mean, cpu, quantum) for i in range(num_terminals)
]
for terminal in terminals:
    env.process(terminal.run())

# Ejecutar la simulación
env.run(until=30)  # Tiempo de simulación (en segundos)

# Calcular estadísticas
total_response_time = sum(
    response_time for terminal in terminals for response_time in terminal.response_times
)
average_response_time = total_response_time / len(
    [
        response_time
        for terminal in terminals
        for response_time in terminal.response_times
    ]
)

print("Tiempo medio de respuesta:", average_response_time)
