from app import webserver
from flask import request, jsonify
from logging import info

import os
import json

# Example endpoint definition
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json
        print(f"got data in post {data}")

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)
    else:
        # Method Not Allowed
        return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    print(f"JobID is {job_id}")
    # TODO
    # Check if job_id is valid
    if webserver.job_counter < int(job_id):
        return jsonify({'status': 'error', 'reason': 'Invalid job_id'})

    # Check if job_id is done and return the result
    #    res = res_for(job_id)
    #    return jsonify({
    #        'status': 'done',
    #        'data': res
    #    })

    if int(job_id) in webserver.tasks_runner.done_jobs:
        with open(f"job_{job_id}.json", "r") as f:
            res = json.load(f)
            return jsonify({
                'status': 'done',
                'data': res
            })

    # If not, return running status
    return jsonify({'status': 'running'})

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    if webserver.tasks_runner.graceful_shutdown:
        return jsonify({"status": "shutdown"})

    webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                           request.get_json(),
                                           lambda request_json: webserver.data_ingestor.states_mean(request_json)))
    webserver.tasks_runner.task_queue_semaphore.release()
    
    response = {"job_id": webserver.job_counter}
    webserver.job_counter += 1

    return jsonify(response)

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    if webserver.tasks_runner.graceful_shutdown:
        return jsonify({"status": "shutdown"})

    webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                            request.get_json(),
                                            lambda request_json: webserver.data_ingestor.state_mean(request_json)))
    webserver.tasks_runner.task_queue_semaphore.release()
    
    response = {"job_id": webserver.job_counter}
    webserver.job_counter += 1

    return jsonify(response)


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    if webserver.tasks_runner.graceful_shutdown:
        return jsonify({"status": "shutdown"})
    
    webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                            request.get_json(),
                                            lambda request_json: webserver.data_ingestor.best5(request_json)))
    webserver.tasks_runner.task_queue_semaphore.release()

    response = {"job_id": webserver.job_counter}
    webserver.job_counter += 1

    return jsonify(response)

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    if webserver.tasks_runner.graceful_shutdown:
        return jsonify({"status": "shutdown"})
    
    webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                           request.get_json(),
                                           lambda request_json: webserver.data_ingestor.worst5(request_json)))
    webserver.tasks_runner.task_queue_semaphore.release()

    response = {"job_id": webserver.job_counter}
    webserver.job_counter += 1

    return jsonify(response)

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    if webserver.tasks_runner.graceful_shutdown:
        return jsonify({"status": "shutdown"})
    
    webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                            request.get_json(),
                                            lambda request_json: webserver.data_ingestor.global_mean(request_json)))
    webserver.tasks_runner.task_queue_semaphore.release()

    response = {"job_id": webserver.job_counter}
    webserver.job_counter += 1

    return jsonify(response)

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    if webserver.tasks_runner.graceful_shutdown:
        return jsonify({"status": "shutdown"})
    
    webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                            request.get_json(),
                                            lambda request_json: webserver.data_ingestor.diff_from_mean(request_json)))
    webserver.tasks_runner.task_queue_semaphore.release()

    response = {"job_id": webserver.job_counter}
    webserver.job_counter += 1

    return jsonify(response)

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    if webserver.tasks_runner.graceful_shutdown:
        return jsonify({"status": "shutdown"})
    
    webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                             request.get_json(),
                                             lambda request_json: webserver.data_ingestor.state_diff_from_mean(request_json)))
    webserver.tasks_runner.task_queue_semaphore.release()

    response = {"job_id": webserver.job_counter}
    webserver.job_counter += 1

    return jsonify(response)

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    return jsonify({"status": "NotImplemented"})

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    if webserver.tasks_runner.graceful_shutdown:
        return jsonify({"status": "shutdown"})
    
    webserver.tasks_runner.task_queue.put((webserver.job_counter,
                                            request.get_json(),
                                            lambda request_json: webserver.data_ingestor.state_mean_by_category(request_json)))
    webserver.tasks_runner.task_queue_semaphore.release()

    response = {"job_id": webserver.job_counter}
    webserver.job_counter += 1

    return jsonify(response)

# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    routes = get_defined_routes()
    msg = f"Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg

@webserver.route('/api/graceful_shutdown', methods=['POST'])
def graceful_shutdown():
    webserver.thread_pool.graceful_shutdown = True

    for _ in range(webserver.thread_pool.num_threads):
        webserver.thread_pool.task_queue.put((None, None))
        webserver.thread_pool.task_queue_semaphore.release()

    return jsonify({"status": "success"})

def get_defined_routes():
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
