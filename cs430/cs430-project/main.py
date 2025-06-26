import argparse

class JobScheduling:
    def __init__(self, file_path, debug=False):
        self.file_path = file_path
        self.jobs = []                   # jobs[j] = (r_j, d_j) where r_j is the release time and d_j is the deadline of job j
        self.machines = []               # machines[t] = (c_t, B_t) where c_t is the cost per time unit and B_t is the budget of machine type t, types are equivalent to indeses of the list
        self.num_jobs = 0
        self.num_machines = 0
        self.min_cost_per_job = []  # min_cost_for_each_job[i] = min cost to schedule job i is equivalent to A in the recurrence relation
        self.batch_choice = []  
        self.debug = debug

    def parse_input(self):
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
            
        self.num_jobs = int(lines[0].strip())
        lines = lines[1:]
        
        while len(lines[0]) >= 4: 
            r, d = map(int, lines[0].strip().split())
            self.jobs.append((r, d))
            lines = lines[1:]
            
        if self.num_jobs != len(self.jobs):
            print(f"Number of jobs: {self.num_jobs}, Number of jobs listed: {len(self.jobs)}")
            raise ValueError("Number of jobs does not match the provided data.")
                
        self.num_machines = int(lines[0].strip())
        lines = lines[1:]
        
        while len(lines[0]) == 4: 
            c, B = map(int, lines[0].strip().split())
            self.machines.append((c, B))
            lines = lines[1:]
            if lines == []:
                break
        
        if self.num_machines != len(self.machines):
            raise ValueError("Number of machines does not match the provided data.")
        
        print("-------INPUT DATA-------")
        print(f"Number of jobs: {self.num_jobs}")
        print(f"Jobs: {self.jobs}")
        print(f"Number of machines: {self.num_machines}")
        print(f"Machines: {self.machines}")
    
        
    def schedule_jobs(self):
        self.min_cost_per_job = [float('inf')] * (self.num_jobs + 1)
        self.batch_choice = [None] * (self.num_jobs + 1)           
        job_q = self.num_jobs               # last job in the queue (in the recursive function: q)  
        return self.min_cost_to_schedule(job_q)


    def min_cost_to_schedule(self, job_index):
        if self.debug:
            print(f"\n---Calculating minimum cost for job {job_index}...---")
        if job_index == 0:           # Base case: if there are no jobs to schedule, the cost is 0  
            return 0
        if self.min_cost_per_job[job_index] != float('inf'):       # if the value is already calculated, return it
            return self.min_cost_per_job[job_index]                # when using job_index with min_cost_per_job, we don't subtract 1 from it, because 0th job represents the base case when we don't have any jobs to schedule
        
        tmp_job_index = job_index
        max_number_of_intersecting_jobs = 1
        
        if self.debug:
            print(f"Finding max intersecting jobs for job {job_index} ({self.jobs[job_index - 1]})")
        
        for time in range(self.jobs[job_index - 1][1], self.jobs[job_index - 1][0] - 1, -1):    # when using job_index with jobs, we subtract 1 from it, because the list is 0-indexed
            if self.debug:
                print(f"Current time: {time}")
            for job in range(tmp_job_index - 1, 0, -1):                                     # job is the index of the job that we are checking if it intersects with the current job
                if self.debug:
                    print(f"Checking if job {job} intersects with job {job_index}...")
                    print(f"Job {job} time interval: {self.jobs[job - 1][0]} and {self.jobs[job - 1][1]}")
                if self.jobs[job - 1][0] <= time and time <= self.jobs[job - 1][1]:
                    if self.debug:
                        print(f"Job {job} intersects with job {job_index}")
                    max_number_of_intersecting_jobs += 1
                    tmp_job_index = tmp_job_index - 1
                else:
                    break
        if self.debug:
            print(f"Max number of intersecting jobs: {max_number_of_intersecting_jobs}\n")
                
        for num_jobs_to_execute in range(1, max_number_of_intersecting_jobs + 1):       # number of jobs that can be executed in "parallel" 
            if self.debug:
                print(f"\nTrying batch size {num_jobs_to_execute} for job {job_index}")
                
            machine_type = None
            for mtype in range(0, self.num_machines):   
                cost, capacity = self.machines[mtype]  
                if capacity >= num_jobs_to_execute:
                    machine_type = mtype
                    break
            
            if machine_type is None:
                if self.debug:
                    print(f"No machine can handle batch size {num_jobs_to_execute}")
                continue
            
            prev_cost = self.min_cost_to_schedule(job_index - num_jobs_to_execute)
            total_cost = prev_cost + self.machines[machine_type][0]
            
            if total_cost < self.min_cost_per_job[job_index]:
                self.min_cost_per_job[job_index] = total_cost
                self.batch_choice[job_index] = (num_jobs_to_execute, machine_type)
                
            if self.debug:
                print(f"Machine type {machine_type}, cost updated to {self.min_cost_per_job[job_index]}")

            # self.min_cost_per_job[job_index] = min(self.min_cost_per_job[job_index], self.min_cost_to_schedule(job_index - num_jobs_to_execute) + self.machines[type][0])
            
        return self.min_cost_per_job[job_index]
    
    def print_batch_schedule(self):
        print("\n-------OUTPUT DATA-------")
        print("Batch Schedule (jobs are 1-indexed):")
        schedule = []
        job_index = self.num_jobs

        while job_index > 0:
            batch_info = self.batch_choice[job_index]
            if not batch_info:
                raise ValueError(f"No batch choice recorded for job {job_index}")
            num_jobs_in_batch, machine_type = batch_info
            batch_start = job_index - num_jobs_in_batch + 1
            job_range = list(range(batch_start, job_index + 1))

            # Get the time interval for this batch
            release_times = [self.jobs[i - 1][0] for i in job_range]
            earliest_start = max(release_times)

            schedule.append((job_range, machine_type, earliest_start))
            job_index -= num_jobs_in_batch

        schedule.reverse()
        num_batches = len(schedule)
        print(f"Number of batches: {num_batches}")
        for i, (job_range, machine_type, time) in enumerate(schedule, 1):
            jobs_str = ' '.join(str(j) for j in job_range)
            print(f"Time {time}: Jobs [{jobs_str}] on Machine Type {machine_type}")
            
        output_path = f"{self.file_path.replace(".txt", "")}_output.txt"
        with open(output_path, 'w') as file:
            file.write(f"{num_batches}\n")
            for i, (job_range, machine_type, start) in enumerate(schedule, 1):
                jobs_str = ' '.join(str(j) for j in job_range)
                file.write(f"{start} {machine_type} {jobs_str}\n")

def parse_args():
    parser = argparse.ArgumentParser(description="Schedule jobs on machines")
    parser.add_argument('--input', type=str, required=True, help='Path to the input file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()
   
def main():
    args = parse_args()
    file_path = f"testing/{args.input}"
    debug = args.debug
    job_scheduler = JobScheduling(file_path, debug)
    job_scheduler.parse_input()
    min_cost_to_schedule_jobs = job_scheduler.schedule_jobs()
    print(f"\nMINIMUM COST to schedule all jobs: {min_cost_to_schedule_jobs}")
    job_scheduler.print_batch_schedule()
    
    
if __name__ == "__main__":
    main() 
