# 环境准备

```
[root@efksvr elk]# ls EFK -Rlh
EFK:
total 4.0K
drwxr-xr-x 2 root root  259 Aug  9 18:37 efk7.17.5
drwxr-xr-x 2 root root   46 Aug  9 18:36 elk-prometheus7.17.5
drwxr-xr-x 2 root root 4.0K Aug  9 18:37 prometheus

EFK/efk7.17.5:
total 667M
-rw-r--r-- 1 root root 294M Aug  9 18:37 elasticsearch-7.17.5-linux-x86_64.tar.gz
-rw-r--r-- 1 root root  34M Aug  9 18:37 filebeat-7.17.5-linux-x86_64.tar.gz
-rw-r--r-- 1 root root  36M Aug  9 18:37 filebeat-7.17.5-linux-x86.tar.gz
-rw-r--r-- 1 root root  27M Aug  9 18:37 filebeat-7.17.5-windows-x86_64.zip
-rw-r--r-- 1 root root  26M Aug  9 18:37 filebeat-7.17.5-windows-x86.zip
-rw-r--r-- 1 root root 252M Aug  9 18:37 kibana-7.17.5-linux-x86_64.tar.gz

EFK/elk-prometheus7.17.5:
total 100K
-rw-r--r-- 1 root root 99K Aug  9 18:36 prometheus-exporter-7.17.5.0.zip

EFK/prometheus:
total 423M
-rw-r--r-- 1 root root  25M Aug  9 18:37 alertmanager-0.24.0.linux-amd64.tar.gz
-rw-r--r-- 1 root root  26M Aug  9 18:37 alertmanager-0.24.0.windows-amd64.zip
-rw-r--r-- 1 root root  11M Aug  9 18:37 blackbox_exporter-0.22.0.linux-amd64.tar.gz
-rw-r--r-- 1 root root  11M Aug  9 18:37 blackbox_exporter-0.22.0.windows-amd64.zip
-rw-r--r-- 1 root root 7.7M Aug  9 18:37 consul_exporter-0.8.0.linux-amd64.tar.gz
-rw-r--r-- 1 root root 7.9M Aug  9 18:37 consul_exporter-0.8.0.windows-amd64.zip
-rw-r--r-- 1 root root  77M Aug  9 18:37 grafana-9.0.6.linux-amd64.tar.gz
-rw-r--r-- 1 root root  14M Aug  9 18:36 graphite_exporter-0.12.3.linux-amd64.tar.gz
-rw-r--r-- 1 root root  13M Aug  9 18:36 graphite_exporter-0.12.3.windows-amd64.zip
-rw-r--r-- 1 root root 7.1M Aug  9 18:36 haproxy_exporter-0.13.0.linux-amd64.tar.gz
-rw-r--r-- 1 root root 7.2M Aug  9 18:36 mysqld_exporter-0.14.0.linux-amd64.tar.gz
-rw-r--r-- 1 root root 7.3M Aug  9 18:36 mysqld_exporter-0.14.0.windows-amd64.zip
-rw-r--r-- 1 root root 8.7M Aug  9 18:36 node_exporter-1.3.1.linux-amd64.tar.gz
-rw-r--r-- 1 root root 9.3M Aug  9 18:36 node_exporter-1.4.0-rc.0.linux-amd64.tar.gz
-rw-r--r-- 1 root root  80M Aug  9 18:36 prometheus-2.37.0.linux-amd64.tar.gz
-rw-r--r-- 1 root root  82M Aug  9 18:36 prometheus-2.37.0.windows-amd64.zip
-rw-r--r-- 1 root root 9.3M Aug  9 18:36 pushgateway-1.4.3.linux-amd64.tar.gz
-rw-r--r-- 1 root root 9.5M Aug  9 18:36 pushgateway-1.4.3.windows-amd64.zip
-rw-r--r-- 1 root root 7.1M Aug  9 18:36 statsd_exporter-0.22.7.linux-amd64.tar.gz
-rw-r--r-- 1 root root 7.3M Aug  9 18:36 statsd_exporter-0.22.7.windows-amd64.zip
[root@efksvr elk]#

[root@efksvr elk]# tail -5  /etc/security/limits.conf

* soft nofile 655360
* hard nofile 655360
* soft noproc 2048
* hard noproc 4096

/*
* soft nofile 65536
* hard nofile 65536
* soft nproc 32000
* hard nproc 32000
* hard memlock unlimited
* soft memlock unlimited

*/

/etc/sysctl.conf文件最后添加一行： vm.max_map_count=655360 添加完毕之后，执行命令： sysctl -p
```



