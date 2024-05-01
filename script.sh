minikube start --driver=docker  --kubernetes-version=1.26.0 --container-runtime=containerd

kubectl create namespace doppler-operator-system
kubectl create namespace app 
kubectl create namespace db
kubectl create namespace monitoring
kubectl create namespace nginx

docker build app_docker/. --tag flask
docker tag flask:latest astanil/flask:latest 
docker push astanil/flask:latest

kubectl apply -k kubernetes/.
kubectl apply -k kubernetes/.

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm upgrade --install prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring --values kubernetes/monitoring/prometheus-grafana/values.yaml
helm upgrade --install loki grafana/loki -n monitoring --values kubernetes/monitoring/loki/values-loki.yaml
helm upgrade --install promtail grafana/promtail -n monitoring --values kubernetes/monitoring/loki/values-promtail.yaml
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx -n nginx --values kubernetes/nginx/conteroller/values.yaml

minikube tunnel