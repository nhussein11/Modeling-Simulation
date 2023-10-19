import math
import random


class Simulation:
    def __init__(self, num_delays_required, mean_interarrival, mean_service):
        self.num_delays_required = num_delays_required
        self.mean_interarrival = mean_interarrival
        self.mean_service = mean_service
        # Non-parameterized variables
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
        self.time_next_event[1] = self.sim_time + self.expon(self.mean_interarrival)
        self.time_next_event[2] = 1.0e30

    def timing(self):
        min_time_next_event = 1.0e29
        self.next_event_type = 0

        for i in range(1, self.num_events + 1):
            if self.time_next_event[i] < min_time_next_event:
                min_time_next_event = self.time_next_event[i]
                self.next_event_type = i

        if self.next_event_type == 0:
            print(f"\nEvent list empty at time {self.sim_time}")
            exit(1)

        self.sim_time = min_time_next_event

    def arrive(self):
        self.time_next_event[1] = self.sim_time + self.expon(self.mean_interarrival)

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
            self.time_next_event[2] = self.sim_time + self.expon(self.mean_service)

    def depart(self):
        delay = 0.0
        if self.num_in_q == 0:
            self.server_status = self.IDLE
            self.time_next_event[2] = 1.0e30
        else:
            self.num_in_q -= 1
            delay = self.sim_time - self.time_arrival[1]
            self.total_of_delays += delay
            self.num_customers_attended += 1
            self.time_next_event[2] = self.sim_time + self.expon(self.mean_service)
            self.time_arrival = self.time_arrival[1:]

    def report(self):
        print(
            "\n\nAverage delay in queue {:11.3f} minutes".format(
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
        print("Time simulation ended {:12.3f} minutes".format(self.sim_time))

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


def main():
    num_delays_required, mean_interarrival, mean_service = map(
        float,
        input("Enter num_delays_required, mean_interarrival, mean_service: ").split(),
    )

    simulation = Simulation(num_delays_required, mean_interarrival, mean_service)
    simulation.run()


if __name__ == "__main__":
    main()
