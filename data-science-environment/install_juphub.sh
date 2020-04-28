#!/bin/sh

kubectl --namespace kube-system create serviceaccount tiller
helm init --service-account tiller --history-max 100 --wait
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'

helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update

RELEASE=jhub
NAMESPACE=jhub
helm upgrade --install $RELEASE jupyterhub/jupyterhub --namespace $NAMESPACE --version=0.8.2 --values $1


echo "Installation of Jupyterhub has been done!!!!!!!"
echo "***********************************************"
echo "Please use proxy-public EXTERNAL-IP from the following list:"
kubectl get service --namespace jhub

echo ""
echo ""
echo "If proxy-public EXTERNAL-IP is pending please run 'kubectl get service --namespace jhub' to get the EXTERNAL-IP after few mins."

