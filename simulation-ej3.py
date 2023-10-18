import math
import random


class Simulation:
    def __init__(
        self, num_delays_required, mean_thinking_time, mean_service_time, num_terminals
    ):
        self.num_delays_required = num_delays_required
        self.mean_thinking_time = mean_thinking_time
        self.mean_service_time = mean_service_time
        self.num_terminals = num_terminals

        self.Q_LIMIT = 100
        self.BUSY = 1
        self.IDLE = 0
        self.next_event_type = 0
        self.num_customers_attended = 0
        self.num_events = 2
        self.num_in_q = 0
        self.server_status = self.IDLE
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.sim_time = 0.0
        self.time_arrival = [0.0] * (self.Q_LIMIT + 1)
        self.time_last_event = 0.0
        self.time_next_event = [0.0] * (self.num_events + 1)
        self.total_of_delays = 0.0

    def initialize(self):
        self.sim_time = 0.0
        self.server_status = self.IDLE
        self.num_in_q = 0
        self.time_last_event = 0.0
        self.num_customers_attended = 0
        self.total_of_delays = 0.0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.time_next_event[1] = self.sim_time + self.expon(self.mean_thinking_time)
        self.time_next_event[2] = 1.0e30

    def timing(self):
        min_time_next_event = min(self.time_next_event[1], self.time_next_event[2])
        self.next_event_type = (
            1 if min_time_next_event == self.time_next_event[1] else 2
        )
        self.sim_time = min_time_next_event

    def arrive(self):
        self.time_next_event[1] = self.sim_time + self.expon(self.mean_thinking_time)

        if self.server_status == self.BUSY:
            self.num_in_q += 1

            if self.num_in_q > self.Q_LIMIT:
                print(f"\nOverflow of the array time_arrival at time {self.sim_time}")
                exit(2)
            self.time_arrival[self.num_in_q] = self.sim_time

        else:
            delay = 0.0
            self.total_of_delays += delay
            self.num_customers_attended += 1
            self.server_status = self.BUSY
            self.time_next_event[2] = self.sim_time + self.quantum_time()

    def quantum_time(self):
        quantum = 0.1  # Quantum of service time
        swap_time = 0.015  # Time for context switch
        remaining_service_time = self.expon(self.mean_service_time)
        if remaining_service_time <= quantum:
            return remaining_service_time + swap_time
        else:
            return quantum + swap_time

    def depart(self):
        delay = 0.0
        if self.num_in_q == 0:
            self.server_status = self.IDLE
            self.time_next_event[2] = 1.0e30
        else:
            delay = self.sim_time - self.time_arrival[1]
            self.total_of_delays += delay
            self.num_customers_attended += 1

            # Shift the elements in the array to the left to remove the first element
            for i in range(1, self.num_in_q):
                self.time_arrival[i] = self.time_arrival[i + 1]

            self.num_in_q -= 1
            self.time_next_event[2] = self.sim_time + self.quantum_time()

    def update_time_avg_stats(self):
        time_since_last_event = self.sim_time - self.time_last_event
        self.time_last_event = self.sim_time
        self.area_num_in_q += self.num_in_q * time_since_last_event
        self.area_server_status += self.server_status * time_since_last_event

    def expon(self, mean):
        return (1 / mean) * math.log1p(random.random())

    def run(self):
        self.initialize()

        while self.num_customers_attended < self.num_delays_required:
            self.timing()
            self.update_time_avg_stats()

            if self.next_event_type == 1:
                self.arrive()
            elif self.next_event_type == 2:
                self.depart()

        self.report()

    def report(self):
        print(
            "\n\nAverage delay in queue {:11.3f} seconds".format(
                self.total_of_delays / self.num_customers_attended
            )
        )
        print(
            "Average number in queue {:10.3f}".format(
                self.area_num_in_q / self.sim_time
            )
        )
        print(
            "Server utilization {:15.3f}".format(
                self.area_server_status / self.sim_time
            )
        )
        print("Time simulation ended {:12.3f} seconds".format(self.sim_time))


def main():
    num_delays_required = 1000
    mean_thinking_time = 25  # in seconds
    mean_service_time = 0.8  # in seconds
    num_terminals = 5  # You can change the number of terminals here

    simulation = Simulation(
        num_delays_required, mean_thinking_time, mean_service_time, num_terminals
    )
    simulation.run()


if __name__ == "__main__":
    main()
