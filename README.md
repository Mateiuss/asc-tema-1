#### Nume: DUDU Matei-Ioan
#### Grupă: 333CB

# Tema1

## Organizare

In threadpool am decis sa tin urmatoarele campuri:

```python
self.logger = logger # referinta la logger
self.task_queue = Queue() # o coada pentru task-uri
self.task_queue_semaphore = Semaphore(0) # semafor pentru thread-uri ca sa astepte accesul in coada
self.done_jobs = set() # multimea nodurilor terminate
self.graceful_shutdown = False # variabila prin care se verifica daca a fost cerut graceful_shutdown
self.threads = [] # lista cu thread-urile care merg
```

Dupa cum se poate observa si in variabilele folosite, folosesc o coada pentru task-uri dupa care se asteapta prin intermediul unui semafor.

Pentru a stabili faptul ca threadpool-ul trebuie inchis, ma folosesc de variabila graceful_shutdown sa imi semnaleze acest lucru; cand graceful_shutdown este apelat, threadpool-ul adauga in coada atatea job-uri nule cate thread-uri sunt pentru a le semnala faptul ca trebuie sa isi incheie activitatea. De asemenea, mai si asteapta dupa thread-uri.

```python
# in threadpool

for _ in range(self.num_threads):
  self.task_queue.put((None, None, None))
  self.task_queue_semaphore.release()

self.logger.info("Waiting for threads to finish")
for thread in self.threads:
  thread.join()
```

```python
# in thread

# Wait for a job to be available
(job_id, request_json, work) = self.get_job()

# Shutdown called
if job_id is None:
  self.thread_pool.logger.info("Shutting down thread")
  break
```

Prelucrarea efectiva a datelor se intampla in DataIngestor.

Tema mi se pare utila pentru a te invata sa lucrezi cu thread-uri/sincronizare in python si pentru a invata sa lucrezi cu un api. Consider ca m-a ajutat sa gandesc mai bine organizarea task-urilor prin modelul cerut la tema.

Implementarea mi se pare eficienta. Thread-urile sunt folosite la maximum (imediat ce primesc un job), verificarea faptului ca un job a fost terminat se face repede pentru ca ma folosesc de un set pentru a face asta.

Pentru job_counter am folosit un lock care sa blocheze accesarea concomitenta a variabilei de catre mai multe thread-uri ale rutelor. Se poate observa aceasta implementare in urmatorul exemplu din state_mean_by_category:

```python
# lock pe job_counter
webserver.job_lock.acquire()

# adaugare job in queue
webserver.tasks_runner.task_queue.put((
  webserver.job_counter,
  request.get_json(),
  lambda request_json: webserver.data_ingestor.state_mean_by_category(request_json)))

# anuntare semafor ca s-a adaugat un job nou
webserver.tasks_runner.task_queue_semaphore.release()

# generarea raspunsului
response = {"job_id": webserver.job_counter}

webserver.job_counter += 1

# eliberarea lock-ului
webserver.job_lock.release()
```

## Implementare

Intregul enunt al temei a fost implementat.

Am invatat sa ma obisnuiesc destul de repede cu un framework si sa incerc sa gasesc pe cat de repede se poate solutii la problemele pe care le pot intampina. De exemplu, atunci cand scriam unittests pentru testarea functionalitatilor temei am observat ca acesta nu termina de rulat, asta fiindca atunci cand importam 'app' fisierul __init__.py era rulat si imi deschidea si task_runner-ul. Am evitat acest scenariu prin testarea functionalitatii graceful_shutdown, unde inchidea threadpool-ul si thread-urile asociate acestuia.

## Resurse utilizate

* https://flask.palletsprojects.com/en/3.0.x/
* https://stackoverflow.com/questions/67528668/flask-what-is-the-use-of-init-py-vs-run-py-and-are-blueprints-standard-thi
* https://flask.palletsprojects.com/en/3.0.x/reqcontext/
* https://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure

## Git

* [Link](https://github.com/Mateiuss/asc-tema-1) către repo-ul de git