目录规划

```
[root@efksvr elk]# pwd
/elk
[root@efksvr elk]# ll -h
total 0
drwxrwxrwx   5 root       root        49 Aug 10 08:20 data
drwxr-xr-x.  5 root       root        69 Aug  9 18:36 EFK
drwxr-xr-x   9 es         es         155 Jun 24 06:02 elasticsearch-7.17.5
drwxr-xr-x.  7 prometheus prometheus 145 Aug  9 17:36 grafana-9.0.6
drwxr-xr-x  10 es         es         210 Aug  9 18:22 kibana-7.17.5-linux-x86_64
drwxr-xr-x   2 prometheus prometheus  56 Dec  5  2021 node_exporter-1.3.1.linux-amd64
drwxr-xr-x.  4 prometheus prometheus 148 Aug  9 17:26 prometheus-2.37.0.linux-amd64
[root@efksvr elk]# ll -Rh data/
data/:
total 0
drwxr-xr-x  4 es         es         30 Aug  9 18:22 es
drwxr-xr-x. 2 prometheus prometheus  6 Aug 10 08:20 grafana
drwxr-xr-x. 2 prometheus prometheus  6 Aug 10 08:21 prometheus

data/es:
total 0
drwxr-xr-x 2 es es 6 Aug  9 18:22 data
drwxr-xr-x 2 es es 6 Aug  9 18:22 logs

data/es/data:
total 0

data/es/logs:
total 0

data/grafana:
total 0

data/prometheus:
total 0
[root@efksvr elk]#

```



# es

```
[root@efksvr elk]# vi elasticsearch-7.17.5/config/elasticsearch.yml

[root@efksvr elk]# grep -v ^# elasticsearch-7.17.5/config/elasticsearch.yml
cluster.name: ss-efk
node.name: efksvr
path.data: /elk/data/es/data
path.logs: /elk/data/es/logs
network.host: 10.240.22.250
http.port: 9200
cluster.initial_master_nodes: ["efksvr"]

```

- run

  ```
  [root@efksvr elk]# chown es:es -R elasticsearch-7.17.5/
  [root@efksvr elk]# su es
  [es@efksvr elk]$ elasticsearch-7.17.5/bin/elasticsearch
  
  -- su - es -c "/elk/elasticsearch-7.17.5/bin/elasticsearch -d >/dev/null 2>&1"
  ```

- check

  ```
  http://10.240.22.250:9200/
  ```



# kibana

```
[root@efksvr elk]# vi kibana-7.17.5-linux-x86_64/config/kibana.yml
[root@efksvr elk]# grep -v ^# kibana-7.17.5-linux-x86_64/config/kibana.yml
server.port: 5601
server.host: "10.240.22.250"
elasticsearch.hosts: ["http://10.240.22.250:9200"]
i18n.locale: "zh-CN"
```

> 在kibana.yml配置文件中添加一行配置
>
> ```javascript
> i18n.locale: "zh-CN"
> ```
>
>  重启打开后中文的界面

- run

  ```
   su - es -c " /elk/kibana-7.17.5-linux-x86_64/bin/kibana --allow-root > /elk/kibana-7.17.5-linux-x86_64/kibana.log 2>&1 &"
  
  ```

- check

  ```
  http://10.240.22.250:5601/
  ```

# filebeat

```
[root@efksvr elk]# tar zxf EFK/efk7.17.5/filebeat-7.17.5-linux-x86_64.tar.gz -C 


[root@efksvr elk]# vi filebeat-7.17.5-linux-x86_64/filebeat.yml

- type: filestream
  id: syslog
  enabled: true
  paths:
    - /var/log/message
  tags: ["syslog"]

- type: filestream
  id: kibanalog
  enabled: true
  paths:
    - /elk/kibana-7.17.5-linux-x86_64/kibana.log
  tags: ["kibana"]

setup.kibana:
  host: "10.240.22.250:5601"
  
output.elasticsearch:
  hosts: ["10.240.22.250:9200"]


```

