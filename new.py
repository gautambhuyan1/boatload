#!/usr/bin/env python3
#  Copyright 2021 Red Hat
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import argparse
import csv
import dateutil.parser as date_parser
from datetime import datetime
from jinja2 import Template
import json
import logging
import numpy as np
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid


workload_create = """---
global:
  writeToFile: true
  metricsDirectory: metrics
  measurements:
  - name: podLatency
    esIndex: {{ measurements_index }}

  indexerConfig:
    enabled: {{ indexing }}
    esServers: [{{ index_server}}]
    insecureSkipVerify: true
    defaultIndex: {{ default_index }}
    type: elastic

jobs:

#  - name: boatload-pv
#    jobType: create
#    jobIterations: 1
#    namespace: default
#    namespacedIterations: false
#    cleanup: true
#    waitFor: ["PersistentVolume"]
#    jobIterationDelay: 0s
#    jobPause: 0s
#    qps: {{ qps }}
#    burst: {{ burst }}
#    verifyObjects: true
#    errorOnVerify: false
#    objects:
#    - objectTemplate: workload-pv.yml
#      replicas: 61
#      namespaced: false

  - name: boatload
    jobType: create
    jobIterations: 1
    namespace: boatload
    namespacedIterations: true
    cleanup: false
    podWait: false
    waitWhenFinished: true
    jobIterationDelay: 0s
    jobPause: 0s
    qps: {{ qps }}
    burst: {{ burst }}
    verifyObjects: true
    errorOnVerify: false
    objects:
    - objectTemplate: workload-deployment-selector.yml
      replicas: {{ deployments }}
      inputVars:
        runtimeClassName: performance-perf-profile
        pod_replicas: {{ pod_replicas }}
        containers: {{ containers }}
        image: {{ container_image }}
        starting_port: {{ starting_port }}
        configmaps: {{ configmaps }}
        set_requests_hps: 1
        set_limits_hps: 1
        secrets: {{ secrets }}
        pvcs: {{pvcs}}
        set_requests_cpu: 28
        set_requests_memory: 100
        set_limits_cpu: 28
        set_limits_memory: 100
        net_resource: net_resource_boatload
        net_name: network-boatload        
        resources:
          requests:
            cpu: 28
            memory: 100Mi
            hugepages-1Gi: 1Gi
          limits:
            cpu: 28
            memory: 100Mi
            hugepages-1Gi: 1Gi
        pod_annotations:
        {%- for item in pod_annotations %}
        - {{ item | tojson }}
        {%- endfor %}
        container_env_args: {{ container_env_args }}
        enable_startup_probe: {{ startup_probe_args | length > 0 }}
        enable_liveness_probe: {{ liveness_probe_args | length > 0 }}
        enable_readiness_probe: {{ readiness_probe_args | length > 0 }}
        startup_probe_args: {{ startup_probe_args }}
        liveness_probe_args: {{ liveness_probe_args }}
        readiness_probe_args: {{ readiness_probe_args }}
        startup_probe_port: {{ startup_probe_port_enable }}
        liveness_probe_port: {{ liveness_probe_port_enable }}
        readiness_probe_port: {{ readiness_probe_port_enable }}
        default_selector: "{{ default_selector }}"
        shared_selectors: {{ shared_selectors }}
        unique_selectors: {{ unique_selectors }}
        unique_selector_offset: {{ offset }}
        tolerations: {{ tolerations }}
    {% if configmaps > 0 %}
    - objectTemplate: workload-configmap.yml
      replicas: {{ deployments * configmaps }}
    {% endif %}
    {% if secrets > 0 %}
    - objectTemplate: workload-secret.yml
      replicas: {{ deployments * secrets }}
    {% endif %}
    {% if pvcs > 0 %}
    - objectTemplate: workload-pvc.yml
      replicas: 1
    {% endif %}
    {% if service %}
    - objectTemplate: workload-service.yml
      replicas: 1
      inputVars:
        ports: {{ containers }}
        starting_port: {{ starting_port }}
    {% endif %}
    {% if route %}
    - objectTemplate: workload-route.yml
      replicas: 1
      inputVars:
        starting_port: {{ starting_port }}
    {% endif %}

  - name: boatload-bu
    jobType: create
    jobIterations: {{ namespaces }}
    namespace: boatload-bu
    namespacedIterations: true
    cleanup: false
    podWait: false
    waitWhenFinished: true
    jobIterationDelay: 0s
    jobPause: 0s
    qps: {{ qps }}
    burst: {{ burst }}
    verifyObjects: true
    errorOnVerify: false
    objects:
    - objectTemplate: workload-deployment-selector.yml
      replicas: {{ deployments }}
      inputVars:
        pod_replicas: {{ pod_replicas }}
        containers: {{ containers }}
        image: {{ container_image }}
        starting_port: {{ starting_port }}
        configmaps: {{ configmaps }}
        secrets: {{ secrets }}
        pvcs: {{pvcs}}
        set_requests_cpu: {{ cpu_requests > 0 }}
        set_requests_memory: {{ memory_requests > 0 }}
        set_limits_cpu: {{ cpu_limits > 0 }}
        set_limits_memory: {{ memory_limits > 0 }}
        set_requests_hps: {{ hugepages_requests > 0 }}
        set_limits_hps: {{ hugepages_limits > 0 }}
        net_resource: net_resource
        net_name: network
        resources:
          requests:
            cpu: {{ cpu_requests }}m
            memory: {{ memory_requests }}Mi
            hugepages-1Gi: {{ hugepages_requests }}Gi
          limits:
            cpu: {{ cpu_limits }}m
            memory: {{ memory_limits }}Mi
            hugepages-1Gi: {{ hugepages_limits }}Gi
        pod_annotations:
        {%- for item in pod_annotations %}
        - {{ item | tojson }}
        {%- endfor %}
        container_env_args: {{ container_env_args }}
        enable_startup_probe: {{ startup_probe_args | length > 0 }}
        enable_liveness_probe: {{ liveness_probe_args | length > 0 }}
        enable_readiness_probe: {{ readiness_probe_args | length > 0 }}
        startup_probe_args: {{ startup_probe_args }}
        liveness_probe_args: {{ liveness_probe_args }}
        readiness_probe_args: {{ readiness_probe_args }}
        startup_probe_port: {{ startup_probe_port_enable }}
        liveness_probe_port: {{ liveness_probe_port_enable }}
        readiness_probe_port: {{ readiness_probe_port_enable }}
        default_selector: "{{ default_selector }}"
        shared_selectors: {{ shared_selectors }}
        unique_selectors: {{ unique_selectors }}
        unique_selector_offset: {{ offset }}
        tolerations: {{ tolerations }}
    {% if configmaps > 0 %}
    - objectTemplate: workload-configmap.yml
      replicas: {{ deployments * configmaps }}
    {% endif %}
    {% if secrets > 0 %}
    - objectTemplate: workload-secret.yml
      replicas: {{ deployments * secrets }}
    {% endif %}
    {% if pvcs > 0 %}
    - objectTemplate: workload-pvc.yml
      replicas: {{ deployments }}
    {% endif %}
    {% if service %}
    - objectTemplate: workload-service.yml
      replicas: {{ deployments }}
      inputVars:
        ports: {{ containers }}
        starting_port: {{ starting_port }}
    {% endif %}
    {% if route %}
    - objectTemplate: workload-route.yml
      replicas: {{ deployments }}
      inputVars:
        starting_port: {{ starting_port }}
    {% endif %}

"""

workload_delete = """---
global:
  writeToFile: false
  measurements:
  - name: podLatency
    esIndex: {{ measurements_index }}

  indexerConfig:
    enabled: {{ indexing }}
    esServers: [{{ index_server}}]
    insecureSkipVerify: true
    defaultIndex: {{ default_index }}
    type: elastic

jobs:
- name: cleanup-boatload
  jobType: delete
  waitForDeletion: true
  qps: 10
  burst: 20
  objects:
  - kind: Namespace
    labelSelector: {kube-burner-job: boatload}
    apiVersion: v1

- name: cleanup-boatload-bu
  jobType: delete
  waitForDeletion: true
  qps: 10
  burst: 20
  objects:
  - kind: Namespace
    labelSelector: {kube-burner-job: boatload-bu}
    apiVersion: v1

#- name: cleanup-boatload-pv
#  jobType: delete
#  waitForDeletion: true
#  qps: 10
#  burst: 20
#  objects:
#  - kind: PersistentVolume
#    labelSelector: {kube-burner-job: boatload-pv}
#    apiVersion: v1

"""

workload_metrics = """---
global:
  writeToFile: true
  metricsDirectory: metrics
  measurements:
  - name: podLatency
    esIndex: {{ measurements_index }}

  indexerConfig:
    enabled: {{ indexing }}
    esServers: [{{ index_server}}]
    insecureSkipVerify: true
    defaultIndex: {{ default_index }}
    type: elastic
"""

