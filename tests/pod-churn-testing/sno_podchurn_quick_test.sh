#!/usr/bin/env bash
set -e
set -o pipefail

# 168 pods x 3 w/ 4 Containers
# 418 pods x 3 w/ 3 Containers
# Guaranteed pods 418 x 3
# configmaps/secrets 8 pods 418 x 3
# tcp probes (1s) 418 pods all probe types x 3
# http probes (1s) 418 pods all probe types x 3
# exec probes (10s) 418 pods, all probe types x 3
# Combined test 3m x 3

# node_250_pods=$1
# node_225_pods=$2
node_160_pods=2
node_225_pods=135

mkdir -p ../logs
mkdir -p ../results

version=$(oc version -o json | jq -r '.openshiftVersion')

sdn_pods=$(oc get po -n openshift-sdn --no-headers | wc -l)
network="ovn"
if [[ $sdn_pods -gt 0 ]]; then
  network="sdn"
fi

nodes=$(oc get no -l jetlag=true --no-headers | wc -l)

gohttp_env_vars="-e LISTEN_DELAY_SECONDS=0 LIVENESS_DELAY_SECONDS=0 READINESS_DELAY_SECONDS=0 RESPONSE_DELAY_MILLISECONDS=0 LIVENESS_SUCCESS_MAX=0 READINESS_SUCCESS_MAX=0"
measurement="-D 180"
metrics="--metrics nodeReadyStatus nodeCoresUsed nodeMemoryConsumed kubeletCoresUsed kubeletMemory crioCoresUsed crioMemory rxNetworkBytes txNetworkBytes nodeDiskWrittenBytes nodeDiskReadBytes nodeCPU"

sleep_period=120
iterations=1

total_160_pods=$((${nodes} * ${node_160_pods}))
total_225_pods=$((${nodes} * ${node_225_pods}))

# Debug/Test entire Run
# dryrun="--dry-run"
# measurement="--no-measurement-phase"
# sleep_period=1
# iterations=1

#tc_num=1
#test_index=0
#csv_suffix="${version}-${network}-sno${nodes}"
#csv_ts=$(date -u +%Y%m%d-%H%M%S)
#csvfile="--csv-results-file ../results/results-quick-${csv_suffix}-${csv_ts}.csv --csv-metrics-file ../results/metrics-quick-${csv_suffix}-${csv_ts}.csv"
#echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
#echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_160_pods} = ${total_160_pods}"
#echo "****************************************************************************************************************************************"
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_160_pods} namespaces, 1 deploy, 1 pod, 1 containers, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets, no resources set"
#  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
#  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_160_pods}n-1d-1p-1c-${iteration}" ${metrics} -n ${total_160_pods} -d 1 -p 1 -c 1 -l -r --no-probes ${gohttp_env_vars} ${INDEX_ARGS} &> ${logfile} --no-measurement-phase 
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#  sleep ${sleep_period}
#  echo "****************************************************************************************************************************************"
#done
#
#tc_num=2
#test_index=0
#csv_suffix="${version}-${network}-sno${nodes}"
#csv_ts=$(date -u +%Y%m%d-%H%M%S)
#csvfile="--csv-results-file ../results/results-quick-${csv_suffix}-${csv_ts}.csv --csv-metrics-file ../results/metrics-quick-${csv_suffix}-${csv_ts}.csv"
#echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
#echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_160_pods} = ${total_160_pods}"
#echo "****************************************************************************************************************************************"
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_160_pods} namespaces, 1 deploy, 1 pod, 2 containers, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets, no resources set"
#  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
#  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_160_pods}n-1d-1p-2c-${iteration}" ${metrics} -n ${total_160_pods} -d 1 -p 1 -c 2 -l -r --no-probes ${gohttp_env_vars} ${INDEX_ARGS} &> ${logfile} --no-measurement-phase 
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#  sleep ${sleep_period}
#  echo "****************************************************************************************************************************************"
#done
#
#tc_num=3
#test_index=0
#csv_suffix="${version}-${network}-sno${nodes}"
#csv_ts=$(date -u +%Y%m%d-%H%M%S)
#csvfile="--csv-results-file ../results/results-quick-${csv_suffix}-${csv_ts}.csv --csv-metrics-file ../results/metrics-quick-${csv_suffix}-${csv_ts}.csv"
#echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
#echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_160_pods} = ${total_160_pods}"
#echo "****************************************************************************************************************************************"
#for iteration in `seq 1 ${iterations}`; do
  test_index=$((${test_index} + 1))
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_160_pods} namespaces, 1 deploy, 1 pod, 2 containers, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets, no resources set"
#  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
#  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_160_pods}n-1d-1p-2c-${iteration}" ${metrics} -n ${total_160_pods} -d 1 -p 1 -c 2 -l -r --no-probes ${gohttp_env_vars} ${INDEX_ARGS} &> ${logfile} --no-measurement-phase --enable-pod-annotations -a cpu-load-balancing.crio.io: true cpu-quota.crio.io: disable(only for guaranteed pods)  irq-load-balancing.crio.io: disable runtimeClassName: performance-sno-perfprofile
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#  sleep ${sleep_period}
#  echo "****************************************************************************************************************************************"
#done
#
#tc_num=4
#test_index=0
#echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
#echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_160_pods} = ${total_160_pods}"
#echo "****************************************************************************************************************************************"
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  probes=" --startup-probe http,0,1,1,12 --liveness-probe http,0,1,1,3 --readiness-probe http,0,1,1,3,1 "
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_160_pods} namespaces, 1 deploy, 1 pod, 2 containers, gohttp image, 1 service, 1 route, ${probes}, 8 configmaps, 8 secrets, no resources set"
#  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
#  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_160_pods}n-1d-1p-3c-${iteration}" ${metrics} -n ${total_160_pods} -d 1 -p 1 -c 2 -l -r ${probes} ${gohttp_env_vars} ${INDEX_ARGS} &> ${logfile} --no-measurement-phase 
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#  sleep ${sleep_period}
#  echo "****************************************************************************************************************************************"
#done
#