- 剔除ipV6地址

  ```
  vim filebeat.yml，在processors中新增script
  - script:
        lang: javascript
        id: remove_ipv6
        source: >
          function process(event) {
              var message = event.Get("host.ip")
              for (var i=0; i<message.length; i++)
              {
                  if(new RegExp(".*\..*\..*\..*").test(message[i]))
                  {
                      event.Put("host.ip",message[i])
                      break;
                  }
              }
          }
  
  ```

  

- run

  ```
  [root@VS-TESTDB01 elk]# nohup filebeat-7.17.5-linux-x86_64/filebeat -c filebeat-7.17.5-linux-x86_64/filebeat.yml >/dev/null 2>&1 &
  ```
  
- 留一个分类的最终yml

  ```
  [root@VS-TESTDB01 filebeat-7.17.5-linux-x86_64]# cat filebeat.yml
  ###################### Filebeat Configuration Example #########################
  
  # This file is an example configuration file highlighting only the most common
  # options. The filebeat.reference.yml file from the same directory contains all the
  # supported options with more comments. You can use it as a reference.
  #
  # You can find the full configuration reference here:
  # https://www.elastic.co/guide/en/beats/filebeat/index.html
  
  # For more available modules and options, please see the filebeat.reference.yml sample
  # configuration file.
  
  # ============================== Filebeat inputs ===============================
  
  filebeat.inputs:
  
  # Each - is an input. Most options can be set at the input level, so
  # you can use different inputs for various configurations.
  # Below are the input specific configurations.
  
  # filestream is an input for collecting log messages from files.
  
  - type: filestream
    id: syslog
    enabled: true
    paths:
      - /var/log/messages
    tags: ["syslog"]
  
  - type: filestream
    id: oracle-testzqf
    enabled: true
    paths:
      - /u01/app/oracle/diag/rdbms/testzqf/TESTZQF/trace/alert_TESTZQF.log
    tags: ["TESTZQF"]
  
  - type: filestream
    id: oracle-kkmgn
    enabled: true
    paths:
      - /u01/app/oracle/diag/rdbms/kkmgn/kkmgn/trace/alert_kkmgn.log
    tags: ["kkmgn"]
  
    # Exclude lines. A list of regular expressions to match. It drops the lines that are
    # matching any regular expression from the list.
    #exclude_lines: ['^DBG']
  
    # Include lines. A list of regular expressions to match. It exports the lines that are
    # matching any regular expression from the list.
    #include_lines: ['^ERR', '^WARN']
  
    # Exclude files. A list of regular expressions to match. Filebeat drops the files that
    # are matching any regular expression from the list. By default, no files are dropped.
    #prospector.scanner.exclude_files: ['.gz$']
  
    # Optional additional fields. These fields can be freely picked
    # to add additional information to the crawled log files for filtering
    #fields:
    #  level: debug
    #  review: 1
  
  # ============================== Filebeat modules ==============================
  
  filebeat.config.modules:
    # Glob pattern for configuration loading
    path: ${path.config}/modules.d/*.yml
  
    # Set to true to enable config reloading
    reload.enabled: false
  
    # Period on which files under path should be checked for changes
    #reload.period: 10s
  
  # ======================= Elasticsearch template setting =======================
  
  setup.template.settings:
    index.number_of_shards: 1
    #index.codec: best_compression
    #_source.enabled: false
  
  
  # ================================== General ===================================
  
  # The name of the shipper that publishes the network data. It can be used to group
  # all the transactions sent by a single shipper in the web interface.
  #name:
  
  # The tags of the shipper are included in their own field with each
  # transaction published.
  #tags: ["service-X", "web-tier"]
  
  # Optional fields that you can specify to add additional information to the
  # output.
  #fields:
  #  env: staging
  
  # ================================= Dashboards =================================
  # These settings control loading the sample dashboards to the Kibana index. Loading
  # the dashboards is disabled by default and can be enabled either by setting the
  # options here or by using the `setup` command.
  #setup.dashboards.enabled: false
  
  # The URL from where to download the dashboards archive. By default this URL
  # has a value which is computed based on the Beat name and version. For released
  # versions, this URL points to the dashboard archive on the artifacts.elastic.co
  # website.
  #setup.dashboards.url:
  
  # =================================== Kibana ===================================
  
  # Starting with Beats version 6.0.0, the dashboards are loaded via the Kibana API.
  # This requires a Kibana endpoint configuration.
  setup.kibana:
  
    # Kibana Host
    # Scheme and port can be left out and will be set to the default (http and 5601)
    # In case you specify and additional path, the scheme is required: http://localhost:5601/path
    # IPv6 addresses should always be defined as: https://[2001:db8::1]:5601
    host: "10.240.22.250:5601"
  
    # Kibana Space ID
    # ID of the Kibana Space into which the dashboards should be loaded. By default,
    # the Default Space will be used.
    #space.id:
  
  # =============================== Elastic Cloud ================================
  
  # These settings simplify using Filebeat with the Elastic Cloud (https://cloud.elastic.co/).
  
  # The cloud.id setting overwrites the `output.elasticsearch.hosts` and
  # `setup.kibana.host` options.
  # You can find the `cloud.id` in the Elastic Cloud web UI.
  #cloud.id:
  
  # The cloud.auth setting overwrites the `output.elasticsearch.username` and
  # `output.elasticsearch.password` settings. The format is `<user>:<pass>`.
  #cloud.auth:
  
  # ================================== Outputs ===================================
  
  # Configure what output to use when sending the data collected by the beat.
  
  # ---------------------------- Elasticsearch Output ----------------------------
  output.elasticsearch:
    # Array of hosts to connect to.
    hosts: ["10.240.22.250:9200"]
  
    # Protocol - either `http` (default) or `https`.
    #protocol: "https"
  
    # Authentication credentials - either API key or username/password.
    #api_key: "id:api_key"
    #username: "elastic"
    #password: "changeme"
  
  # ================================= Processors =================================
  processors:
    - add_host_metadata:
        when.not.contains.tags: forwarded
    - add_cloud_metadata: ~
    - add_docker_metadata: ~
    - add_kubernetes_metadata: ~
    - script:
        lang: javascript
        id: remove_ipv6
        source: >
          function process(event) {
              var message = event.Get("host.ip")
              for (var i=0; i<message.length; i++)
              {
                  if(new RegExp(".*\..*\..*\..*").test(message[i]))
                  {
                      event.Put("host.ip",message[i])
                      break;
                  }
              }
          }
  
  # ================================== Logging ===================================
  
  # Sets log level. The default log level is info.
  # Available log levels are: error, warning, info, debug
  #logging.level: debug
  
  # At debug level, you can selectively enable logging only for some components.
  # To enable all selectors use ["*"]. Examples of other selectors are "beat",
  # "publisher", "service".
  #logging.selectors: ["*"]
  
  # ============================= X-Pack Monitoring ==============================
  # Filebeat can export internal metrics to a central Elasticsearch monitoring
  # cluster.  This requires xpack monitoring to be enabled in Elasticsearch.  The
  # reporting is disabled by default.
  
  # Set to true to enable the monitoring reporter.
  #monitoring.enabled: false
  
  # Sets the UUID of the Elasticsearch cluster under which monitoring data for this
  # Filebeat instance will appear in the Stack Monitoring UI. If output.elasticsearch
  # is enabled, the UUID is derived from the Elasticsearch cluster referenced by output.elasticsearch.
  #monitoring.cluster_uuid:
  
  # Uncomment to send the metrics to Elasticsearch. Most settings from the
  # Elasticsearch output are accepted here as well.
  # Note that the settings should point to your Elasticsearch *monitoring* cluster.
  # Any setting that is not set is automatically inherited from the Elasticsearch
  # output configuration, so if you have the Elasticsearch output configured such
  # that it is pointing to your Elasticsearch monitoring cluster, you can simply
  # uncomment the following line.
  #monitoring.elasticsearch:
  
  # ============================== Instrumentation ===============================
  
  # Instrumentation support for the filebeat.
  #instrumentation:
      # Set to true to enable instrumentation of filebeat.
      #enabled: false
  
      # Environment in which filebeat is running on (eg: staging, production, etc.)
      #environment: ""
  
      # APM Server hosts to report instrumentation results to.
      #hosts:
      #  - http://localhost:8200
  
      # API Key for the APM Server(s).
      # If api_key is set then secret_token will be ignored.
      #api_key:
  
      # Secret token for the APM Server(s).
      #secret_token:
  
  
  # ================================= Migration ==================================
  
  # This allows to enable 6.7 migration aliases
  #migration.6_to_7.enabled: true
  
  
  ```

  

