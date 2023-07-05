# flask2dock2kube
Testjes om te kijken hoe je een flask applicatie kan laten draaien op een kubernetes cluster

docker hub https://hub.docker.com/repository/docker/lister1308/python-hello-app/general

Hoe ga je nu van een flask applicatie naar deze werkend te krijgen op een kubernetes omgeving? Diverse links gevonden die hier iets over zeggen. Hieronder aantal links gevolgd om een test applicatie werkend te krijgen.
Link:

* https://docs.oracle.com/en-us/iaas/developer-tutorials/tutorials/flask-cloud-shell/01oci-flask-shell-summary.htm
* https://www.bhavaniravi.com/devops/kubernetes-101-deploy-apps-in-kubernetes
<h2>De stappen</h2>
De volgende stappen gevolgd om eerst een flask python applicatie te maken en deze vervolgens via docker te deployen op een kubernetes cluster

<h3>Flask applicatie</h3>
Aanmaken van een simpele flask applicatie
<pre>
from flask import Flask
import platform

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Hello NEW World from Flask running on ' + platform.node() + '</h1>'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("12345"), debug=True)

$ vi run.sh

export FLASK_APP=hello.py
export FLASK_ENV=development
python3 hello.py

$ run.sh
</pre><br>
Je kan daarna testen door naar poort 12345 te connecten met je webbrowser of middels curl en dan krijg je de tekst "Hello World from Flask!" te zien. Hierna gaan we dit omzetten naar een docker image

<h3>Docker image</h3>
In de directory waar de applicatie staat maak je een file genaamd
<pre>Dockerfile</pre>
aan met als inhoud
<pre>
FROM python:3.9-slim-buster
ADD hello.py /
COPY . /app
WORKDIR /app
RUN pip3 install Flask
EXPOSE 12345
CMD [ "python3", "./hello.py" ]
</pre><br>
Bouw daarna het docker image met
<pre>
$ docker build -t python-hello-app .
</pre><br>
Als het image gebouwd is, moet je deze met onderstaand commando ook zien staan
<pre>
$ docker images

REPOSITORY                    TAG       IMAGE ID       CREATED          SIZE
python-hello-app              latest    49f8c76140a3   57 minutes ago   128MB
</pre>
Draai het image daarna met
<pre>
docker run --rm -p 12345:12345 python-hello-app:latest &
</pre>
Ook nu moet je, door naar de browser te gaan of curl te gebruiken, de applicatie weer hebben draaien.

<h3>Docker repository</h3>
Maak op https://hub.docker.com een repository aan waar je dit image in wilt bewaren. Daarna voer de volgende commando's uit om je image te pushen naar deze repository
<pre>
$ docker tag python-hello-app:latest lister1308/python-hello-app:0.0.1
$ docker push lister1308/python-hello-app:0.0.1
</pre>
Hierna is in je docker hub het image zichtbaar

<h3>Kubernetes uitrol</h3>
Hierna kan je je docker image uitrollen in een kubernetes cluster. Hiervoor is onderstaande config python-hello-app.yaml aangemaakt
<pre>
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-app
spec:
  selector:
    matchLabels:
      app: hello-app
  replicas: 2
  template:
    metadata:
      labels:
        app: hello-app
    spec:
      containers:
      - name: hello-app
        image: lister1308/python-hello-app:latest
        imagePullPolicy: Always
        ports:
        - name: hello-app
          containerPort: 12345
          protocol: TCP
---
apiVersion: v1
kind: Service
metadata:
  name: hello-app-lb
  labels:
    app: hello-app
  annotations:
    service.beta.kubernetes.io/oci-load-balancer-shape: "flexible"
    service.beta.kubernetes.io/oci-load-balancer-shape-flex-min: "10"
    service.beta.kubernetes.io/oci-load-balancer-shape-flex-max: "100"
spec:
  type: LoadBalancer
  loadBalancerIP: 192.168.10.244
  ports:
  - port: 12345
  selector:
    app: hello-app
</pre>
Deply daarna dit op je cluster met
<pre>
$ kubectl create -f python-hello-app.yaml
</pre>
Als deze draait, zie je dit met
<pre>
$ kubectl get all -o wide

NAME                             READY   STATUS    RESTARTS   AGE   IP           NODE    NOMINATED NODE   READINESS GATES
pod/hello-app-85d64585f9-hx774   1/1     Running   0          48m   10.xxxxxxx   spock   <none>           <none>
pod/hello-app-85d64585f9-w2fvw   1/1     Running   0          48m   10.xxxxxxx   kirk    <none>           <none>
pod/nginx-95f4c5857-f7g8n        1/1     Running   3          48d   10.xxxxxxx   kirk    <none>           <none>
pod/nginx-95f4c5857-qpmf7        1/1     Running   3          48d   10.xxxxxxx   spock   <none>           <none>

NAME                    TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)           AGE   SELECTOR
service/hello-app-lb    LoadBalancer   10.xxxxxxxxxxx   <pending>     12345:32078/TCP   48m   app=hello-app
service/kubernetes      ClusterIP      10.xxxxxxx       <none>        443/TCP           98d   <none>
service/nginx-service   NodePort       10.xxxxxxxxx     <none>        80:30800/TCP      48d   app=nginx

NAME                        READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                              SELECTOR
deployment.apps/hello-app   2/2     2            2           48m   hello-app    lister1308/python-hello-app:0.0.1   app=hello-app
deployment.apps/nginx       2/2     2            2           48d   nginx        nginx:latest                        app=nginx

NAME                                   DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES                              SELECTOR
replicaset.apps/hello-app-85d64585f9   2         2         2       48m   hello-app    lister1308/python-hello-app:0.0.1   app=hello-app,pod-template-hash=85d64585f9
replicaset.apps/nginx-95f4c5857        2         2         2       48d   nginx        nginx:latest                        app=nginx,pod-template-hash=95f4c5857
</pre>