#workload_pv = """---
#apiVersion: v1
#kind: PersistentVolume
#metadata:
#  name: pv-boatload-{{ .Iteration }}-{{ .Replica }}-{{ .JobName }}
#spec:
#  capacity:
#    storage: 1Gi
#  volumeMode: Filesystem
#  accessModes:
#  - ReadWriteOnce
#  persistentVolumeReclaimPolicy: Delete
#  storageClassName: local-storage
#  local:
#    path: /dev/sdc
#  nodeAffinity:
#    required:
#      nodeSelectorTerms:
#      - matchExpressions:
#        - key: kubernetes.io/hostname
#          operator: In
#          values:
#          - e32-h17-000-r750.stage.rdu2.scalelab.redhat.com
#"""

workload_deployment = """---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: boatload-{{ .Iteration }}-{{ .Replica }}-{{ .JobName }}
spec:
  replicas: {{ .pod_replicas }}
  selector:
    matchLabels:
      app: boatload-{{ .Iteration }}-{{ .Replica }}
  strategy:
    resources: {}
  template:
    metadata:
      annotations:
        {{ range .pod_annotations }}
        {{ . }}
        {{ end }}
        k8s.v1.cni.cncf.io/networks: {{ .net_name }}-{{ .Iteration }}
      labels:
        app: boatload-{{ .Iteration }}-{{ .Replica }}
    spec:
      runtimeClassName: performance-perf-profile
      containers:
      {{ $data := . }}
      {{ range $index, $element := sequence 1 .containers }}
      - name: boatload-{{ $element }}
        image: {{ $data.image }}
        ports:
        - containerPort: {{ add $data.starting_port $element }}
          protocol: TCP
        resources:
          requests:
            {{ if $data.set_requests_cpu }}
            cpu: {{ $data.resources.requests.cpu }}
            {{ end }}
            {{if $data.set_requests_memory }}
            memory: {{ $data.resources.requests.memory }}
            {{ end }}
            {{ if $data.set_requests_hps }}
            hugepages-1Gi: {{ index $data "resources" "requests" "hugepages-1Gi" }}
            {{ end }}
            {{ if $data.net_resource }}
            openshift.io/{{ $data.net_resource }}_{{ $data.Iteration }}: "1"
            {{ end }}
          limits:
            {{ if $data.set_limits_cpu }}
            cpu: {{ $data.resources.limits.cpu }}
            {{ end }}
            {{ if $data.set_limits_memory }}
            memory: {{ $data.resources.limits.memory }}
            {{ end }}
            {{ if $data.set_limits_hps }}
            hugepages-1Gi: {{ index $data "resources" "limits" "hugepages-1Gi" }}
            {{ end }}
            {{ if $data.net_resource }}
            openshift.io/{{ $data.net_resource }}_{{ $data.Iteration }}: "1"
            {{ end }}
        env:
        - name: PORT
          value: "{{ add $data.starting_port $element }}"
        {{ range $data.container_env_args }}
        - name: "{{ .name }}"
          value: "{{ .value }}"
        {{ end }}
        {{ if $data.enable_startup_probe }}
        startupProbe:
          {{ range $data.startup_probe_args }}
          {{ . }}
          {{ end }}
          {{ if $data.startup_probe_port }}
            port: {{ add $data.starting_port $element }}
          {{ end }}
        {{ end }}
        {{ if $data.enable_liveness_probe }}
        livenessProbe:
          {{ range $data.liveness_probe_args }}
          {{ . }}
          {{ end }}
          {{ if $data.liveness_probe_port }}
            port: {{ add $data.starting_port $element }}
          {{ end }}
        {{ end }}
        {{ if $data.enable_readiness_probe }}
        readinessProbe:
          {{ range $data.readiness_probe_args }}
          {{ . }}
          {{ end }}
          {{ if $data.readiness_probe_port }}
            port: {{ add $data.starting_port $element }}
          {{ end }}
        {{ end }}
        volumeMounts:
        {{ range $index, $element := sequence 1 $data.pvcs }}
        - name: pvc-{{ $element }}
          mountPath: /etc/pvc-{{ $element }}
        {{ end }}
        {{ range $index, $element := sequence 1 $data.configmaps }}
        - name: cm-{{ $element }}
          mountPath: /etc/cm-{{ $element }}
        {{ end }}
        {{ range $index, $element := sequence 1 $data.secrets }}
        - name: secret-{{ $element }}
          mountPath: /etc/secret-{{ $element }}
        {{ end }}
        {{ if $data.set_requests_hps }}
        - name: hugepage
          mountPath: /dev/hugepages
        {{ end }}
      {{ end }}
      volumes:
      {{ range $index, $element := sequence 1 .pvcs }}
      {{ $d_index := add $data.Replica -1 }}
      {{ $d_pvcs_count := multiply $d_index $data.pvcs }}
      {{ $pvcs_index := add $d_pvcs_count $element }}
      - name: pvc-{{ $element }}
        persistentVolumeClaim:
          claimName: boatload-{{ $data.Iteration }}-{{ $pvcs_index }}-{{ $data.JobName }}
      {{ end }}
      {{ range $index, $element := sequence 1 .configmaps }}
      {{ $d_index := add $data.Replica -1 }}
      {{ $d_cm_count := multiply $d_index $data.configmaps }}
      {{ $cm_index := add $d_cm_count $element }}
      - name: cm-{{ $element }}
        configMap:
          name: boatload-{{ $data.Iteration }}-{{ $cm_index }}-{{ $data.JobName }}
      {{ end }}
      {{ range $index, $element := sequence 1 .secrets }}
      {{ $d_index := add $data.Replica -1 }}
      {{ $d_s_count := multiply $d_index $data.secrets }}
      {{ $s_index := add $d_s_count $element }}
      - name: secret-{{ $element }}
        secret:
          secretName: boatload-{{ $data.Iteration }}-{{ $s_index }}-{{ $data.JobName }}
      {{ end }}
      {{ if $data.set_requests_hps }}
      - name: hugepage
        emptyDir:
         medium: HugePages
        restartPolicy: Never
      {{ end }}
      nodeSelector:
        {{ .default_selector }}
        {{ range $index, $element := sequence 1 .shared_selectors }}
        boatloads-{{ $element }}: "true"
        {{ end }}
        {{ $data := . }}
        {{ range $index, $element := sequence 1 $data.unique_selectors }}
        {{ $first := multiply $data.unique_selector_offset $index }}
        boatloadu-{{ add $first $data.Iteration }}: "true"
        {{ end }}
      {{ if .tolerations }}
      tolerations:
      - key: "node.kubernetes.io/unreachable"
        operator: "Exists"
        effect: "NoExecute"
      - key: "node.kubernetes.io/not-ready"
        operator: "Exists"
        effect: "NoExecute"
      - key: "node.kubernetes.io/unschedulable"
        operator: "Exists"
        effect: "NoExecute"
      {{ end }}
"""

workload_service = """---
apiVersion: v1
kind: Service
metadata:
  name: boatload-{{ .Iteration }}-{{ .Replica }}-{{ .JobName }}
spec:
  selector:
    app: boatload-{{ .Iteration }}-{{ .Replica }}
  ports:
    {{ $data := . }}
    {{ range $index, $element := sequence 1 .ports }}
    - protocol: TCP
      name: port-{{ add $data.starting_port $element }}
      port: {{ add 80 $element }}
      targetPort: {{ add $data.starting_port $element }}
    {{ end }}
"""

workload_route = """---
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: boatload-{{ .Iteration }}-{{ .Replica }}-{{ .JobName }}
spec:
  tls:
    termination: edge
  to:
    name: boatload-{{ .Iteration }}-{{ .Replica }}-{{ .JobName }}
"""

workload_configmap = """---
apiVersion: v1
kind: ConfigMap
metadata:
  name: boatload-{{ .Iteration }}-{{ .Replica }}-{{ .JobName }}
data:
  boatload-{{ .Iteration }}-{{ .Replica }}-{{ .JobName }}: "Random data"
"""

workload_secret = """---
apiVersion: v1
kind: Secret
metadata:
  name: boatload-{{ .Iteration }}-{{ .Replica }}-{{ .JobName }}
data:
  boatload-{{ .Iteration }}-{{ .Replica }}-{{ .JobName }}: UmFuZG9tIGRhdGEK
"""

workload_pvc = """---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: boatload-{{ .Iteration }}-{{ .Replica }}-{{ .JobName }}
spec:
  accessModes:
  - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 1Gi
  storageClassName: example-storage-class-1
"""

metrics_header = ["start_ts", "workload_complete_ts", "measurement_complete_ts", "cleanup_complete_ts", "end_ts",
    "start_time", "workload_complete_time", "measurement_complete_time", "cleanup_complete_time", "end_time",
    "title", "workload_uuid",]

logging.basicConfig(level=logging.INFO, format="%(asctime)s : %(levelname)s : %(message)s")
logger = logging.getLogger("boatload")
logging.Formatter.converter = time.gmtime