# prometheus

```
配置文件没什么可改的。
直接在启动命令里指定数据存放目录就好。
注意权限

nohup /elk/prometheus-2.37.0.linux-amd64/prometheus --config.file=/elk/prometheus-2.37.0.linux-amd64/prometheus.yml --web.enable-admin-api --web.listen-address=:9090 --storage.tsdb.path=/elk/data/prometheus >/dev/null 2>&1 &

```

- check

  ```
  http://10.240.22.250:9090/targets
  ```

  

# node_exporter

```
解压
 nohup /elk/node_exporter-1.3.1.linux-amd64/node_exporter  > /dev/null 2>&1 &
```

- check

  ```
  http://10.240.22.250:9100/
  --> ok.
  ```

- startup

  ```
  #!/bin/bash
  # if node_exporter is not in process list, then auto execute it.
  ps -ef|grep node_exporter | grep -v grep
  
  if [ $? -ne 0 ] ;then
  	nohup /opt/node_exporter-1.3.1.linux-amd64/node_exporter  > /dev/null 2>&1 &
  fi
  
  
  # nohup /opt/node_exporter-1.3.1.linux-amd64/node_exporter  > /dev/null 2>&1 &
  
  ```

  

- 将node加入Prometheus监控

  ```
  [root@efksvr elk]# vi prometheus-2.37.0.linux-amd64/prometheus.yml  
    - job_name: "node_exporter"
      static_configs:
        - targets: ["localhost:9100"]
  
  ```

  > ```
  > [root@efksvr elk]# vi prometheus-2.37.0.linux-amd64/prometheus.yml
  > # my global config
  > # storage.tsdb.path="data/"
  > global:
  >   scrape_interval: 15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  >   evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  >   # scrape_timeout is set to the global default (10s).
  > 
  > # Alertmanager configuration
  > alerting:
  >   alertmanagers:
  >     - static_configs:
  >         - targets:
  >           # - alertmanager:9093
  > 
  > # Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
  > rule_files:
  >   # - "first_rules.yml"
  >   # - "second_rules.yml"
  > 
  > # A scrape configuration containing exactly one endpoint to scrape:
  > # Here it's Prometheus itself.
  > scrape_configs:
  >   # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  >   - job_name: "prometheus"
  > 
  >     # metrics_path defaults to '/metrics'
  >     # scheme defaults to 'http'.
  > 
  >     static_configs:
  >       - targets: ["localhost:9090"]
  > 
  >   - job_name: "node_exporter"
  >     static_configs:
  >       - targets: ["localhost:9100"]
  > 
  > ```
  >
  > 

