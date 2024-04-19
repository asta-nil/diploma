kubectl create namespace doppler-operator-system
kubectl create namespace app 
kubectl create namespace db
kubectl create namespace monitoring

docker build app_docker/.
docker push .

kustomize build kubernetes/. > kuber.yaml
kubectl apply -f kuber.yaml

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring --values kubernetes/monitoring/prometheus-grafana/values.yaml

helm upgrade --install loki grafana/loki -n monitoring --values kubernetes/monitoring/loki/values-loki.yaml
helm upgrade --install promtail grafana/promtail -n monitoring --values kubernetes/monitoring/loki/values-promtail.yaml