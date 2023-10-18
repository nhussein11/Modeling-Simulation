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
        self.response_times = []

    def run(self):
        while True:
            arrival_time = self.env.now

            # Tiempo de pensamiento del terminal (llegada a la cola)
            yield self.env.timeout(random.expovariate(1.0 / self.thinking_time))

            # Tiempo de servicio del trabajo en la CPU
            service_time = random.expovariate(1.0 / self.service_mean)
            while service_time > 0:
                processing_time = min(service_time, self.quantum)

                with self.cpu.request() as req:
                    yield req
                    yield self.env.timeout(processing_time)
                    service_time -= processing_time

                    if service_time > 0:
                        yield self.env.timeout(0.015)
                    else:
                        response_time = self.env.now - arrival_time
                        self.response_times.append(response_time)

    def run_process(self, remaining_time):
        while remaining_time > 0:
            processing_time = min(remaining_time, self.quantum)

            with self.cpu.request() as req:
                yield req
                yield self.env.timeout(processing_time)
                remaining_time -= processing_time
                yield self.env.timeout(0.015)


def simular_sistema(n):
    env = simpy.Environment()
    cpu = simpy.Resource(env, capacity=1)

    terminals = [Terminal(env, i, 25, 0.8, cpu, 0.1) for i in range(n)]
    for terminal in terminals:
        env.process(terminal.run())

    env.run(until=1000)  # Simular para 1000 terminaciones de trabajos

    total_response_time = sum(
        response_time
        for terminal in terminals
        for response_time in terminal.response_times
    )
    average_response_time = total_response_time / len(
        [
            response_time
            for terminal in terminals
            for response_time in terminal.response_times
        ]
    )

    total_wait_time = sum(
        response_time - 0.8
        for terminal in terminals
        for response_time in terminal.response_times
    )
    average_wait_time = total_wait_time / len(
        [
            response_time
            for terminal in terminals
            for response_time in terminal.response_times
        ]
    )

    cpu_utilization = sum(terminal.cpu.count for terminal in terminals) / (n * env.now)

    return n, average_response_time, average_wait_time, cpu_utilization


# Simulación para diferentes números de terminales
results = []

for n in range(10, 81, 10):
    result = simular_sistema(n)
    results.append(result)

# Imprimir resultados
print(
    "Número de Terminales | Tiempo de Respuesta Promedio | Tiempo de Espera Promedio | Utilización de la CPU"
)
for result in results:
    print(f"{result[0]:20} | {result[1]:30.2f} | {result[2]:24.2f} | {result[3]:23.2f}")
