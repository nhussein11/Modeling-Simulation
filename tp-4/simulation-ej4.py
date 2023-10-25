import random
import simpy


class Cajero:
    def __init__(self, env, id, service_mean, queue):
        self.env = env
        self.id = id
        self.service_mean = service_mean
        self.queue = queue
        self.service_times = []
        self.total_customers = 0

    def run(self):
        while True:
            if len(self.queue) > 0:
                customer = self.queue.pop(0)
                service_time = random.expovariate(1.0 / self.service_mean)
                yield self.env.timeout(service_time)
                self.service_times.append(service_time)
                self.total_customers += 1

                # Check if other queues have more customers, and move if necessary
                for other_cajero in cajeros:
                    if other_cajero.id != self.id and len(other_cajero.queue) < len(
                        self.queue
                    ):
                        other_cajero.queue.append(customer)
                        break

            else:
                # Wait for a customer to arrive
                yield self.env.timeout(1)


def simular_banco(num_cajeros, env):
    # Inicialización de las colas y cajeros
    global cajeros
    colas = [[] for _ in range(num_cajeros)]
    cajeros = [Cajero(env, i, 4.5, colas[i]) for i in range(num_cajeros)]

    # Add customers to queues at the beginning of the simulation
    for _ in range(100):  # 100 customers for initialization
        random.choice(colas).append(1)

    for cajero in cajeros:
        env.process(cajero.run())

    # Simular el banco de 9 a.m. a 5 p.m.
    env.run(until=8 * 60)  # 8 horas

    # Calcular métricas
    average_customers = sum(cajero.total_customers for cajero in cajeros) / num_cajeros
    average_queue_length = sum(len(cola) for cola in colas) / num_cajeros
    max_queue_length = max(len(cola) for cola in colas)

    return num_cajeros, average_customers, average_queue_length, max_queue_length


# Simular para diferentes números de cajeros
results = []

for num_cajeros in range(5, 8):
    env = simpy.Environment()
    result = simular_banco(num_cajeros, env)
    results.append(result)

# Imprimir resultados
print(
    "Número de Cajeros | Clientes Promedio en Colas | Longitud Promedio de Colas | Longitud Máxima de Colas"
)
for result in results:
    print(f"{result[0]:17} | {result[1]:27.2f} | {result[2]:29.2f} | {result[3]:25}")