#tc_num=5
#test_index=0
#echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
#echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_160_pods} = ${total_160_pods}"
#echo "****************************************************************************************************************************************"
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  probes=" --startup-probe http,0,1,1,12 --liveness-probe http,0,1,1,3 --readiness-probe http,0,1,1,3,1 "
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_160_pods} namespaces, 1 deploy, 1 pod, 2 containers, gohttp image, 1 service, 1 route, ${probes}, 8 configmaps, 8 secrets, guaranteed resources"
#  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
#  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_160_pods}n-1d-1p-3c-${iteration}" ${metrics} -n ${total_160_pods} -d 1 -p 1 -c 2 -l -r ${probes} ${gohttp_env_vars} ${resources} ${INDEX_ARGS} &> ${logfile} --no-measurement-phase --enable-pod-annotations -a ("cpu-load-balancing.crio.io: true" "irq-load-balancing.crio.io: disable")
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#  sleep ${sleep_period}
#  echo "****************************************************************************************************************************************"
#done

#tc_num=5
#test_index=0
#echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
#echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_160_pods} = ${total_160_pods}"
#echo "****************************************************************************************************************************************"
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  probes=" --startup-probe http,0,1,1,12 --liveness-probe http,0,1,1,3 --readiness-probe http,0,1,1,3,1 "
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_160_pods} namespaces, 1 deploy, 1 pod, 2 containers, gohttp image, 1 service, 1 route, ${probes}, 8 configmaps, 8 secrets, guaranteed resources"
#  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
#  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_160_pods}n-1d-1p-3c-${iteration}" ${metrics} -n ${total_160_pods} -d 1 -p 1 -c 2 -l -r ${probes} ${gohttp_env_vars} ${resources} ${INDEX_ARGS} &> ${logfile} --no-measurement-phase 
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#  sleep ${sleep_period}
#  echo "****************************************************************************************************************************************"
#done

tc_num=6
test_index=0
echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_225_pods} = ${total_225_pods}"
echo "****************************************************************************************************************************************"
for iteration in `seq 1 ${iterations}`; do
  test_index=$((${test_index} + 1))
  resources=" --cpu-requests 50 --memory-requests 100 --cpu-limits 50 --memory-limits 100 "
  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_225_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets, ${resources}"
  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_225_pods}n-1d-1p-1c-gu-${iteration}" ${metrics} -n ${total_225_pods} -d 1 -p 1 -c 1 -l -r --no-probes ${resources} ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile}
  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
  sleep ${sleep_period}
  echo "****************************************************************************************************************************************"