- 重启prometheus

  ```
  http://10.240.22.250:9090/targets
  node up 1/1 --> ok.
  then->
  ```

  

# grafana

```
解压
创建custom.ini的配置文件，以覆盖conf/defaults.ini中定义的任何设置

[paths]
data = /elk/data/grafana
temp_data_lifetime = 24h
logs = /elk/data/grafana/log
plugins = /elk/data/grafana/plugins
provisioning = /elk/data/grafana/conf/provisioning

```

- run

  ```
  [root@efksvr elk]# cat startgrafana.sh
   cd /elk/grafana-9.0.6
   nohup ./bin/grafana-server >/dev/null 2>&1 &
  
  ```

- check

  ```
  http://10.240.22.250:3000/
   初始密码admin/admin
  ```

- 配置数据源

  > configuartion -> data source -> add data source -> prometheus
  >
  > -> URL : http://10.240.22.250:9090 -> save&test

- 导入dashboard

  > 可在官方模板https://grafana.com/grafana/dashboards，查看模板编号，也可以下载后导入。比如我这里选择import，输入模板编号为8919 12633
  >
  > -> +import -> 12633 ->load -> select prometheus data source -> import



# 打通Prometheus和EFK

elasticsearch-prometheus-exporter ,用来使Prometheus监控elk/efk。

