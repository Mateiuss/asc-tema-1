"""
This file contains the definition of the endpoints for the webserver.
"""

import json
from flask import request, jsonify
from app import webserver

LOGGER = webserver.logger

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    """
    This function is called when the user wants to get the results of a job.
    """
    LOGGER.info('Received GET request for job_id %s', job_id)
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    with webserver.job_lock:
        if webserver.job_counter < int(job_id):
            return jsonify({'status': 'error', 'reason': 'Invalid job_id'})

        if int(job_id) in webserver.tasks_runner.done_jobs:
            with open(f"results/job_{job_id}.json", "r", encoding="utf-8") as f:
                res = json.load(f)
                return jsonify({
                    'status': 'done',
                    'data': res
                })

        return jsonify({'status': 'running'})

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    """
    This function is called when the user wants to get the mean of all states.
    """
    LOGGER.info("Received POST request for states_mean")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    with webserver.job_lock:
        webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                            request.get_json(),
                                            webserver.data_ingestor.states_mean))
        webserver.tasks_runner.task_queue_semaphore.release()

        response = {"job_id": webserver.job_counter}
        webserver.job_counter += 1

        return jsonify(response)

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    """
    This function is called when the user wants to get the mean of a state
    """
    LOGGER.info("Received POST request for state_mean")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    with webserver.job_lock:
        webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                            request.get_json(),
                                            webserver.data_ingestor.state_mean))
        webserver.tasks_runner.task_queue_semaphore.release()

        response = {"job_id": webserver.job_counter}
        webserver.job_counter += 1

        return jsonify(response)

@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    """
    This function is called when the user wants to get the best 5 states by mean.
    """
    LOGGER.info("Received POST request for best5")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    with webserver.job_lock:
        webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                                request.get_json(),
                                                webserver.data_ingestor.best5))
        webserver.tasks_runner.task_queue_semaphore.release()

        response = {"job_id": webserver.job_counter}
        webserver.job_counter += 1

        return jsonify(response)

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    """
    This function is called when the user wants to get the worst 5 states by mean.
    """
    LOGGER.info("Received POST request for worst5")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    with webserver.job_lock:
        webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                            request.get_json(),
                                            webserver.data_ingestor.worst5))
        webserver.tasks_runner.task_queue_semaphore.release()

        response = {"job_id": webserver.job_counter}
        webserver.job_counter += 1

        return jsonify(response)

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    """
    This function is called when the user wants to get the global mean.
    """
    LOGGER.info("Received POST request for global_mean")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    with webserver.job_lock:
        webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                            request.get_json(),
                                            webserver.data_ingestor.global_mean))
        webserver.tasks_runner.task_queue_semaphore.release()

        response = {"job_id": webserver.job_counter}
        webserver.job_counter += 1

        return jsonify(response)

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    """
    This function is called when the user wants to get the difference from
    the global mean of all states.
    """
    LOGGER.info("Received POST request for diff_from_mean")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    with webserver.job_lock:
        webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                        request.get_json(),
                                        webserver.data_ingestor.diff_from_mean))
        webserver.tasks_runner.task_queue_semaphore.release()

        response = {"job_id": webserver.job_counter}
        webserver.job_counter += 1

        return jsonify(response)

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    """
    This function is called when the user wants to get the difference from
    the global mean of a state.
    """
    LOGGER.info("Received POST request for state_diff_from_mean")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    with webserver.job_lock:
        webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                    request.get_json(),
                                    webserver.data_ingestor.state_diff_from_mean))
        webserver.tasks_runner.task_queue_semaphore.release()

        response = {"job_id": webserver.job_counter}
        webserver.job_counter += 1

        return jsonify(response)

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    """
    This function is called when the user wants to get the mean of each state
    by every category.
    """
    LOGGER.info("Received POST request for mean_by_category")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    with webserver.job_lock:
        webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                        request.get_json(),
                                        webserver.data_ingestor.mean_by_category))
        webserver.tasks_runner.task_queue_semaphore.release()

        response = {"job_id": webserver.job_counter}
        webserver.job_counter += 1

        return jsonify(response)

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    """
    This function is called when the user wants to get the mean of a given state
    by every category.
    """
    LOGGER.info("Received POST request for state_mean_by_category")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    with webserver.job_lock:
        webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                request.get_json(),
                                webserver.data_ingestor.state_mean_by_category))
        webserver.tasks_runner.task_queue_semaphore.release()

        response = {"job_id": webserver.job_counter}
        webserver.job_counter += 1

        return jsonify(response)

# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    """
    This is the index route for the webserver.
    """
    LOGGER.info("Received GET request for index")
    routes = get_defined_routes()
    msg = "Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    paragraphs = '\n'.join([f"<p>{route}</p>" for route in routes])

    msg += paragraphs
    return msg

@webserver.route('/api/graceful_shutdown', methods=['POST'])
def graceful_shutdown():
    """
    This function is called when the user wants to shutdown the thread pool.
    """
    LOGGER.info("Received POST request for graceful_shutdown")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    webserver.tasks_runner.close()

    return jsonify({"status": "shutdown"})

@webserver.route('/api/jobs', methods=['GET'])
def get_jobs():
    """
    This function is called when the user wants to get the status of the jobs.
    """
    LOGGER.info("Received GET request for jobs")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    ans = {}
    ans['status'] = 'done'
    ans['data'] = []

    with webserver.job_lock:
        for i in range(webserver.job_counter):
            if i in webserver.tasks_runner.done_jobs:
                ans['data'].append({f'job_id_{i}': 'done'})
            else:
                ans['data'].append({f'job_id_{i}': 'running'})

        return jsonify(ans)

@webserver.route('/api/num_jobs', methods=['GET'])
def get_num_jobs():
    """
    This function is called when the user wants to get the number of jobs
    in the queue.
    """
    LOGGER.info("Received GET request for num_jobs")
    if webserver.tasks_runner.is_shutdown():
        return jsonify({"status": "shutdown"})

    return jsonify({"num_jobs": webserver.tasks_runner.task_queue.qsize()})

def get_defined_routes():
    """
    This function returns all the defined routes in the webserver.
    """
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
