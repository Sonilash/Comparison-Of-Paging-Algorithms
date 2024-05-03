import random
import time
import matplotlib.pyplot as plt


class Process:
    def __init__(self, pid, num_pages):
        self.pid = pid
        self.num_pages = num_pages
        self.recently_accessed_pages = []

    def access_page(self):
        all_pages = list(range(self.num_pages))

        weights = [1] * self.num_pages

        for page in self.recently_accessed_pages:
            weights[page] *= 0.5

            if page - 1 >= 0:
                weights[page - 1] *= 2
            if page + 1 < self.num_pages:
                weights[page + 1] *= 2

        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        page = random.choices(all_pages, weights=weights, k=1)[0]

        self.recently_accessed_pages.append(page)
        if len(self.recently_accessed_pages) > 5:
            self.recently_accessed_pages.pop(0)

        return page


class Memory:
    def __init__(self, size):
        self.size = size
        self.pages = [0] * size
        self.allocation_timestamps = [0] * size
        self.access_timestamps = [0] * size
        self.reference_bits = [0] * size
        self.page_faults = 0
        self.page_accesses = 0

    def allocate_fifo(self, process_id, num_pages):
        if self.pages.count(0) > 0:
            for i in range(self.pages.index(0), self.size):
                if self.pages[i] == 0 and num_pages > 0:
                    self.pages[i] = process_id
                    self.allocation_timestamps[i] = time.time_ns()
                    self.access_timestamps[i] = time.time_ns()
                    self.reference_bits[i] = 0
                    num_pages -= 1
                elif num_pages == 0:
                    break
        else:
            while num_pages > 0:
                fifo_page = self.allocation_timestamps.index(min(self.allocation_timestamps))
                self.pages[fifo_page] = process_id
                self.allocation_timestamps[fifo_page] = time.time_ns()
                self.access_timestamps[fifo_page] = time.time_ns()
                self.reference_bits[fifo_page] = 0
                num_pages -= 1

        return True

    def allocate_random(self, process_id, num_pages):
        if self.pages.count(0) > 0:
            for i in range(self.pages.index(0), self.size):
                if self.pages[i] == 0 and num_pages > 0:
                    self.pages[i] = process_id
                    self.allocation_timestamps[i] = time.time_ns()
                    self.access_timestamps[i] = time.time_ns()
                    self.reference_bits[i] = 0
                    num_pages -= 1
                if num_pages == 0:
                    break
        else:
            while num_pages > 0:
                random_page = random.choice(
                    [i for i in range(self.size) if (self.pages[i] != 0 and self.pages[i] != process_id)])
                self.pages[random_page] = process_id
                self.allocation_timestamps[random_page] = time.time_ns()
                self.access_timestamps[random_page] = time.time_ns()
                self.reference_bits[random_page] = 0
                num_pages -= 1

        return True

    def allocate_second_chance(self, process_id, num_pages):
        pointer = 0
        if self.pages.count(0) > 0:
            for i in range(self.pages.index(0), self.size):
                if self.pages[i] == 0 and num_pages > 0:
                    self.pages[i] = process_id
                    self.allocation_timestamps[i] = time.time_ns()
                    self.access_timestamps[i] = time.time_ns()
                    self.reference_bits[i] = 0
                    num_pages -= 1
                if num_pages == 0:
                    break

        else:
            while num_pages > 0:
                if self.reference_bits[pointer] == 1:
                    self.reference_bits[pointer] = 0
                else:
                    self.pages[pointer] = process_id
                    self.allocation_timestamps[pointer] = time.time_ns()
                    self.access_timestamps[pointer] = time.time_ns()
                    self.reference_bits[pointer] = 0
                    num_pages -= 1
                pointer = (pointer + 1) % self.size

        return True

    def allocate_mru(self, process_id, num_pages):
        if self.pages.count(0) > 0:
            for i in range(self.pages.index(0), self.size):
                if self.pages[i] == 0 and num_pages > 0:
                    self.pages[i] = process_id
                    self.allocation_timestamps[i] = time.time_ns()
                    self.access_timestamps[i] = time.time_ns()
                    self.reference_bits[i] = 0
                    num_pages -= 1
                if num_pages == 0:
                    break

        else:
            while num_pages > 0:
                filtered_access_timestamps = [self.access_timestamps[i] if self.pages[i] != process_id else -1 for i in
                                              range(self.size)]
                mru_page = filtered_access_timestamps.index(max(filtered_access_timestamps))
                self.pages[mru_page] = process_id
                self.access_timestamps[mru_page] = time.time_ns()
                self.reference_bits[mru_page] = 0
                num_pages -= 1

        return True

    def allocate_lru(self, process_id, num_pages):
        if self.pages.count(0):
            for i in range(self.pages.index(0), self.size):
                if num_pages == 0:
                    break
                if self.pages[i] == 0:
                    self.pages[i] = process_id
                    self.allocation_timestamps[i] = time.time_ns()
                    self.access_timestamps[i] = time.time_ns()
                    self.reference_bits[i] = 0
                    num_pages -= 1

        else:
            while num_pages > 0:
                lru_page = self.access_timestamps.index(min(self.access_timestamps))
                self.pages[lru_page] = process_id
                self.allocation_timestamps[lru_page] = time.time_ns()
                self.access_timestamps[lru_page] = time.time_ns()
                self.reference_bits[lru_page] = 0
                num_pages -= 1

        return True

    def deallocate(self, process_id):
        for i in range(self.size):
            if self.pages[i] == process_id:
                self.pages[i] = 0
                self.allocation_timestamps[i] = 0
                self.access_timestamps[i] = 0
                self.reference_bits[i] = 0

    def print_memory(self):
        print(self.pages)

    def access_page(self, process, page):
        self.page_accesses += 1
        if process.pid in self.pages:
            indices = [i for i, x in enumerate(self.pages) if x == process.pid]
            if page in indices:
                self.reference_bits[page] = 1
                self.access_timestamps[page] = time.time_ns()

            return True

        self.page_faults += 1
        return False