- 在es的机器上安装插件。

  > 选择对应的elk版本进行下载，将其解压后存放在/usr/share/elasticsearch/plugins目录下，下载的安装包解压后存在plugin-descriptor.properties才能正确安装，安装好以后重启elasticsearch
  >
  > 配置prometheus的配置文件
  >
  > 添加如下配置：
  >
  > ```
  > - job_name: 'elasticsearch'
  >     metrics_path: "/_prometheus/metrics"
  >     static_configs:
  >     - targets:[ '10.240.22.250:9200']
  > ```
  >
  > 其中job_name随便定义，如果已经对接grafana，可以去grafana官网下载对应的json模板。

  ```
  [root@efksvr elk]# cd elasticsearch-7.17.5/plugins/
  
  [root@efksvr plugins]# ll -d
  drwxr-xr-x 2 es es 6 Jun 24 05:59 .
  
  [root@efksvr plugins]# mkdir prometheus-exporter
  
  [root@efksvr plugins]# cd prometheus-exporter
  
  [root@efksvr prometheus-exporter]# ls /elk/EFK/elk-prometheus7.17.5/prometheus-exporter-7.17.5.0.zip
  /elk/EFK/elk-prometheus7.17.5/prometheus-exporter-7.17.5.0.zip
  
  [root@efksvr prometheus-exporter]# unzip !$ -d .
  unzip /elk/EFK/elk-prometheus7.17.5/prometheus-exporter-7.17.5.0.zip -d .
  Archive:  /elk/EFK/elk-prometheus7.17.5/prometheus-exporter-7.17.5.0.zip
    inflating: ./plugin-descriptor.properties
    inflating: ./prometheus-exporter-7.17.5.0.jar
    inflating: ./simpleclient_common-0.8.0.jar
    inflating: ./simpleclient-0.8.0.jar
    inflating: ./plugin-security.policy
    
  [root@efksvr prometheus-exporter]# ls
  plugin-descriptor.properties  prometheus-exporter-7.17.5.0.jar  simpleclient_common-0.8.0.jar
  plugin-security.policy        simpleclient-0.8.0.jar
  
  [root@efksvr prometheus-exporter]# cd ..
  
  [root@efksvr plugins]# chown es:es -R prometheus-exporter
  
  # 安装好以后重启elasticsearch
  ```

- 配置prometheus的配置文件

  ```
  # 添加如下配置
  - job_name: 'elasticsearch'
      metrics_path: "/_prometheus/metrics"
      static_configs:
      - targets:[ '10.240.22.250:9200']
  ```

  > ```
  > cat prometheus-2.37.0.linux-amd64/prometheus.yml
  > # my global config
  > # storage.tsdb.path="data/"
  > global:
  >   scrape_interval: 15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  >   evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  >   # scrape_timeout is set to the global default (10s).
  > 
  > # Alertmanager configuration
  > alerting:
  >   alertmanagers:
  >     - static_configs:
  >         - targets:
  >           # - alertmanager:9093
  > 
  > # Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
  > rule_files:
  >   # - "first_rules.yml"
  >   # - "second_rules.yml"
  > 
  > # A scrape configuration containing exactly one endpoint to scrape:
  > # Here it's Prometheus itself.
  > scrape_configs:
  >   # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  >   - job_name: "prometheus"
  > 
  >     # metrics_path defaults to '/metrics'
  >     # scheme defaults to 'http'.
  > 
  >     static_configs:
  >       - targets: ["localhost:9090"]
  > 
  >   - job_name: "node_exporter"
  >     static_configs:
  >       - targets: ["localhost:9100"]
  > 
  >   - job_name: 'elasticsearch'
  >     metrics_path: "/_prometheus/metrics"
  >     static_configs:
  >       - targets: ["10.240.22.250:9200"]
  > 
  > [root@efksvr elk]#
  > 
  > ```
  >
  > 

- check

  ```
  http://10.240.22.250:9200/_prometheus/metrics
  ```

- 重启Prometheus

  ```
  http://10.240.22.250:9090/targets
  -> elasticsearch 1/1 up
  -> node_exporter 1/1 up
  -> prometheus    1/1 up
  --> ok.
  ```

- grafana

  ```
  -> +import -> 266 -> load
  ```

  



# 入口

- es-kibana

  ```
  http://10.240.22.250:5601/
  ```

- prometheus

  ```
  http://10.240.22.250:9090/targets
  ```

- es data

  ```
  http://10.240.22.250:9200/
  ```

- grafana

  ```
  http://10.240.22.250:3000/
  ```

  



# oracle_exporter

- 在oracle database server 上安装 oracle_exporter

  ```
  [oracle@VS-TESTDB01 oracledb_exporter.0.3.0rc1-ora18.5.linux-amd64]$ cat start.sh
  export ORACLE_SID=TESTZQF
  export DATA_SOURCE_NAME=${USERNAME}/${PASSWORD}
  ./oracledb_exporter
  
  ```

