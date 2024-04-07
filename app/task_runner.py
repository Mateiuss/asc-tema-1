"""
This is the module for the ThreadPool and TaskRunner classes.
"""

from queue import Queue
from threading import Thread, Semaphore
import os
import json

class ThreadPool:
    """
    This is the threadpool class that will be used to manage the threads.
    """
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

    def start(self):
        """
        Function that runs the threads.
        """
        self.logger.info("Starting ThreadPool")
        for _ in range(self.num_threads):
            thread = TaskRunner(self)
            self.threads.append(thread)
            thread.start()

    def is_shutdown(self):
        """
        Function that returns whether the ThreadPool is closed or not.
        """
        return self.graceful_shutdown

    def close(self):
        """
        Function that closes the ThreadPool and waits for the threads to finish.
        """
        self.logger.info("Closing ThreadPool")

        if self.graceful_shutdown:
            self.logger.info("ThreadPool already closed")
            return

        self.graceful_shutdown = True

        for _ in range(self.num_threads):
            self.task_queue.put((None, None, None))
            self.task_queue_semaphore.release()

        self.logger.info("Waiting for threads to finish")
        for thread in self.threads:
            thread.join()

def key_to_string(data: dict) -> dict:
    """
    Function that turns all keys in a dictionary to strings.
    """
    ans = {}

    for (k, v) in data.items():
        if isinstance(v, dict):
            ans[str(k)] = key_to_string(v)
        else:
            ans[str(k)] = v

    return ans

class TaskRunner(Thread):
    """
    This is the TaskRunner class that will be used to run the tasks.
    """
    def __init__(self, thread_pool: ThreadPool):
        Thread.__init__(self)
        self.thread_pool = thread_pool

    def get_job(self):
        """
        Function that gets a job from the ThreadPool.
        """
        self.thread_pool.task_queue_semaphore.acquire()
        return self.thread_pool.task_queue.get()

    def mark_job_done(self, job_id):
        """
        Function that marks a job as done in the ThreadPool.
        """
        self.thread_pool.done_jobs.add(job_id)

    def run(self):
        """
        Function that runs the TaskRunner.
        """
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
            with open(f"results/job_{job_id}.json", "w", encoding='utf-8') as f:
                f.write(json.dumps(result))

            # Mark the job as done
            self.mark_job_done(job_id)