def main():
    memory = Memory(1024)

    processes = [Process(i, random.randint(16, 64)) for i in range(1, 129)]
    total_pages = sum([process.num_pages for process in processes])

    print("Initial process details:")
    for process in processes:
        print(f"Process ID: {process.pid}, Number of Pages: {process.num_pages}")

    algorithms = [memory.allocate_fifo, memory.allocate_lru, memory.allocate_random,
                  memory.allocate_second_chance, memory.allocate_mru]
    algorithm_names = ["FIFO", "LRU", "Random", "Second Chance", "MRU"]
    times = []
    page_faults = []
    for algorithm, name in zip(algorithms, algorithm_names):
        allocated_processes = []
        print(f"\n{name} Algorithm:")
        total_time = 0
        total_page_faults = 0
        for process in processes:
            start_time = time.perf_counter() * 1000
            if algorithm(process.pid, process.num_pages):
                # print(f"Allocated {process.num_pages} pages for process {process.pid}")
                allocated_processes.append(process)
            else:
                print(f"Failed to allocate {process.num_pages} pages for process {process.pid}")

            end_time = time.perf_counter() * 1000
            total_time += end_time - start_time
            total_page_faults += memory.page_faults
            # memory.print_memory()

            for i in range(20):
                if allocated_processes:
                    weights = [1 / (2 ** process.pid) for process in allocated_processes]
                    random_process = random.choices(allocated_processes, weights=weights, k=1)[0]
                if random_process.recently_accessed_pages and random.random() < 0.6:
                    random_page = random.choice(random_process.recently_accessed_pages)
                else:
                    random_page = random.randint(0, random_process.num_pages - 1)
                memory.access_page(random_process, random_page)

        for process in processes:
            memory.deallocate(process.pid)

        avg_time_per_process = total_time / len(processes)
        print(f"Average time taken per process: {round(avg_time_per_process, 2)} milliseconds")
        print(f"Total time taken for allocation: {round(total_time, 2)} milliseconds")
        print(f"Total Page Faults: {total_page_faults}")
        print(f"Page Fault Rate: {round(memory.page_faults / memory.page_accesses * 100, 2)}%")

        times.append(total_time)
        page_faults.append(total_page_faults)
        memory.page_faults = 0
        memory.page_accesses = 0

    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    fig, axs = plt.subplots(2, 1)

    for i in range(len(algorithm_names)):
        axs[0].bar(algorithm_names[i], times[i], color=colors[i], label=algorithm_names[i])
        axs[0].text(i, times[i], algorithm_names[i], ha='center')
    axs[0].set_xlabel('Algorithms')
    axs[0].set_ylabel('Time (milliseconds)')
    axs[0].set_title('Time taken by each algorithm')

    for i in range(len(algorithm_names)):
        axs[1].bar(algorithm_names[i], page_faults[i], color=colors[i], label=algorithm_names[i])
        axs[1].text(i, page_faults[i], algorithm_names[i], ha='center')
    axs[1].set_xlabel('Algorithms')
    axs[1].set_ylabel('Page Faults')
    axs[1].set_title('Page Faults by each algorithm')

    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    main()