- 使用oracle用户运行

- libclntsh.so.18.1 问题

  ```
  cd /u01/app/oracle/product/12.1.0/dbhome_1/lib/
  $ ln -s libclntsh.so libclntsh.so.18.1
  $ ls libclntsh.so.* -l
  lrwxrwxrwx. 1 oracle oinstall       12 Aug 25  2020 libclntsh.so.10.1 -> libclntsh.so
  lrwxrwxrwx. 1 oracle oinstall       12 Aug 25  2020 libclntsh.so.11.1 -> libclntsh.so
  -rwxr-xr-x. 1 oracle oinstall 55452679 Aug 25  2020 libclntsh.so.12.1
  lrwxrwxrwx  1 oracle oinstall       12 Aug 10 14:09 libclntsh.so.18.1 -> libclntsh.so
  
  ```

- check

  ```
  oracle_exporter 机器的9161 端口访问
  ```

  

- 将job添加到Prometheus.yml 中， 重启Prometheus

  ```
  ######################## Oracle监控 ##########################
    - job_name: 'oracle'
      metrics_path: '/metrics'
      static_configs:
      - targets: ['xxx.xxx.xxx.xxx:9161']
  ```

- 指定端口

  ```
  oracledb_exporter --log.level error --web.listen-address 0.0.0.0:9161
  ```

  > ```
  > Usage of oracledb_exporter:
  >   --log.format value
  >        	If set use a syslog logger or JSON logging. Example: logger:syslog?appname=bob&local=7 or logger:stdout?json=true. Defaults to stderr.
  >   --log.level value
  >        	Only log messages with the given severity or above. Valid levels: [debug, info, warn, error, fatal].
  >   --custom.metrics string
  >         File that may contain various custom metrics in a TOML file.
  >   --default.metrics string
  >         Default TOML file metrics.
  >   --web.listen-address string
  >        	Address to listen on for web interface and telemetry. (default ":9161")
  >   --web.telemetry-path string
  >        	Path under which to expose metrics. (default "/metrics")
  >   --database.maxIdleConns string
  >         Number of maximum idle connections in the connection pool. (default "0")
  >   --database.maxOpenConns string
  >         Number of maximum open connections in the connection pool. (default "10")
  >   --web.secured-metrics  boolean
  >         Expose metrics using https server. (default "false")
  >   --web.ssl-server-cert string
  >         Path to the PEM encoded certificate file.
  >   --web.ssl-server-key string
  >         Path to the PEM encoded key file.
  > ```

- oracledb_export startup.sh

  - 一个节点多个实例的情况下

    ```
    #!/bin/bash
    # for auto start oracledb_exporter of prometheus. Aug 10,2022 by kk
    source /home/oracle/.bash_profile
    
    if [ ! -f  "${ORACLE_HOME}/lib/libclntsh.so.18.1" ] ;then
            cd $ORACLE_HOME/lib && ln -s libclntsh.so libclntsh.so.18.1
            else
            echo "libclntsh.so.18.1 has been already exists."
    fi
    
    
    ps -ef|grep oracledb_exporter | grep -v grep
    
    if [ $? -ne 0 ] ;then
    	export LD_LIBRARY_PATH=$ORACLE_HOME/lib:/lib:/usr/lib
    	export DATA_SOURCE_NAME=zabbix2019/pwdorabbix_udontknow
    
    	script_dir=$(cd $(dirname $0);pwd)
    	cd $script_dir
    
    	export ORACLE_SID=SSDB2
    	nohup ./oracledb_exporter --log.level error --web.listen-address 0.0.0.0:9161 > ${ORACLE_SID}_log 2>&1 &
    
    	export ORACLE_SID=CENDB2
    	nohup ./oracledb_exporter --log.level error --web.listen-address 0.0.0.0:9162 > ${ORACLE_SID}_log 2>&1 &
    
    	export ORACLE_SID=FMDB2
    	nohup ./oracledb_exporter --log.level error --web.listen-address 0.0.0.0:9163 > ${ORACLE_SID}_log 2>&1 &
    
    	# end
    	ps -ef|grep oracledb
    	sleep 5
    	ps -ef|grep oracledb
    fi
    
    #echo $0
    #script_dir=$(cd $(dirname $0);pwd)
    #echo $script_dir
    
    ```

    