import simpy
import random
import matplotlib.pyplot as plt

# Parameters
RANDOM_SEED = 42
INTERARRIVAL_TIME = 5  # Average time between car arrivals
SERVICE_TIME = 10      # Average time to wash a car
SIM_TIME = 100         # Total simulation time
NUM_WASHERS = 2        # Number of washing stations

# Metrics
wait_times = []
queue_lengths = []
server_utilization = [0] * NUM_WASHERS
last_event_time = 0

def car_wash(env, name, washers):
    global last_event_time
    arrival_time = env.now
    # Record queue length
    queue_lengths.append(len(washers.queue))
    
    with washers.request() as request:
        yield request
        wait = env.now - arrival_time
        wait_times.append(wait)
        
        # Assign the first available washer
        washer_id = washers.users.index(request)
        server_utilization[washer_id] += env.now - last_event_time
        last_event_time = env.now
        
        # Simulate service time
        service_time = random.expovariate(1.0 / SERVICE_TIME)
        yield env.timeout(service_time)
        
        # Update server utilization
        server_utilization[washer_id] += service_time

def car_generator(env, washers):
    car_count = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / INTERARRIVAL_TIME))
        car_count += 1
        env.process(car_wash(env, f'Car {car_count}', washers))

def run_simulation():
    global last_event_time
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    washers = simpy.Resource(env, capacity=NUM_WASHERS)
    env.process(car_generator(env, washers))
    env.run(until=SIM_TIME)
    
    # Calculate metrics
    avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0
    avg_queue = sum(queue_lengths) / len(queue_lengths) if queue_lengths else 0
    utilization = [(u / SIM_TIME) * 100 for u in server_utilization]
    
    print(f'Average wait time: {avg_wait:.2f} time units')
    print(f'Average queue length: {avg_queue:.2f} cars')
    for i, u in enumerate(utilization):
        print(f'Utilization of Washer {i+1}: {u:.2f}%')
    
    # Plotting
    plt.figure(figsize=(12, 6))
    
    # Queue Length Over Time
    plt.subplot(2, 1, 1)
    plt.plot(queue_lengths, label='Queue Length')
    plt.xlabel('Events')
    plt.ylabel('Number of Cars in Queue')
    plt.title('Queue Length Over Time')
    plt.legend()
    
    # Wait Time Distribution
    plt.subplot(2, 1, 2)
    plt.hist(wait_times, bins=20, edgecolor='black')
    plt.xlabel('Wait Time')
    plt.ylabel('Number of Cars')
    plt.title('Wait Time Distribution')
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    run_simulation()
