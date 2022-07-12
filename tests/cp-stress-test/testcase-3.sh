#!/usr/bin/env bash
# Node Density Enhanced Testing for SNO
# Test Case 3 - Validate Max-pods with different resource configurations
set -e
set -o pipefail

csv_suffix=$1

nodes=$(oc get no -l jetlag=true --no-headers | wc -l)
node_pods=$2
total_pods=$((${nodes} * ${node_pods}))

mkdir -p ../logs
mkdir -p ../results
sleep_period=120
iterations=3
tc_num=3

gohttp_env_vars="-e LISTEN_DELAY_SECONDS=0 LIVENESS_DELAY_SECONDS=0 READINESS_DELAY_SECONDS=0 RESPONSE_DELAY_MILLISECONDS=0 LIVENESS_SUCCESS_MAX=0 READINESS_SUCCESS_MAX=0"
measurement="-D 180"
csv_ts=$(date -u +%Y%m%d-%H%M%S)
csvfile="--csv-results-file ../results/results-tc${tc_num}-${csv_suffix}-${csv_ts}.csv --csv-metrics-file ../results/metrics-tc${tc_num}-${csv_suffix}-${csv_ts}.csv"

# Debug/Test entire Run
# dryrun="--dry-run"
# measurement="--no-measurement-phase"
# sleep_period=1
# iterations=1

echo "$(date -u +%Y%m%d-%H%M%S) - Test Case ${tc_num} Start"
echo "$(date -u +%Y%m%d-%H%M%S) - Total Pod Count (Nodes * pods/node) :: ${nodes} * ${node_pods} = ${total_pods}"
echo "****************************************************************************************************************************************"
test_index=0

# Best-effort pods
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets, no resources set"
#  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-nodedensity-${tc_num}.${test_index}.log"
#  ../../boatload/boatload.py ${dryrun} ${csvfile} --csv-title "${total_pods}n-1d-1p-1c-be-${iteration}" -n ${total_pods} -d 1 -p 1 -c 1 -l -r --no-probes ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile}
#  echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#  sleep ${sleep_period}
#  echo "****************************************************************************************************************************************"
#done

# Burstable pods
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  resources=" --cpu-requests 50 --memory-requests 100 "
#  echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets,${resources}"
#  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-nodedensity-${tc_num}.${test_index}.log"
#  ../../boatload/boatload.py ${dryrun} ${csvfile} --csv-title "${total_pods}n-1d-1p-1c-bu-${iteration}" -n ${total_pods} -d 1 -p 1 -c 1 -l -r --no-probes ${resources} ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile}
#  echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#  sleep ${sleep_period}
#  echo "****************************************************************************************************************************************"
#done

# Guaranteed pods
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  resources=" --cpu-requests 50 --memory-requests 100 --cpu-limits 50 --memory-limits 100 "
#  echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets, ${resources}"
#  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-nodedensity-${tc_num}.${test_index}.log"
#  ../../boatload/boatload.py ${dryrun} ${csvfile} --csv-title "${total_pods}n-1d-1p-1c-gu-${iteration}" -n ${total_pods} -d 1 -p 1 -c 1 -l -r --no-probes ${resources} ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile}
#  echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#  sleep ${sleep_period}
#  echo "****************************************************************************************************************************************"
#done

# Guaranteed pods with pod annotations
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  annotations=" cpu-load-balancing.crio.io=\''true'\' irq-load-balancing.crio.io=\''disable'\' cpu-quota.crio.io=\''disable'\' "
#  resources=" --cpu-requests 1 --memory-requests 100 --cpu-limits 1 --memory-limits 100 "
#  echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets, ${resources}"
#  logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-nodedensity-${tc_num}.${test_index}.log"
#  ../../boatload/boatload-cpu.py ${dryrun} ${csvfile} --csv-title "${total_pods}n-1d-1p-1c-1coregu-${iteration}" -n ${total_pods} -d 1 -p 1 -c 1 -l -r --no-probes ${resources} ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile} --enable-pod-annotations -a ${annotations}
#  echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#  sleep ${sleep_period}
#  echo "****************************************************************************************************************************************"
#done
#
# Guaranteed pods
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  resources=" --cpu-requests 50 --memory-requests 100 --cpu-limits 50 --memory-limits 100 "
#   echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets, ${resources}"
#   logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-nodedensity-${tc_num}.${test_index}.log"
#   ../../boatload/boatload.py ${dryrun} ${csvfile} --csv-title "${total_pods}n-1d-1p-1c-gu-${iteration}" -n ${total_pods} -d 1 -p 1 -c 1 -l -r --no-probes ${resources} ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile}
#   echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#   sleep ${sleep_period}
#   echo "****************************************************************************************************************************************"
#done