done

tc_num=7
test_index=0
echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_225_pods} = ${total_225_pods}"
echo "****************************************************************************************************************************************"
for iteration in `seq 1 ${iterations}`; do
  test_index=$((${test_index} + 1))
  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_225_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, no probes, 8 configmaps, 8 secrets, no resources set"
  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_225_pods}n-1d-1p-1c-8cm-8s-${iteration}" ${metrics} -n ${total_225_pods} -d 1 -p 1 -c 1 -l -r -m 8 --secrets 8 --no-probes ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile}
  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
  sleep ${sleep_period}
  echo "****************************************************************************************************************************************"
done

tc_num=8
test_index=0
echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_225_pods} = ${total_225_pods}"
echo "****************************************************************************************************************************************"
for iteration in `seq 1 ${iterations}`; do
  test_index=$((${test_index} + 1))
  probes=" --startup-probe tcp,0,1,1,12 --liveness-probe tcp,0,1,1,3 --readiness-probe tcp,0,1,1,3,1 "
  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_225_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, ${probes}, no configmaps, no secrets, no resources set"
  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_225_pods}n-1d-1p-1c-tcp-s1-l1-r1-${iteration}" ${metrics} -n ${total_225_pods} -d 1 -p 1 -c 1 -l -r ${probes} ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile}
  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
  sleep ${sleep_period}
  echo "****************************************************************************************************************************************"
done

tc_num=9
test_index=0
echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_225_pods} = ${total_225_pods}"
echo "****************************************************************************************************************************************"
for iteration in `seq 1 ${iterations}`; do
  test_index=$((${test_index} + 1))
  probes=" --startup-probe http,0,1,1,12 --liveness-probe http,0,1,1,3 --readiness-probe http,0,1,1,3,1 "
  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_225_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, ${probes}, no configmaps, no secrets, no resources set"
  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_225_pods}n-1d-1p-1c-http-s1-l1-r1-${iteration}" ${metrics} -n ${total_225_pods} -d 1 -p 1 -c 1 -l -r ${probes} ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile}
  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
  sleep ${sleep_period}
  echo "****************************************************************************************************************************************"
done

#tc_num=10
#test_index=0
#echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
#echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_225_pods} = ${total_225_pods}"
#echo "****************************************************************************************************************************************"
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  probes="--startup-probe exec,0,10,1,12 --liveness-probe exec,0,10,1,3 --readiness-probe exec,0,10,1,3,1"
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_225_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, ${probes}, no configmaps, no secrets, no resources set"
#  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
#  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_225_pods}n-1d-1p-1c-exec-s10-l10-r10-${iteration}" ${metrics} -n ${total_225_pods} -d 1 -p 1 -c 1 -l -r ${probes} ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile}
#  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#  sleep ${sleep_period}
#  echo "****************************************************************************************************************************************"
#done

tc_num=11
test_index=0
echo "$(date -u +%Y%m%d-%H%M%S) - SNO Quick Pod Churn Test ${tc_num} Start"
echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_225_pods} = ${total_225_pods}"
echo "****************************************************************************************************************************************"
for iteration in `seq 1 ${iterations}`; do
  test_index=$((${test_index} + 1))
  configmaps_secrets=" -m 8 --secrets 8 "
  probes=" --startup-probe http,0,1,1,12 --liveness-probe http,0,1,1,3 --readiness-probe http,0,1,1,3,1 "
  resources=" --cpu-requests 50 --memory-requests 100 --cpu-limits 50 --memory-limits 100 "
  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_225_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, http probes, 8 configmaps, 8 secrets, guaranteed resources"
  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-podchurn-${tc_num}.${test_index}.log"
  ../../boatload/boatload-churn.py ${dryrun} ${csvfile} --csv-title "${total_225_pods}n-1d-1p-1c-${iteration}" ${metrics} -n ${total_225_pods} -d 1 -p 1 -c 1 -l -r ${configmaps_secrets} ${probes} ${resources} ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile}
  echo "$(date -u +%Y%m%d-%H%M%S) - pod churn ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
  sleep ${sleep_period}
  echo "****************************************************************************************************************************************"
done
