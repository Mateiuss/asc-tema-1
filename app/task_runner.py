from queue import Queue
from threading import Thread, Lock, Semaphore
import os
import json

class ThreadPool:
    def __init__(self, logger):
        if 'TP_NUM_OF_THREADS' in os.environ:
            self.num_threads = os.environ.get('TP_NUM_OF_THREADS')
        else:
            self.num_threads = os.cpu_count()

        self.logger = logger
        self.task_queue = Queue()
        self.task_queue_semaphore = Semaphore(0)
        self.done_jobs = set()
        self.graceful_shutdown = False
        self.threads = []
        self.lock = Lock()

    def start(self):
        self.logger.info("Starting ThreadPool")
        for _ in range(self.num_threads):
            thread = TaskRunner(self)
            self.threads.append(thread)
            thread.start()

    def is_shutdown(self):
        self.lock.acquire()
        ans = self.graceful_shutdown
        self.lock.release()
        return ans

    def close(self):
        self.logger.info("Closing ThreadPool")
        self.lock.acquire()
        if self.graceful_shutdown:
            self.lock.release()
            self.logger.info("ThreadPool already closed")
            return

        self.graceful_shutdown = True
        self.lock.release()

        for _ in range(self.num_threads):
            self.task_queue.put((None, None, None))
            self.task_queue_semaphore.release()

        self.logger.info("Waiting for threads to finish")
        for thread in self.threads:
            thread.join()

def key_to_string(data: dict) -> dict:
        ans = {}

        for (k, v) in data.items():
            if isinstance(v, dict):
                ans[str(k)] = key_to_string(v)
            else:
                ans[str(k)] = v

        return ans

class TaskRunner(Thread):
    def __init__(self, thread_pool: ThreadPool):
        Thread.__init__(self)
        self.thread_pool = thread_pool

    def get_job(self):
        self.thread_pool.task_queue_semaphore.acquire()
        return self.thread_pool.task_queue.get()
    
    def mark_job_done(self, job_id):
        self.thread_pool.done_jobs.add(job_id)

    def run(self):
        while True:
            # Wait for a job to be available
            (job_id, request_json, work) = self.get_job()

            # Shutdown called
            if job_id is None:
                self.thread_pool.logger.info("Shutting down thread")
                break

            # Execute the job and turn keys into strings
            result = work(request_json)
            self.thread_pool.logger.info(f"TaskRunner {job_id} done")
            result = key_to_string(result)

            # Save the result to disk
            with open(f"results/job_{job_id}.json", "w") as f:
                f.write(json.dumps(result))

            # Mark the job as done
            self.mark_job_done(job_id)