#echo "$(date -u +%Y%m%d-%H%M%S) - Test Case ${tc_num} Complete"

# Mixed workload
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  annotations=" cpu-load-balancing.crio.io=\''true'\' irq-load-balancing.crio.io=\''disable'\' cpu-quota.crio.io=\''disable'\' "
#  resources=" --cpu-requests 28 --memory-requests 100 --cpu-limits 28 --memory-limits 100 "
#   echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets, ${resources}"
#   logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-nodedensity-${tc_num}.${test_index}.log"
#   ../../boatload/boatload-cpu.py ${dryrun} ${csvfile} --csv-title "${total_pods}n-1d-1p-1c-coregu-${iteration}" -n 1 -d 1 -p 1 -c 1 -l -r --no-probes ${resources} ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile} --enable-pod-annotations -a ${annotations} --no-cleanup-phase
#   ../../boatload/boatload.py ${dryrun} ${csvfile} --csv-title "${total_pods}n-1d-1p-1c-bu-${iteration}" -n ${total_pods} -d 1 -p 1 -c 1 -l -r --no-probes --cpu-requests 50 --memory-requests 100 ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile}
#   echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#   sleep ${sleep_period}
#   echo "****************************************************************************************************************************************"
#done

# Mixed workload
for iteration in `seq 1 ${iterations}`; do
  test_index=$((${test_index} + 1))
  annotations=" cpu-load-balancing.crio.io=\''true'\' irq-load-balancing.crio.io=\''disable'\' cpu-quota.crio.io=\''disable'\' "
  resources=" --cpu-requests 50 --memory-requests 100 "
   echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets, ${resources}"
   logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-nodedensity-${tc_num}.${test_index}.log"
   source namespace-create.sh
   sleep 500
   ../../boatload/boatload-mixed-pv-test-2.py ${dryrun} ${csvfile} --csv-title "${total_pods}n-1d-1p-1c-gubu-${iteration}" -n ${total_pods} -d 1 -p 1 -c 1 -v 1 -l -r --no-probes ${resources} ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile} --enable-pod-annotations -a ${annotations}
   oc delete $(oc get pv -o name)
   echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
   sleep ${sleep_period}
   echo "****************************************************************************************************************************************"
done
#
# Mixed workload
#for iteration in `seq 1 ${iterations}`; do
#  test_index=$((${test_index} + 1))
#  annotations=" cpu-load-balancing.crio.io=\''true'\' irq-load-balancing.crio.io=\''disable'\' cpu-quota.crio.io=\''disable'\' "
#  resources=" --cpu-requests 50 --memory-requests 100 "
#   echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} - ${total_pods} namespaces, 1 deploy, 1 pod, 1 container, gohttp image, 1 service, 1 route, no probes, no configmaps, no secrets, ${resources}"
#   logfile="../logs/$(date -u +%Y%m%d-%H%M%S)-nodedensity-${tc_num}.${test_index}.log"
#   ../../boatload/boatload-mixed-pv2.py ${dryrun} ${csvfile} --csv-title "${total_pods}n-1d-1p-1c-gubu-${iteration}" -n ${total_pods} -d 1 -p 1  --no-probes ${gohttp_env_vars} ${measurement} ${INDEX_ARGS} &> ${logfile} 
#   echo "$(date -u +%Y%m%d-%H%M%S) - node density ${tc_num}.${test_index} - ${iteration}/${iterations} complete, sleeping ${sleep_period}"
#   sleep ${sleep_period}
#   echo "****************************************************************************************************************************************"
#done
#
#echo "$(date -u +%Y%m%d-%H%M%S) - Test Case ${tc_num} Complete"