def command(cmd, dry_run, cmd_directory="", mask_output=False, mask_arg=0, no_log=False):
  if cmd_directory != "":
    logger.debug("Command Directory: {}".format(cmd_directory))
    working_directory = os.getcwd()
    os.chdir(cmd_directory)
  if dry_run:
    cmd.insert(0, "echo")
  if mask_arg == 0:
    logger.info("Command: {}".format(" ".join(cmd)))
  else:
    logger.info("Command: {} {} {}".format(" ".join(cmd[:mask_arg - 1]), "**(Masked)**", " ".join(cmd[mask_arg:])))
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

  output = ""
  while True:
    output_line = process.stdout.readline()
    if output_line.strip() != "":
      if not no_log:
        if not mask_output:
          logger.info("Output : {}".format(output_line.strip()))
        else:
          logger.info("Output : **(Masked)**")
      if output == "":
        output = output_line.strip()
      else:
        output = "{}\n{}".format(output, output_line.strip())
    return_code = process.poll()
    if return_code is not None:
      for output_line in process.stdout.readlines():
        if output_line.strip() != "":
          if not no_log:
            if not mask_output:
              logger.info("Output : {}".format(output_line.strip()))
            else:
              logger.info("Output : **(Masked)**")
          if output == "":
            output = output_line
          else:
            output = "{}\n{}".format(output, output_line.strip())
      logger.debug("Return Code: {}".format(return_code))
      break
  if cmd_directory != "":
    os.chdir(working_directory)
  return return_code, output


def parse_container_env_args(args):
  container_env_args = []
  for arg in args:
    split_args = arg.split("=")
    logger.debug("Parsing container env args: {}".format(split_args))
    if len(split_args) == 2:
      container_env_args.append({"name": split_args[0], "value": split_args[1]})
    else:
      logger.warning("Skipping Container env argument: {}".format(split_args))
  return container_env_args


def parse_probe_args(args, path, command):
  split_args = args.split(",")
  prefixes = ["initialDelaySeconds:", "periodSeconds:", "timeoutSeconds:", "failureThreshold:", "successThreshold:"]
  probe_args = []
  logger.debug("Parsing probe args: {}".format(split_args))

  if len(split_args) > 1 and len(split_args) <= 6:
    for index, arg in enumerate(split_args[1:]):
      if arg.isdigit():
        probe_args.append("{} {}".format(prefixes[index], arg))
      else:
        logger.error("Probe argument not an integer: {}".format(arg))
        sys.exit(1)
  elif len(split_args) > 6:
    logger.error("Too many probe arguments: {}".format(split_args))
    sys.exit(1)

  if split_args[0].lower() == "http":
    probe_args.extend(["httpGet:", "  path: {}".format(path)])
  elif split_args[0].lower() == "tcp":
    probe_args.append("tcpSocket:")
  elif split_args[0].lower() == "exec":
    probe_args.extend(["exec:", "  command:"])
    # Split the command by "\n" and attach the prefix of "  - " to each line
    probe_args.extend(list("  - " + line for line in command.split("\n")))
  elif split_args[0].lower() == "off":
    return []
  else:
    logger.error("Unrecognized probe argument: {}".format(split_args[0]))
    sys.exit(1)

  return probe_args


def parse_tc_netem_args(cliargs):
  args = {}

  if cliargs.latency > 0:
    args["latency"] = ["delay", "{}ms".format(cliargs.latency)]
  if cliargs.packet_loss > 0:
    args["packet loss"] = ["loss", "{}%".format(cliargs.packet_loss)]
  if cliargs.bandwidth_limit > 0:
    args["bandwidth limit"] = ["rate", "{}kbit".format(cliargs.bandwidth_limit)]

  return args


def apply_tc_netem(interface, start_vlan, end_vlan, impairments, dry_run=False):
  if len(impairments) > 1:
    logger.info("Applying {} impairments".format(", ".join(impairments.keys())))
  elif len(impairments) == 1:
    logger.info("Applying only {} impairment".format(list(impairments.keys())[0]))
  else:
    logger.warn("Invalid state. Applying no impairments.")

  for vlan in range(start_vlan, end_vlan + 1):
    tc_command = ["tc", "qdisc", "add", "dev", "{}.{}".format(interface, vlan), "root", "netem"]
    for impairment in impairments.values():
      tc_command.extend(impairment)
    rc, _ = command(tc_command, dry_run)
    if rc != 0:
      logger.error("boatload applying impairments failed, tc rc: {}".format(rc))
      sys.exit(1)


def remove_tc_netem(interface, start_vlan, end_vlan, dry_run=False, ignore_errors=False):
  logger.info("Removing bandwidth, latency, and packet loss impairments")
  for vlan in range(start_vlan, end_vlan + 1):
    tc_command = ["tc", "qdisc", "del", "dev", "{}.{}".format(interface, vlan), "root", "netem"]
    rc, _ = command(tc_command, dry_run)
    if rc != 0 and not ignore_errors:
      logger.error("boatload removing impairments failed, tc rc: {}".format(rc))
      sys.exit(1)


def flap_links_down(interface, start_vlan, end_vlan, dry_run, iptables, network):
  logger.info("Flapping links down")
  for vlan in range(start_vlan, end_vlan + 1):
    if iptables:
      iptables_command = [
          "iptables", "-A", "FORWARD", "-j", "DROP", "-i", "{}.{}".format(interface, vlan), "-d", network]
      rc, _ = command(iptables_command, dry_run)
      if rc != 0:
        logger.error("boatload, iptables rc: {}".format(rc))
        sys.exit(1)
    else:
      ip_command = ["ip", "link", "set", "{}.{}".format(interface, vlan), "down"]
      rc, _ = command(ip_command, dry_run)
      if rc != 0:
        logger.error("boatload, ip link set {} down rc: {}".format("{}.{}".format(interface, vlan), rc))
        sys.exit(1)


def flap_links_up(interface, start_vlan, end_vlan, dry_run, iptables, network, ignore_errors=False):
  logger.info("Flapping links up")
  for vlan in range(start_vlan, end_vlan + 1):
    if iptables:
      iptables_command = [
          "iptables", "-D", "FORWARD", "-j", "DROP", "-i", "{}.{}".format(interface, vlan), "-d", network]
      rc, _ = command(iptables_command, dry_run)
      if rc != 0 and not ignore_errors:
        logger.error("boatload, iptables rc: {}".format(rc))
        sys.exit(1)
    else:
      ip_command = ["ip", "link", "set", "{}.{}".format(interface, vlan), "up"]
      rc, _ = command(ip_command, dry_run)
      if rc != 0 and not ignore_errors:
        logger.error("boatload, ip link set {} up rc: {}".format("{}.{}".format(interface, vlan), rc))
        sys.exit(1)


def phase_break():
  logger.info("###############################################################################")


def write_csv_metrics(metrics_file_name, metrics_header, results):
  logger.info("Writing metrics csv to {}".format(metrics_file_name))
  write_header = False
  if not pathlib.Path(metrics_file_name).is_file():
    write_header = True
  with open(metrics_file_name, "a") as csvfile:
    csv_writer = csv.writer(csvfile)
    if write_header:
      csv_writer.writerow(metrics_header)
    csv_writer.writerow(results)


def write_csv_results(result_file_name, results):
  header = ["start_ts", "workload_complete_ts", "measurement_complete_ts", "cleanup_complete_ts", "end_ts",
      "start_time", "workload_complete_time", "measurement_complete_time", "cleanup_complete_time", "end_time",
      "title", "workload_uuid", "workload_duration", "measurement_duration", "cleanup_duration", "metrics_duration",
      "total_duration", "namespaces", "deployments", "pods", "containers", "services", "routes", "configmaps",
      "secrets", "pvcs", "image", "cpu_requests", "memory_requests", "cpu_limits", "memory_limits", "hugepages_limits", "startup_probe",
      "liveness_probe", "readiness_probe", "shared_selectors", "unique_selectors", "tolerations", "kb_qps", "kb_burst",
      "duration", "interface", "start_vlan", "end_vlan", "latency", "packet_loss", "bandwidth_limit", "flap_down",
      "flap_up", "firewall", "network", "indexed", "dry_run", "flapped_down", "NodeNotReady_node-controller",
      "NodeNotReady_kubelet", "NodeReady", "TaintManagerEviction_pods", "killed_pods", "started_pods",  "notready_pods", "kb_PodScheduled_avg",
      "kb_PodScheduled_max", "kb_PodScheduled_p50", "kb_PodScheduled_p95", "kb_PodScheduled_p99", "kb_Initialized_avg",
      "kb_Initialized_max", "kb_Initialized_p50", "kb_Initialized_p95", "kb_Initialized_p99", "kb_ContainersReady_avg",
      "kb_ContainersReady_max", "kb_ContainersReady_p50", "kb_ContainersReady_p95", "kb_ContainersReady_p99",
      "kb_Ready_avg", "kb_Ready_max", "kb_Ready_p50", "kb_Ready_p95", "kb_Ready_p99",]

  logger.info("Writing results to {}".format(result_file_name))
  write_header = False
  if not pathlib.Path(result_file_name).is_file():
    write_header = True
  with open(result_file_name, "a") as csvfile:
    csv_writer = csv.writer(csvfile)
    if write_header:
      csv_writer.writerow(header)
    csv_writer.writerow(results)


