from queue import Queue
from threading import Thread, Event, Semaphore
import time
import os
import json

class ThreadPool:
    def __init__(self):
        # You must implement a ThreadPool of TaskRunners
        # Your ThreadPool should check if an environment variable TP_NUM_OF_THREADS is defined
        # If the env var is defined, that is the number of threads to be used by the thread pool
        # Otherwise, you are to use what the hardware concurrency allows
        # You are free to write your implementation as you see fit, but
        # You must NOT:
        #   * create more threads than the hardware concurrency allows
        #   * recreate threads for each task
        if 'TP_NUM_OF_THREADS' in os.environ:
            self.num_threads = os.environ.get('TP_NUM_OF_THREADS')
        else:
            self.num_threads = os.cpu_count()
        
        self.task_queue = Queue()
        self.task_queue_semaphore = Semaphore(0)
        self.done_jobs = set()
        self.graceful_shutdown = False

    def start(self):
        for _ in range(self.num_threads):
            thread = TaskRunner(self)
            thread.start()

class TaskRunner(Thread):
    def __init__(self, thread_pool: ThreadPool):
        # TODO: init necessary data structures
        Thread.__init__(self)
        self.thread_pool = thread_pool

    def get_job(self):
        self.thread_pool.task_queue_semaphore.acquire()
        return self.thread_pool.task_queue.get()
    
    def mark_job_done(self, job_id):
        self.thread_pool.done_jobs.add(job_id)

    def run(self):
        while True:
            # TODO
            # Get pending job
            # Execute the job and save the result to disk
            # Repeat until graceful_shutdown

            # Wait for a job to be available
            (job_id, request_json, work) = self.get_job()

            # Shutdown called
            if job_id is None:
                break

            # Execute the job
            result = work(request_json)

            # Save the result to disk
            with open(f"job_{job_id}.json", "w") as f:
                f.write(json.dumps(result))

            # Mark the job as done
            self.mark_job_done(job_id)