def main():
  start_time = time.time()

  # Default annotation is to apply an additional network (net1) from default namespace
  # Annotations are disabled by default
  default_pod_annotations = [
      "k8s.v1.cni.cncf.io/networks='[{\"name\": \"net1\", \"namespace\": \"default\"}]'"
  ]

  default_container_env = [
      "LISTEN_DELAY_SECONDS=20", "LIVENESS_DELAY_SECONDS=10", "READINESS_DELAY_SECONDS=30",
      "RESPONSE_DELAY_MILLISECONDS=50", "LIVENESS_SUCCESS_MAX=60", "READINESS_SUCCESS_MAX=30"
  ]
  # Defaults set for bare-metal cluster nodedensity metrics
#  default_metrics_collected = [
#      "nodeReadyStatus", "nodeCoresUsed", "nodeMemoryConsumed", "kubeletCoresUsed",
#      "kubeletMemory", "crioCoresUsed", "crioMemory"
#  ]
  # Recommended SNO nodedensity metrics
  default_metrics_collected = [
      "nodeReadyStatus", "nodeCoresUsed", "nodeMemoryConsumed", "nodeCPU", "kubeletCoresUsed",
      "kubeletMemory", "kubeletCPU", "crioCoresUsed", "crioMemory", "crioCPU", "rxNetworkBytes", "txNetworkBytes",
      "nodeDiskWrittenBytes", "nodeDiskReadBytes"
  ]

  parser = argparse.ArgumentParser(
      description="Run boatload",
      prog="boatload.py", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # Phase arguments
  parser.add_argument("--no-workload-phase", action="store_true", default=False, help="Disables workload phase")
  parser.add_argument("--no-measurement-phase", action="store_true", default=False, help="Disables measurement phase")
  parser.add_argument("--no-cleanup-phase", action="store_true", default=False, help="Disables cleanup phase")
  parser.add_argument("--no-metrics-phase", action="store_true", default=False, help="Disables metrics phase")

  # Workload arguments
  parser.add_argument("-n", "--namespaces", type=int, default=1, help="Number of namespaces to create")
  parser.add_argument("-d", "--deployments", type=int, default=1, help="Number of deployments per namespace to create")
  parser.add_argument("-l", "--service", action="store_true", default=False, help="Include service per deployment")
  parser.add_argument("-r", "--route", action="store_true", default=False, help="Include route per deployment")
  parser.add_argument("-p", "--pods", type=int, default=1, help="Number of pod replicas per deployment to create")
  parser.add_argument("-v", "--pvcs", type=int, default=1, help="Number of pvcs per deployment to create")
  parser.add_argument("-c", "--containers", type=int, default=1, help="Number of containers per pod replica to create")

  # Workload annotation arguments
  parser.add_argument("--enable-pod-annotations", action="store_true", default=False, help="Enable pod annotations")
  parser.add_argument("-a", "--pod-annotations", nargs="*", default=default_pod_annotations,
                      help="The pod annotations")

  # Workload container image, port, environment, and resources arguments
  parser.add_argument("-i", "--container-image", type=str,
                      default="quay.io/redhat-performance/test-gohttp-probe:v0.0.2", help="The container image to use")
  parser.add_argument("--container-port", type=int, default=8000,
                      help="The starting container port to expose (PORT Env Var)")
  parser.add_argument("-e", "--container-env", nargs="*", default=default_container_env,
                      help="The container environment variables")
  parser.add_argument("-m", "--configmaps", type=int, default=0, help="Number of configmaps per container")
  parser.add_argument("--secrets", type=int, default=0, help="Number of secrets per container")
  parser.add_argument("--cpu-requests", type=int, default=0, help="CPU requests per container (millicores)")
  parser.add_argument("--memory-requests", type=int, default=0, help="Memory requests per container (MiB)")
  parser.add_argument("--hugepages-requests", type=int, default=0, help="Hugepages-1Gi requests per container (Gi)")
  parser.add_argument("--cpu-limits", type=int, default=0, help="CPU limits per container (millicores)")
  parser.add_argument("--memory-limits", type=int, default=0, help="Memory limits per container (MiB)")
  parser.add_argument("--hugepages-limits", type=int, default=0, help="Hugepages-1Gi limits per container (Gi)")

  # Workload probe arguments
  parser.add_argument("--startup-probe", type=str, default="http,0,10,1,12",
                      help="Container startupProbe configuration")
  parser.add_argument("--liveness-probe", type=str, default="http,0,10,1,3",
                      help="Container livenessProbe configuration")
  parser.add_argument("--readiness-probe", type=str, default="http,0,10,1,3,1",
                      help="Container readinessProbe configuration")
  parser.add_argument("--startup-probe-endpoint", type=str, default="/livez", help="startupProbe endpoint")
  parser.add_argument("--liveness-probe-endpoint", type=str, default="/livez", help="livenessProbe endpoint")
  parser.add_argument("--readiness-probe-endpoint", type=str, default="/readyz", help="readinessProbe endpoint")
  parser.add_argument("--startup-probe-exec-command", type=str, default="test\n-f\n/tmp/startup", help="startupProbe exec command")
  parser.add_argument("--liveness-probe-exec-command", type=str, default="test\n-f\n/tmp/liveness", help="livenessProbe exec command")
  parser.add_argument("--readiness-probe-exec-command", type=str, default="test\n-f\n/tmp/readiness", help="readinessProbe exec command")
  parser.add_argument("--no-probes", action="store_true", default=False, help="Disable all probes")

  # Workload node-selector/tolerations arguments
  parser.add_argument("--default-selector", type=str, default="jetlag: 'true'", help="Default node-selector")
  parser.add_argument("-s", "--shared-selectors", type=int, default=0, help="How many shared node-selectors to use")
  parser.add_argument("-u", "--unique-selectors", type=int, default=0, help="How many unique node-selectors to use")
  parser.add_argument("-o", "--offset", type=int, default=0, help="Offset for iterated unique node-selectors")
  parser.add_argument("--tolerations", action="store_true", default=False, help="Include RWN tolerations on pod spec")

  # kube-burner qps/burst settings
  parser.add_argument("-q", "--kb-qps", type=int, default=20, help="kube-burner qps setting")
  parser.add_argument("-b", "--kb-burst", type=int, default=40, help="kube-burner burst setting")

  # Measurement arguments
  parser.add_argument(
      "-D", "--duration", type=int, default=30, help="Duration of measurement/impairment phase (Seconds)")
  parser.add_argument("-I", "--interface", type=str, default="ens1f1", help="Interface of vlans to impair")
  parser.add_argument("-S", "--start-vlan", type=int, default=100, help="Starting VLAN off interface")
  parser.add_argument("-E", "--end-vlan", type=int, default=105, help="Ending VLAN off interface")
  parser.add_argument(
      "-L", "--latency", type=int, default=0, help="Amount of latency to add to all VLANed interfaces (milliseconds)")
  parser.add_argument(
      "-P", "--packet-loss", type=int, default=0, help="Percentage of packet loss to add to all VLANed interfaces")
  parser.add_argument(
      "-B", "--bandwidth-limit", type=int, default=0,
      help="Bandwidth limit to apply to all VLANed interfaces (kilobits). 0 for no limit.")
  parser.add_argument("-F", "--link-flap-down", type=int, default=0, help="Time period to flap link down (Seconds)")
  parser.add_argument("-U", "--link-flap-up", type=int, default=0, help="Time period to flap link up (Seconds)")
  parser.add_argument("-T", "--link-flap-firewall", action="store_true", default=False,
                      help="Flaps links via iptables instead of ip link set")
  parser.add_argument("-N", "--link-flap-network", type=str, default="198.18.10.0/24",
                      help="Network to block for iptables link flapping")

  # Metrics arguments
  parser.add_argument("--metrics-profile", type=str, default="metrics.yaml", help="Metrics profile for kube-burner")
  parser.add_argument("--prometheus-url", type=str, default="", help="Cluster prometheus URL")
  parser.add_argument("--prometheus-token", type=str, default="", help="Token to access prometheus")
  parser.add_argument(
      "--metrics", nargs="*", default=default_metrics_collected, help="List of metrics to collect into metrics.csv")

  # Indexing arguments
  parser.add_argument(
      "--index-server", type=str, default="", help="ElasticSearch server (Ex https://user:password@example.org:9200)")
  parser.add_argument("--default-index", type=str, default="boatload-default", help="Default index")
  parser.add_argument("--measurements-index", type=str, default="boatload-default", help="Measurements index")

  # CSV results/metrics file arguments:
  parser.add_argument("--csv-results-file", type=str, default="results.csv", help="Determines results csv to append to")
  parser.add_argument("--csv-metrics-file", type=str, default="metrics.csv", help="Determines metrics csv to append to")
  parser.add_argument("--csv-title", type=str, default="untitled", help="Determines title of row of data")

  # Other arguments
  parser.add_argument("--cleanup", action="store_true", default=False, help="Shortcut to only run cleanup phase")
  parser.add_argument("--debug", action="store_true", default=False, help="Set log level debug")
  parser.add_argument("--dry-run", action="store_true", default=False, help="Echos commands instead of executing them")
  parser.add_argument("--reset", action="store_true", default=False, help="Attempts to undo all network impairments")

  cliargs = parser.parse_args()

  if cliargs.debug:
    logger.setLevel(logging.DEBUG)

  phase_break()
  if cliargs.dry_run:
    logger.info("boatload - Dry Run")
  else:
    logger.info("boatload")
  phase_break()
  logger.debug("CLI Args: {}".format(cliargs))

  if cliargs.enable_pod_annotations:
    pd_annotations_parsed = [annotation.replace("=", ": ") for annotation in cliargs.pod_annotations]
    cliargs.pod_annotations = pd_annotations_parsed
  else:
    cliargs.pod_annotations = []

  container_env_args = parse_container_env_args(cliargs.container_env)

  if cliargs.no_probes:
    cliargs.startup_probe = "off"
    cliargs.liveness_probe = "off"
    cliargs.readiness_probe = "off"
  startup_probe_args = parse_probe_args(
      cliargs.startup_probe, cliargs.startup_probe_endpoint, cliargs.startup_probe_exec_command)
  liveness_probe_args = parse_probe_args(
      cliargs.liveness_probe, cliargs.liveness_probe_endpoint, cliargs.liveness_probe_exec_command)
  readiness_probe_args = parse_probe_args(
      cliargs.readiness_probe, cliargs.readiness_probe_endpoint, cliargs.readiness_probe_exec_command)

  netem_impairments = parse_tc_netem_args(cliargs)

  if cliargs.reset:
    logger.info("Resetting all network impairments")
    flap_links_up(cliargs.interface, cliargs.start_vlan, cliargs.end_vlan, cliargs.dry_run, cliargs.link_flap_firewall,
                  cliargs.link_flap_network, ignore_errors=True)
    remove_tc_netem(
        cliargs.interface,
        cliargs.start_vlan,
        cliargs.end_vlan,
        cliargs.dry_run,
        ignore_errors=True)
    sys.exit(0)

  if cliargs.no_workload_phase and cliargs.no_measurement_phase and cliargs.no_cleanup_phase:
    logger.error("No meaningful phases enabled. Exiting...")
    sys.exit(0)

  if cliargs.cleanup:
    logger.info("--cleanup set, only running cleanup phase")
    cliargs.no_workload_phase = True
    cliargs.no_measurement_phase = True
    cliargs.no_cleanup_phase = False
    cliargs.no_metrics_phase = True

  # Validate link flap args
  flap_links = False
  if not cliargs.no_measurement_phase:
    if ((cliargs.link_flap_down == 0 and cliargs.link_flap_up > 0)
       or (cliargs.link_flap_down > 0 and cliargs.link_flap_up == 0)):
      logger.error("Both link flap args (--link-flap-down, --link-flap-up) are required for link flapping. Exiting...")
      sys.exit(1)
    elif cliargs.link_flap_down > 0 and cliargs.link_flap_up > 0:
      if cliargs.link_flap_firewall:
        logger.info("Link flapping enabled via iptables")
        flap_links = True
      else:
        if len(netem_impairments) > 0:
          logger.warning("Netem (Bandwidth/Latency/Packet Loss) impairments are mutually exclusive to link flapping "
                         "impairment via ip link. Use -T flag to combine impairments by using iptables instead of ip "
                         "link. Disabling link flapping.")
        else:
          logger.info("Link flapping enabled via ip link")
          flap_links = True
    else:
      logger.debug("Link flapping impairment disabled")

  # Validate metrics phase arguments
  if not cliargs.no_metrics_phase:
    logger.info("Metrics phase is enabled, checking metrics profile")
    base_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    base_dir_kb = os.path.join(base_dir, "kube-burner")

    if not pathlib.Path(cliargs.metrics_profile).is_file():
      kb_metrics_profile = os.path.join(base_dir, cliargs.metrics_profile)
      if not pathlib.Path(kb_metrics_profile).is_file():
        kb_metrics_profile = os.path.join(base_dir, "kube-burner", cliargs.metrics_profile)
        if pathlib.Path(kb_metrics_profile).is_file():
          cliargs.metrics_profile = kb_metrics_profile
        else:
          logger.error("Metrics Profile ({}) not found in: {} or {}".format(cliargs.metrics_profile, base_dir, base_dir_kb))
          sys.exit(1)
      else:
        cliargs.metrics_profile = kb_metrics_profile

    logger.info("Checking prometheus url and token")
    if cliargs.prometheus_url == "":
      logger.info("Prometheus URL not set, attempting to get prometheus URL with OpenShift client")
      oc_cmd = ["oc", "get", "route/prometheus-k8s", "-n", "openshift-monitoring", "--no-headers", "-o",
                "custom-columns=HOST:status.ingress[].host"]
      rc, output = command(oc_cmd, cliargs.dry_run)
      if rc != 0:
        logger.warning("Unable to determine prometheus URL via oc, disabling metrics phase, oc rc: {}".format(rc))
      else:
        cliargs.prometheus_url = "https://{}".format(output)

    if cliargs.prometheus_token == "" and not (cliargs.prometheus_url == ""):
      logger.info("Prometheus token not set, attempting to get prometheus "
                  "token with OpenShift client and kubeburner sa")
      oc_cmd = ["oc", "sa", "get-token", "kubeburner", "-n", "default"]
      rc, output = command(oc_cmd, cliargs.dry_run, mask_output=True)
      if rc != 0:
        logger.warning("Unable to determine prometheus token via oc, disabling metrics phase, oc rc: {}".format(rc))
        logger.warning(
            "To remedy, as cluster-admin, run 'oc create sa kubeburner -n default' and "
            "'oc adm policy add-cluster-role-to-user -z kubeburner cluster-admin'")
      else:
        cliargs.prometheus_token = output

    if cliargs.prometheus_url == "" or cliargs.prometheus_token == "":
      logger.warning("Prometheus server or token unset, disabling metrics phase")
      cliargs.no_metrics_phase = True

  # Validate indexing args
  indexing_enabled = False
  if not cliargs.index_server == "":
    if not cliargs.no_metrics_phase:
      logger.info("Indexing server is set, indexing measurements and metrics enabled")
    else:
      logger.info("Indexing server is set, indexing measurements enabled")
    clean_server = cliargs.index_server[cliargs.index_server.find("@") + 1:].replace("\"", "")
    logger.info("Indexing server: {}".format(clean_server))
    indexing_enabled = True
  else:
    logger.info("Indexing server is unset, all indexing is disabled")

  logger.info("Scenario Phases:")
  if not cliargs.no_workload_phase:
    logger.info("* Workload Phase")
    if indexing_enabled:
      logger.info("  * Measurement index: {}".format(cliargs.measurements_index))
    else:
      logger.info("  * No measurement indexing")
    logger.info("  * {} Namespace(s)".format(cliargs.namespaces))
    logger.info("  * {} Deployment(s) per namespace".format(cliargs.deployments))
    if cliargs.service:
      logger.info("  * 1 Service per deployment")
    else:
      logger.info("  * No Service per deployment")
    if cliargs.pvcs:
      logger.info("  * 1 PVC per deployment")
    else:
      logger.info("  * No PVC per deployment")
    if cliargs.route:
      logger.info("  * 1 Route per deployment")
    else:
      logger.info("  * No Route per deployment")
    logger.info("  * {} Pod replica(s) per deployment".format(cliargs.pods))
    logger.info("  * {} Container(s) per pod replica".format(cliargs.containers))
    logger.info("  * {} ConfigMap(s) per deployment".format(cliargs.configmaps))
    logger.info("  * {} Secret(s) per deployment".format(cliargs.secrets))
    logger.info("  * Pod Annotations: {}".format(cliargs.pod_annotations))
    logger.info("  * Container Image: {}".format(cliargs.container_image))
    logger.info("  * Container starting port: {}".format(cliargs.container_port))
    logger.info("  * Container CPU: {}m requests, {}m limits".format(cliargs.cpu_requests, cliargs.cpu_limits))
    logger.info(
        "  * Container Memory: {}Mi requests, {}Mi limits".format(cliargs.memory_requests, cliargs.memory_limits))
    logger.info("  * Container Hugepages-1Gi: {}Gi requests, {}Gi limits".format(cliargs.hugepages_requests, cliargs.hugepages_limits))
    logger.info("  * Container Environment: {}".format(container_env_args))
    su_probe = cliargs.startup_probe.split(",")[0]
    l_probe = cliargs.liveness_probe.split(",")[0]
    r_probe = cliargs.readiness_probe.split(",")[0]
    startup_probe_port_enable = True if su_probe in ["tcp", "http"] else False
    liveness_probe_port_enable = True if l_probe in ["tcp", "http"] else False
    readiness_probe_port_enable = True if r_probe in ["tcp", "http"] else False
    logger.info("  * Probes: startup: {}, liveness: {}, readiness: {}".format(su_probe, l_probe, r_probe))
    logger.info("  * Default Node-Selector: {}".format(cliargs.default_selector))
    logger.info("  * {} Shared Node-Selectors".format(cliargs.shared_selectors))
    logger.info("  * {} Unique Node-Selectors".format(cliargs.unique_selectors))
    if cliargs.tolerations:
      logger.info("  * RWN tolerations")
    else:
      logger.info("  * No tolerations")
  if not cliargs.no_measurement_phase:
    logger.info("* Measurement Phase - {}s Duration".format(cliargs.duration))
    if len(netem_impairments) > 0:
      logger.info("  * Bandwidth Limit: {}kbits".format(cliargs.bandwidth_limit))
      logger.info("  * Link Latency: {}ms".format(cliargs.latency))
      logger.info("  * Packet Loss: {}%".format(cliargs.packet_loss))
    if flap_links:
      flapping = "ip link"
      if cliargs.link_flap_firewall:
        flapping = "iptables"
      logger.info("  * Links {}.{} - {}.{}".format(
          cliargs.interface,
          cliargs.start_vlan,
          cliargs.interface,
          cliargs.end_vlan))
      logger.info("  * Flap {}s down, {}s up by {}".format(cliargs.link_flap_down, cliargs.link_flap_up, flapping))
    if len(netem_impairments) == 0 and not flap_links:
      logger.info("  * No impairments")
  if not cliargs.no_cleanup_phase:
    logger.info("* Cleanup Phase")
    if indexing_enabled:
      logger.info("  * Measurement index: {}".format(cliargs.measurements_index))
    else:
      logger.info("  * No measurement indexing")
  if not cliargs.no_metrics_phase:
    logger.info("* Metrics Phase")
    logger.info("  * Metrics profile file: {}".format(cliargs.metrics_profile))
    logger.info("  * Prometheus Url: {}".format(cliargs.prometheus_url))
    if indexing_enabled:
      logger.info("  * ES index: {}".format(cliargs.default_index))
    logger.info("  * Metrics csv file: {}".format(cliargs.csv_metrics_file))
    logger.info("  * Metrics to collect in csv: {}".format(cliargs.metrics))
  if not cliargs.cleanup:
    logger.info("Results csv file: {}".format(cliargs.csv_results_file))
    logger.info("Results title: {}".format(cliargs.csv_title))

  # Workload UUID is used with both workload and cleanup phases
  workload_UUID = str(uuid.uuid4())

  # Workload Phase
  workload_end_time = start_time
  if not cliargs.no_workload_phase:
    workload_start_time = time.time()
    phase_break()
    logger.info("Workload phase starting ({})".format(int(workload_start_time * 1000)))
    phase_break()

    t = Template(workload_create)
    workload_create_rendered = t.render(
        measurements_index=cliargs.measurements_index,
        indexing=indexing_enabled,
        index_server=cliargs.index_server,
        default_index=cliargs.default_index,
        namespaces=cliargs.namespaces,
        qps=cliargs.kb_qps,
        burst=cliargs.kb_burst,
        deployments=cliargs.deployments,
        pod_replicas=cliargs.pods,
        containers=cliargs.containers,
        container_image=cliargs.container_image,
        starting_port=cliargs.container_port - 1,
        configmaps=cliargs.configmaps,
        secrets=cliargs.secrets,
        cpu_requests=cliargs.cpu_requests,
        cpu_limits=cliargs.cpu_limits,
        hugepages_requests=cliargs.hugepages_requests,
        memory_requests=cliargs.memory_requests,
        memory_limits=cliargs.memory_limits,
        hugepages_limits=cliargs.hugepages_limits,
        pod_annotations=cliargs.pod_annotations,
        container_env_args=container_env_args,
        startup_probe_args=startup_probe_args,
        liveness_probe_args=liveness_probe_args,
        readiness_probe_args=readiness_probe_args,
        startup_probe_port_enable=startup_probe_port_enable,
        liveness_probe_port_enable=liveness_probe_port_enable,
        readiness_probe_port_enable=readiness_probe_port_enable,
        default_selector=cliargs.default_selector,
        shared_selectors=cliargs.shared_selectors,
        unique_selectors=cliargs.unique_selectors,
        offset=cliargs.offset,
        tolerations=cliargs.tolerations,
        service=cliargs.service,
        pvcs=cliargs.pvcs,
        route=cliargs.route)

    tmp_directory = tempfile.mkdtemp()
    logger.info("Created {}".format(tmp_directory))
    with open("{}/workload-create.yml".format(tmp_directory), "w") as file1:
      file1.writelines(workload_create_rendered)
    logger.info("Created {}/workload-create.yml".format(tmp_directory))
#    with open("{}/workload-pv.yml".format(tmp_directory), "w") as file1:
#      file1.writelines(workload_pv)
#    logger.info("Created {}/workload-pv.yml".format(tmp_directory))
    with open("{}/workload-deployment-selector.yml".format(tmp_directory), "w") as file1:
      file1.writelines(workload_deployment)
    logger.info("Created {}/workload-deployment-selector.yml".format(tmp_directory))
    with open("{}/workload-service.yml".format(tmp_directory), "w") as file1:
      file1.writelines(workload_service)
    logger.info("Created {}/workload-service.yml".format(tmp_directory))
    with open("{}/workload-route.yml".format(tmp_directory), "w") as file1:
      file1.writelines(workload_route)
    logger.info("Created {}/workload-route.yml".format(tmp_directory))
    with open("{}/workload-configmap.yml".format(tmp_directory), "w") as file1:
      file1.writelines(workload_configmap)
    logger.info("Created {}/workload-configmap.yml".format(tmp_directory))
    with open("{}/workload-secret.yml".format(tmp_directory), "w") as file1:
      file1.writelines(workload_secret)
    logger.info("Created {}/workload-secret.yml".format(tmp_directory))
    with open("{}/workload-pvc.yml".format(tmp_directory), "w") as file1:
      file1.writelines(workload_pvc)
    logger.info("Created {}/workload-pvc.yml".format(tmp_directory))
    workload_measurements_json = "{}/metrics/boatload-podLatency-summary.json".format(tmp_directory)

    kb_cmd = ["kube-burner", "init", "-c", "workload-create.yml", "--uuid", workload_UUID]
    rc, _ = command(kb_cmd, cliargs.dry_run, tmp_directory)
    if rc != 0:
      logger.error("boatload (workload-create.yml) failed, kube-burner rc: {}".format(rc))
      sys.exit(1)
    workload_end_time = time.time()
    logger.info("Workload phase complete ({})".format(int(workload_end_time * 1000)))

  # Measurement phase
  nodenotready_node_controller_count = 0
  nodenotready_kubelet_count = 0
  nodeready_count = 0
  link_flap_count = 0
  killed_pod = 0
  started_pod = 0
  notready_pod = 0
  marked_evictions = 0
  measurement_end_time = workload_end_time
  if not cliargs.no_measurement_phase:
    measurement_start_time = time.time()
    phase_break()
    logger.info("Measurement phase starting ({})".format(int(measurement_start_time * 1000)))
    phase_break()
    measurement_expected_end_time = measurement_start_time + cliargs.duration

    logger.info("Measurement phase start: {}, end: {}, duration: {}".format(
        datetime.utcfromtimestamp(measurement_start_time),
        datetime.utcfromtimestamp(measurement_expected_end_time),
        cliargs.duration))
    logger.info("Measurement phase expected end timestamp: {}".format(int(measurement_expected_end_time * 1000)))

    if len(netem_impairments):
      apply_tc_netem(
          cliargs.interface,
          cliargs.start_vlan,
          cliargs.end_vlan,
          netem_impairments,
          cliargs.dry_run)

    if flap_links:
      link_flap_count = 1
      flap_links_down(cliargs.interface, cliargs.start_vlan, cliargs.end_vlan, cliargs.dry_run,
                      cliargs.link_flap_firewall, cliargs.link_flap_network)
      next_flap_time = time.time() + cliargs.link_flap_down
      links_down = True

    wait_logger = 0
    current_time = time.time()
    while current_time < measurement_expected_end_time:
      if flap_links:
        if current_time >= next_flap_time:
          if links_down:
            links_down = False
            flap_links_up(cliargs.interface, cliargs.start_vlan, cliargs.end_vlan, cliargs.dry_run,
                          cliargs.link_flap_firewall, cliargs.link_flap_network)
            next_flap_time = time.time() + cliargs.link_flap_up
          else:
            links_down = True
            link_flap_count += 1
            flap_links_down(cliargs.interface, cliargs.start_vlan, cliargs.end_vlan, cliargs.dry_run,
                            cliargs.link_flap_firewall, cliargs.link_flap_network)
            next_flap_time = time.time() + cliargs.link_flap_down

      time.sleep(.1)
      wait_logger += 1
      if wait_logger >= 100:
        logger.info("Remaining measurement duration: {}".format(round(measurement_expected_end_time - current_time, 1)))
        wait_logger = 0
      current_time = time.time()

    if flap_links:
      flap_links_up(cliargs.interface, cliargs.start_vlan, cliargs.end_vlan, cliargs.dry_run,
                    cliargs.link_flap_firewall, cliargs.link_flap_network, True)

    if len(netem_impairments):
      remove_tc_netem(
          cliargs.interface,
          cliargs.start_vlan,
          cliargs.end_vlan,
          cliargs.dry_run)
    measurement_end_time = time.time()
    logger.info("Measurement phase complete ({})".format(int(measurement_end_time * 1000)))

    # OpenShift by default keeps kubernetes events for 3 hours
    # Thus measurement periods beyond 3 hours may not record correct counts for all events below
    phase_break()
    logger.info("Post measurement NodeNotReady/NodeReady count")
    phase_break()
    oc_cmd = ["oc", "get", "ev", "-n", "default", "--field-selector", "reason=NodeNotReady", "-o", "json"]
    rc, output = command(oc_cmd, cliargs.dry_run, no_log=True)
    if rc != 0:
      logger.error("boatload, oc get ev rc: {}".format(rc))
      sys.exit(1)
    if not cliargs.dry_run:
      json_data = json.loads(output)
    else:
      json_data = {"items": []}
    for item in json_data["items"]:
      last_timestamp_unix = date_parser.parse(item["lastTimestamp"]).timestamp()
      logger.debug(
          "Reviewing NodeNotReady event from {} which last occured {} / {}".format(item["source"]["component"],
          item["lastTimestamp"], last_timestamp_unix))
      if last_timestamp_unix >= measurement_start_time:
        if item["source"]["component"] == "node-controller":
          nodenotready_node_controller_count += 1
        elif item["source"]["component"] == "kubelet":
          nodenotready_kubelet_count += 1
        else:
          logger.warning("NodeNotReady, Unrecognized component: {}".format(item["source"]["component"]))
      else:
        logger.debug("Event occured before measurement started")

    oc_cmd = ["oc", "get", "ev", "-n", "default", "--field-selector", "reason=NodeReady", "-o", "json"]
    rc, output = command(oc_cmd, cliargs.dry_run, no_log=True)
    if rc != 0:
      logger.error("boatload, oc get ev rc: {}".format(rc))
      sys.exit(1)
    if not cliargs.dry_run:
      json_data = json.loads(output)
    else:
      json_data = {"items": []}
    for item in json_data["items"]:
      last_timestamp_unix = date_parser.parse(item["lastTimestamp"]).timestamp()
      logger.debug(
          "Reviewing NodeReady event which last occured {} / {}".format(item["lastTimestamp"], last_timestamp_unix))
      if last_timestamp_unix >= measurement_start_time:
        nodeready_count += 1
      else:
        logger.debug("Event occured before measurement started")
    logger.info("NodeNotReady event count reported by node-controller: {}".format(nodenotready_node_controller_count))
    logger.info("NodeNotReady event count reported by kubelet: {}".format(nodenotready_kubelet_count))
    logger.info("NodeReady event count: {}".format(nodeready_count))

    # Check for pods evicted before cleanup
    phase_break()
    logger.info("Post measurement pod eviction count")
    phase_break()
    ns_pattern1 = re.compile("boatload-[0-9]+")
    ns_pattern2 = re.compile("boatload-bu-[0-9]+")
    eviction_pattern = re.compile("Marking for deletion Pod")
    oc_cmd = ["oc", "get", "ev", "-A", "--field-selector", "reason=TaintManagerEviction", "-o", "json"]
    rc, output = command(oc_cmd, cliargs.dry_run, no_log=True)
    if rc != 0:
      logger.error("boatload, oc get ev rc: {}".format(rc))
      sys.exit(1)
    if not cliargs.dry_run:
      json_data = json.loads(output)
    else:
      json_data = {"items": []}
    for item in json_data["items"]:
      if ns_pattern1.search(item["involvedObject"]["namespace"]) and eviction_pattern.search(item["message"]):
        marked_evictions += 1
      if ns_pattern2.search(item["involvedObject"]["namespace"]) and eviction_pattern.search(item["message"]):
        marked_evictions += 1
    oc_cmd = ["oc", "get", "ev", "-A", "--field-selector", "reason=Killing", "-o", "json"]
    rc, output = command(oc_cmd, cliargs.dry_run, no_log=True)
    if rc != 0:
      logger.error("boatload, oc get ev rc: {}".format(rc))
      sys.exit(1)
    if not cliargs.dry_run:
      json_data = json.loads(output)
    else:
      json_data = {"items": []}
    x = 0
    y = 0
    for item in json_data["items"]:
      if ns_pattern1.search(item["involvedObject"]["namespace"]):
        killed_pod += 1
        if x == 0:
          print("ns_pattern1 =" , item["involvedObject"]["namespace"])
          x = 1
      if ns_pattern2.search(item["involvedObject"]["namespace"]):
        killed_pod += 1
        if y == 0: 
          print("ns_pattern2 =" , item["involvedObject"]["namespace"])
          y = 1
    oc_cmd = ["oc", "get", "ev", "-A", "--field-selector", "reason=Started", "-o", "json"]
    rc, output = command(oc_cmd, cliargs.dry_run, no_log=True)
    if rc != 0:
      logger.error("boatload, oc get ev rc: {}".format(rc))
      sys.exit(1)
    if not cliargs.dry_run:
      json_data = json.loads(output)
    else:
      json_data = {"items": []}
    for item in json_data["items"]:
      if ns_pattern1.search(item["involvedObject"]["namespace"]):
        started_pod += 1
      if ns_pattern2.search(item["involvedObject"]["namespace"]):
        started_pod += 1
    oc_cmd = ["oc", "get", "pods", "-A", "-o", "json"]
    rc, output = command(oc_cmd, cliargs.dry_run, no_log=True)
    if rc != 0:
     logger.error("boatload, oc get ev rc: {}".format(rc))
     sys.exit(1)
    if not cliargs.dry_run:
      json_data = json.loads(output)
    else:
      json_data = {"items": []}
    for item in json_data["items"]:
     #pod_name = item["metadata"]["name"]
      if ns_pattern1.search(item["metadata"]["namespace"]) or ns_pattern2.search(item["metadata"]["namespace"]):
        condition = [con for con in item["status"]["conditions"] if con["type"] == "Ready"][0]["status"]
        if item["status"]["phase"] != "Running" or condition == "False":
          notready_pod += 1
    logger.info("boatload-* pods marked for deletion by Taint Manager: {}".format(marked_evictions))
    logger.info("boatload-* pods killed: {}".format(killed_pod))
    logger.info("boatload-* pods started: {}".format(started_pod))
    logger.info("boatload-* pods not ready: {}".format(notready_pod))
  # Cleanup Phase
  cleanup_end_time = measurement_end_time
  if not cliargs.no_cleanup_phase:
    cleanup_start_time = time.time()
    phase_break()
    logger.info("Cleanup phase starting ({})".format(int(cleanup_start_time * 1000)))
    phase_break()

    t = Template(workload_delete)
    workload_delete_rendered = t.render(
        measurements_index=cliargs.measurements_index,
        indexing=indexing_enabled,
        index_server=cliargs.index_server,
        default_index=cliargs.default_index)

    tmp_directory = tempfile.mkdtemp()
    logger.info("Created {}".format(tmp_directory))
    with open("{}/workload-delete.yml".format(tmp_directory), "w") as file1:
      file1.writelines(workload_delete_rendered)
    logger.info("Created {}/workload-delete.yml".format(tmp_directory))

    kb_cmd = ["kube-burner", "init", "-c", "workload-delete.yml", "--uuid", workload_UUID]
    rc, _ = command(kb_cmd, cliargs.dry_run, tmp_directory)
    if rc != 0:
      logger.error("boatload (workload-delete.yml) failed, kube-burner rc: {}".format(rc))
      sys.exit(1)
    cleanup_end_time = time.time()
    logger.info("Cleanup phase complete ({})".format(int(cleanup_end_time * 1000)))

  # Metrics Phase
  if not cliargs.no_metrics_phase:
    metrics_start_time = time.time()
    phase_break()
    logger.info("Metrics phase starting ({})".format(int(metrics_start_time * 1000)))
    phase_break()

    t = Template(workload_metrics)
    workload_metrics_rendered = t.render(
        measurements_index=cliargs.measurements_index,
        indexing=indexing_enabled,
        index_server=cliargs.index_server,
        default_index=cliargs.default_index)

    tmp_directory = tempfile.mkdtemp()
    logger.info("Created {}".format(tmp_directory))
    with open("{}/workload-metrics.yml".format(tmp_directory), "w") as file1:
      file1.writelines(workload_metrics_rendered)
    logger.info("Created {}/workload-metrics.yml".format(tmp_directory))
    metrics_dir = os.path.join(tmp_directory, "metrics")

    shutil.copy2(cliargs.metrics_profile, "{}/metrics.yaml".format(tmp_directory))
    logger.info("Copied {} to {}".format(cliargs.metrics_profile, "{}/metrics.yaml".format(tmp_directory)))

    if not cliargs.no_workload_phase:
      start_time = workload_start_time
    elif not cliargs.no_measurement_phase:
      start_time = measurement_start_time
    else:
      start_time = cleanup_start_time

    if not cliargs.no_cleanup_phase:
      end_time = cleanup_end_time
    elif not cliargs.no_measurement_phase:
      end_time = measurement_end_time
    else:
      end_time = workload_end_time

    kb_cmd = [
        "kube-burner", "index", "-c", "workload-metrics.yml", "--start", str(int(start_time)),
        "--end", str(int(end_time)), "--uuid", workload_UUID, "-u", cliargs.prometheus_url,
        "-m", "{}/metrics.yaml".format(tmp_directory), "-t", cliargs.prometheus_token]
    rc, _ = command(kb_cmd, cliargs.dry_run, tmp_directory, mask_arg=16)
    metrics_end_time = time.time()
    if rc != 0:
      logger.warning("boatload (workload-metrics.yml) failed, kube-burner rc: {}".format(rc))
      # No sys.exit(1) on metrics job error
      logger.info("Metrics phase complete (kube-burner failed) ({})".format(int(metrics_end_time * 1000)))
    else:
      logger.info("Metrics phase complete ({})".format(int(metrics_end_time * 1000)))
    phase_break()

  end_time = time.time()

  # Read in podLatency summary from kube-burner
  kb_measurements = ["PodScheduled", "Initialized", "ContainersReady", "Ready"]
  kb_stats = ["avg", "max", "P50", "P95", "P99"]
  pod_latencies = {}
  for measurement in kb_measurements:
    pod_latencies[measurement] = {}
    for stat in kb_stats:
      pod_latencies[measurement][stat] = 0
  if not cliargs.no_workload_phase and not cliargs.dry_run:
    logger.info("Reading {} for measurement data".format(workload_measurements_json))
    with open(workload_measurements_json) as measurements_file:
      measurements = json.load(measurements_file)
    for measurement in measurements:
      pod_latencies[measurement["quantileName"]] = {}
      for stat in kb_stats:
        pod_latencies[measurement["quantileName"]][stat] = measurement[stat]
  logger.debug("kube-burner podLatency measurements: {}".format(pod_latencies))

  # Read in metrics into metrics csv
  if not cliargs.no_metrics_phase and not cliargs.dry_run:
    metric_collection_start = time.time()
    metrics_data = {}
    logger.info("Collecting metric data for metrics csv")
    for metric in cliargs.metrics:
      metric_json = os.path.join(metrics_dir, "{}-{}.json".format(metric, workload_UUID))
      logger.info("Reading data from {}".format(metric_json))
      try:
        with open(metric_json) as metric_file:
          measurements = json.load(metric_file)
          for measurement in measurements:
            metric_key = metric
            if "instance" in measurement["labels"]:
              metric_key = "{}_{}".format(metric_key, measurement["labels"]["instance"])
            if "node" in measurement["labels"]:
              metric_key = "{}_{}".format(metric_key, measurement["labels"]["node"])
            if "mode" in measurement["labels"]:
              metric_key = "{}_{}".format(metric_key, measurement["labels"]["mode"])
            if "device" in measurement["labels"]:
              metric_key = "{}_{}".format(metric_key, measurement["labels"]["device"])
            if not metric_key in metrics_data.keys():
              metrics_data[metric_key] = {}
              metrics_data[metric_key]["values"] = []
            metrics_data[metric_key]["values"].append(measurement["value"])
      except FileNotFoundError as err:
        logger.warning("Metric file was not found: {}".format(err))
        metrics_data[metric] = {}
        metrics_data[metric]["values"] = []
    # metric data is now collected from the files from kube-burner, now process that data
    for metric in metrics_data:
      logger.debug("Compute values for {}".format(metric))
      if len(metrics_data[metric]["values"]) > 0:
        metrics_data[metric]["len"] = len(metrics_data[metric]["values"])
        metrics_data[metric]["min"] = np.min(metrics_data[metric]["values"])
        metrics_data[metric]["avg"] = np.mean(metrics_data[metric]["values"])
        metrics_data[metric]["max"] = np.max(metrics_data[metric]["values"])
        metrics_data[metric]["P50"] = np.percentile(metrics_data[metric]["values"], 50)
        metrics_data[metric]["P95"] = np.percentile(metrics_data[metric]["values"], 95)
        metrics_data[metric]["P99"] = np.percentile(metrics_data[metric]["values"], 99)
      else:
        metrics_data[metric]["len"] = 0
        metrics_data[metric]["min"] = 0
        metrics_data[metric]["avg"] = 0
        metrics_data[metric]["max"] = 0
        metrics_data[metric]["P50"] = 0
        metrics_data[metric]["P95"] = 0
        metrics_data[metric]["P99"] = 0
      metrics_header.extend(["{}_len".format(metric), "{}_min".format(metric), "{}_avg".format(metric),
          "{}_max".format(metric), "{}_p50".format(metric), "{}_p95".format(metric), "{}_p99".format(metric)])
    logger.info("Completed collecting metric data for csv in: {}".format(round(time.time() - metric_collection_start, 1)))
  phase_break()
  logger.info("boatload Stats")

  workload_duration = 0
  measurement_duration = 0
  cleanup_duration = 0
  metrics_duration = 0

  if flap_links:
    logger.info("* Number of times links flapped down: {}".format(link_flap_count))
  if not cliargs.no_measurement_phase:
    logger.info("* Number of NodeNotReady events reported by node-controller: {}".format(nodenotready_node_controller_count))
    logger.info("* Number of NodeNotReady events reported by kubelet: {}".format(nodenotready_kubelet_count))
    logger.info("* Number of NodeReady events: {}".format(nodeready_count))
    logger.info("* Number of boatload pods marked for deletion (TaintManagerEviction): {}".format(marked_evictions))
    logger.info("* Number of boatload pods killed: {}".format(killed_pod))
    logger.info("* Number of boatload pods started: {}".format(started_pod))
    logger.info("* Number of boatload pods not ready: {}".format(notready_pod))
  if not cliargs.no_workload_phase:
    workload_duration = round(workload_end_time - workload_start_time, 1)
    logger.info("Workload phase duration: {}".format(workload_duration))
  if not cliargs.no_measurement_phase:
    measurement_duration = round(measurement_end_time - measurement_start_time, 1)
    logger.info("Measurement phase duration: {}".format(measurement_duration))
  if not cliargs.no_cleanup_phase:
    cleanup_duration = round(cleanup_end_time - cleanup_start_time, 1)
    logger.info("Cleanup phase duration: {}".format(cleanup_duration))
  if not cliargs.no_metrics_phase:
    metrics_duration = round(metrics_end_time - metrics_start_time, 1)
    logger.info("Metrics phase duration: {}".format(metrics_duration))
  total_time = round(end_time - start_time, 1)
  logger.info("Total duration: {}".format(total_time))
  if not cliargs.no_metrics_phase:
    logger.info("Workload UUID: {}".format(workload_UUID))


  if not cliargs.cleanup:
    # Milliseconds to Seconds * 1000 (For using the timestamp in Grafana, it must be a Unix timestamp in milliseconds)
    results = [int(start_time * 1000), int(workload_end_time * 1000), int(measurement_end_time * 1000),
        int(cleanup_end_time * 1000), int(end_time * 1000), datetime.utcfromtimestamp(start_time),
        datetime.utcfromtimestamp(workload_end_time), datetime.utcfromtimestamp(measurement_end_time),
        datetime.utcfromtimestamp(cleanup_end_time), datetime.utcfromtimestamp(end_time), cliargs.csv_title,
        workload_UUID, workload_duration, measurement_duration, cleanup_duration, metrics_duration, total_time,
        cliargs.namespaces, cliargs.deployments, cliargs.pods, cliargs.containers, int(cliargs.service),
        int(cliargs.route), cliargs.configmaps, cliargs.secrets, int(cliargs.pvcs), cliargs.container_image, cliargs.cpu_requests,
        cliargs.memory_requests, cliargs.cpu_limits, cliargs.memory_limits, cliargs.startup_probe, cliargs.liveness_probe,
        cliargs.readiness_probe, cliargs.shared_selectors, cliargs.unique_selectors, cliargs.tolerations, cliargs.kb_qps,
        cliargs.kb_burst, cliargs.duration, cliargs.interface, cliargs.start_vlan, cliargs.end_vlan, cliargs.latency,
        cliargs.packet_loss, cliargs.bandwidth_limit, cliargs.link_flap_down, cliargs.link_flap_up,
        cliargs.link_flap_firewall, cliargs.link_flap_network, indexing_enabled, cliargs.dry_run, link_flap_count,
        nodenotready_node_controller_count, nodenotready_kubelet_count, nodeready_count, marked_evictions, killed_pod, started_pod, notready_pod]
    for measurement in kb_measurements:
      for stat in kb_stats:
        results.append(pod_latencies[measurement][stat])
    write_csv_results(cliargs.csv_results_file, results)

  if not cliargs.no_metrics_phase and not cliargs.dry_run:
    metrics_csv = [int(start_time * 1000), int(workload_end_time * 1000), int(measurement_end_time * 1000),
        int(cleanup_end_time * 1000), int(end_time * 1000), datetime.utcfromtimestamp(start_time),
        datetime.utcfromtimestamp(workload_end_time), datetime.utcfromtimestamp(measurement_end_time),
        datetime.utcfromtimestamp(cleanup_end_time), datetime.utcfromtimestamp(end_time), cliargs.csv_title,
        workload_UUID]
    for metric in metrics_data:
      metrics_csv.extend([metrics_data[metric]["len"], metrics_data[metric]["min"], metrics_data[metric]["avg"],
          metrics_data[metric]["max"], metrics_data[metric]["P50"], metrics_data[metric]["P95"],
          metrics_data[metric]["P99"]])
    write_csv_metrics(cliargs.csv_metrics_file, metrics_header, metrics_csv)

if __name__ == '__main__':
  sys.exit(main())
