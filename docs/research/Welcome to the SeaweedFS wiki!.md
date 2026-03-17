---
source_url: https://github.com/seaweedfs/seaweedfs/wiki
retrieved_at_utc: 2026-03-17T01:22:37.843388+00:00
title: Home · seaweedfs/seaweedfs Wiki · GitHub
slug: github_com-wiki
scrape_method: html_fragment
raw_markdown_url: 
prefer_raw_markdown: true
polished: true
localized_images: true
generator_mcp_server: mcp_server_page_scraper.py
---

# Home · seaweedfs/seaweedfs Wiki · GitHub

Source: https://github.com/seaweedfs/seaweedfs/wiki
[seaweedfs](https://github.com/seaweedfs)
 /

 [seaweedfs](https://github.com/seaweedfs/seaweedfs)

 Public

 - ### Uh oh! There was an error while loading. Please reload this page.

 - [Notifications](https://github.com/login?return_to=%2Fseaweedfs%2Fseaweedfs) You must be signed in to change notification settings

 - [Fork 2.8k](https://github.com/login?return_to=%2Fseaweedfs%2Fseaweedfs)

 - [Star 31k](https://github.com/login?return_to=%2Fseaweedfs%2Fseaweedfs)

 - [Code](https://github.com/seaweedfs/seaweedfs)

 - [Issues 627](https://github.com/seaweedfs/seaweedfs/issues)

 - [Pull requests 83](https://github.com/seaweedfs/seaweedfs/pulls)

 - [Discussions](https://github.com/seaweedfs/seaweedfs/discussions)

 - [Actions](https://github.com/seaweedfs/seaweedfs/actions)

 - [Projects](https://github.com/seaweedfs/seaweedfs/projects)

 - [Wiki](https://github.com/seaweedfs/seaweedfs/wiki)

 - [Security 0](https://github.com/seaweedfs/seaweedfs/security)

 - [Insights](https://github.com/seaweedfs/seaweedfs/pulse)

Additional navigation options

 - [Code](https://github.com/seaweedfs/seaweedfs)

 - [Issues](https://github.com/seaweedfs/seaweedfs/issues)

 - [Pull requests](https://github.com/seaweedfs/seaweedfs/pulls)

 - [Discussions](https://github.com/seaweedfs/seaweedfs/discussions)

 - [Actions](https://github.com/seaweedfs/seaweedfs/actions)

 - [Projects](https://github.com/seaweedfs/seaweedfs/projects)

 - [Wiki](https://github.com/seaweedfs/seaweedfs/wiki)

 - [Security](https://github.com/seaweedfs/seaweedfs/security)

 - [Insights](https://github.com/seaweedfs/seaweedfs/pulse)

# Home

 [Jump to bottom](https://github.com/seaweedfs/seaweedfs/wiki#wiki-pages-box)

 [Edit](https://github.com/seaweedfs/seaweedfs/wiki/Home/_edit)

 [New page](https://github.com/seaweedfs/seaweedfs/wiki/_new)

 Nathan Hurst edited this page Feb 3, 2024
 ·
 [37 revisions](https://github.com/seaweedfs/seaweedfs/wiki/Home/_history)

# Welcome to the SeaweedFS wiki!
[#welcome-to-the-seaweedfs-wiki](https://github.com/seaweedfs/seaweedfs/wiki#welcome-to-the-seaweedfs-wiki)

SeaweedFS is a versatile and efficient storage system designed to meet the needs of modern sysadmins managing a mix of blob, object, file, and data warehouse storage requirements. Its architecture guarantees fast access times, with constant-time (O(1)) disk seeks, regardless of the size of the dataset. This makes it an excellent choice for environments where speed and efficiency are critical.

SeaweedFS is organized into several layers, each serving a different storage need:

- Blob Storage is the foundation, comprising master servers, volume servers, and a cloud tier for infinite scalability.

- File Storage builds on Blob Storage by adding filer servers for managing filesystem-like operations.

- Object Storage extends File Storage with S3-compatible servers, making it a breeze to integrate with existing S3 workflows.

- Data Warehouse capabilities are integrated into File Storage, offering compatibility with big data frameworks like Hadoop, Spark, and Flink, through Hadoop-compatible libraries.

- FUSE Mount allows File Storage to be directly mounted in user space on clients, supporting common use cases like FUSE mounts and Kubernetes persistent volumes.

SeaweedFS stands out for its high performance, scalability, and flexibility. It features:

- Fast key-to-file mapping with minimal disk seek time.

- Customizable tiered storage that intelligently places data based on activity, moving less active data to cheaper cloud storage.

- Elastic scalability, easily expanding capacity by adding volume servers.

- A robust, high-performance, S3-compatible object store that can serve as an in-house alternative to HDFS.

The system is designed for high availability and durability, with features like:

- No single point of failure (SPOF), supporting active-active asynchronous replication and erasure coding for data protection.

- Support for file checksums to ensure data integrity.

- Rack and data center aware replication to enhance reliability.

- Flexible metadata management, compatible with a variety of popular databases and storage systems.

For sysadmins, SeaweedFS simplifies operations significantly. Adding capacity is as straightforward as integrating more volume servers. The system's architecture allows for easy data migration and backup, supporting a wide array of backend stores for metadata. This makes SeaweedFS an adaptable and reliable choice for managing diverse and demanding storage environments.

Here is the white paper for [SeaweedFS Architecture.pdf](https://github.com/seaweedfs/seaweedfs/wiki/SeaweedFS_Architecture.pdf)

### Roadmap
[#roadmap](https://github.com/seaweedfs/seaweedfs/wiki#roadmap)

- [Getting Started](https://github.com/seaweedfs/seaweedfs/wiki/Getting-Started): If you are a user wanting to try out SeaweedFS.

- [Production Setup](https://github.com/seaweedfs/seaweedfs/wiki/Production-Setup): this lays out a more serious configuration designed for large volumes of traffic and high relability.

- [Components](https://github.com/seaweedfs/seaweedfs/wiki/Components): How the services fit together.

- [Benchmarks](https://github.com/seaweedfs/seaweedfs/wiki/Benchmarks): the measured performance of SeaweedFS.

- [FAQ](https://github.com/seaweedfs/seaweedfs/wiki/FAQ): things we should work to include in the main documentation.

- [Applications](https://github.com/seaweedfs/seaweedfs/wiki/Applications), [Use-Cases](https://github.com/seaweedfs/seaweedfs/wiki/Use-Cases) and [Actual-Users](https://github.com/seaweedfs/seaweedfs/wiki/Actual-Users): inspiration and ideas for how you might use SeaweedFS.

![SeaweedFS Architecture](github_com-wiki-images/SeaweedFS_Architecture_png)

![SeaweedFS Remote Storage](github_com-wiki-images/SeaweedFS_RemoteMount_png)

 [Add a custom footer](https://github.com/seaweedfs/seaweedfs/wiki/_new?wiki%5Bname%5D=_Footer)

## Toggle table of contents Pages 142

 - Loading [Home](https://github.com/seaweedfs/seaweedfs/wiki) [Welcome to the SeaweedFS wiki!](https://github.com/seaweedfs/seaweedfs/wiki#welcome-to-the-seaweedfs-wiki)

 - [Roadmap](https://github.com/seaweedfs/seaweedfs/wiki#roadmap)

 - Loading [Actual Users](https://github.com/seaweedfs/seaweedfs/wiki/Actual-Users) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Admin UI](https://github.com/seaweedfs/seaweedfs/wiki/Admin-UI) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Amazon IAM API](https://github.com/seaweedfs/seaweedfs/wiki/Amazon-IAM-API) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Amazon S3 API](https://github.com/seaweedfs/seaweedfs/wiki/Amazon-S3-API) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Applications](https://github.com/seaweedfs/seaweedfs/wiki/Applications) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Async Backup](https://github.com/seaweedfs/seaweedfs/wiki/Async-Backup) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Async Filer Metadata Backup](https://github.com/seaweedfs/seaweedfs/wiki/Async-Filer-Metadata-Backup) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Async Replication to another Filer](https://github.com/seaweedfs/seaweedfs/wiki/Async-Replication-to-another-Filer) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Async Replication to Cloud](https://github.com/seaweedfs/seaweedfs/wiki/Async-Replication-to-Cloud) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [AWS CLI with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/AWS-CLI-with-SeaweedFS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [AWS IAM CLI](https://github.com/seaweedfs/seaweedfs/wiki/AWS-IAM-CLI) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Benchmark SeaweedFS as a GlusterFS replacement](https://github.com/seaweedfs/seaweedfs/wiki/Benchmark-SeaweedFS-as-a-GlusterFS-replacement) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Benchmarks](https://github.com/seaweedfs/seaweedfs/wiki/Benchmarks) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Benchmarks from jinleileiking](https://github.com/seaweedfs/seaweedfs/wiki/Benchmarks-from-jinleileiking) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Cache Remote Storage](https://github.com/seaweedfs/seaweedfs/wiki/Cache-Remote-Storage) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Choosing a Filer Store](https://github.com/seaweedfs/seaweedfs/wiki/Choosing-a-Filer-Store) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Client Libraries](https://github.com/seaweedfs/seaweedfs/wiki/Client-Libraries) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Cloud Drive Architecture](https://github.com/seaweedfs/seaweedfs/wiki/Cloud-Drive-Architecture) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Cloud Drive Benefits](https://github.com/seaweedfs/seaweedfs/wiki/Cloud-Drive-Benefits) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Cloud Drive Quick Setup](https://github.com/seaweedfs/seaweedfs/wiki/Cloud-Drive-Quick-Setup) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Cloud Monitoring](https://github.com/seaweedfs/seaweedfs/wiki/Cloud-Monitoring) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Cloud Tier](https://github.com/seaweedfs/seaweedfs/wiki/Cloud-Tier) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Components](https://github.com/seaweedfs/seaweedfs/wiki/Components) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Configure Remote Storage](https://github.com/seaweedfs/seaweedfs/wiki/Configure-Remote-Storage) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Cryptography and FIPS Compliance](https://github.com/seaweedfs/seaweedfs/wiki/Cryptography-and-FIPS-Compliance) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Customize Filer Store](https://github.com/seaweedfs/seaweedfs/wiki/Customize-Filer-Store) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Data Backup](https://github.com/seaweedfs/seaweedfs/wiki/Data-Backup) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Data Structure for Large Files](https://github.com/seaweedfs/seaweedfs/wiki/Data-Structure-for-Large-Files) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Deployment to Kubernetes and Minikube](https://github.com/seaweedfs/seaweedfs/wiki/Deployment-to-Kubernetes-and-Minikube) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Directories and Files](https://github.com/seaweedfs/seaweedfs/wiki/Directories-and-Files) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Docker Compose for S3](https://github.com/seaweedfs/seaweedfs/wiki/Docker-Compose-for-S3) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Docker Image Registry with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/Docker-Image-Registry-with-SeaweedFS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Environment Variables](https://github.com/seaweedfs/seaweedfs/wiki/Environment-Variables) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Erasure Coding for warm storage](https://github.com/seaweedfs/seaweedfs/wiki/Erasure-Coding-for-warm-storage) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Error reporting to sentry](https://github.com/seaweedfs/seaweedfs/wiki/Error-reporting-to-sentry) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Failover Master Server](https://github.com/seaweedfs/seaweedfs/wiki/Failover-Master-Server) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [FAQ](https://github.com/seaweedfs/seaweedfs/wiki/FAQ) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [File Operations Quick Reference](https://github.com/seaweedfs/seaweedfs/wiki/File-Operations-Quick-Reference) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Active Active cross cluster continuous synchronization](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Active-Active-cross-cluster-continuous-synchronization) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer as a Key Large Value Store](https://github.com/seaweedfs/seaweedfs/wiki/Filer-as-a-Key-Large-Value-Store) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Cassandra Setup](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Cassandra-Setup) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Change Data Capture](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Change-Data-Capture) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Commands and Operations](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Commands-and-Operations) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Data Encryption](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Data-Encryption) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer JWT Use](https://github.com/seaweedfs/seaweedfs/wiki/Filer-JWT-Use) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Metadata Events](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Metadata-Events) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Notification Webhook](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Notification-Webhook) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Redis Setup](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Redis-Setup) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Server API](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Server-API) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Setup](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Setup) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Store Replication](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Store-Replication) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Filer Stores](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Stores) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [FIO benchmark](https://github.com/seaweedfs/seaweedfs/wiki/FIO-benchmark) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [fstab](https://github.com/seaweedfs/seaweedfs/wiki/fstab) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [FUSE Mount](https://github.com/seaweedfs/seaweedfs/wiki/FUSE-Mount) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Gateway to Remote Object Storage](https://github.com/seaweedfs/seaweedfs/wiki/Gateway-to-Remote-Object-Storage) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Getting Started](https://github.com/seaweedfs/seaweedfs/wiki/Getting-Started) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Hadoop Benchmark](https://github.com/seaweedfs/seaweedfs/wiki/Hadoop-Benchmark) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Hadoop Compatible File System](https://github.com/seaweedfs/seaweedfs/wiki/Hadoop-Compatible-File-System) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Hardware](https://github.com/seaweedfs/seaweedfs/wiki/Hardware) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [HDFS via S3 connector](https://github.com/seaweedfs/seaweedfs/wiki/HDFS-via-S3-connector) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Hobbyest Tinkerer scale on premises tutorial](https://github.com/seaweedfs/seaweedfs/wiki/Hobbyest-Tinkerer-scale-on-premises-tutorial) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Iceberg Table Maintenance](https://github.com/seaweedfs/seaweedfs/wiki/Iceberg-Table-Maintenance) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Independent Benchmarks](https://github.com/seaweedfs/seaweedfs/wiki/Independent-Benchmarks) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Kafka to Kafka Gateway to SMQ to SQL](https://github.com/seaweedfs/seaweedfs/wiki/Kafka-to-Kafka-Gateway-to-SMQ-to-SQL) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Kubernetes Backups and Recovery with K8up](https://github.com/seaweedfs/seaweedfs/wiki/Kubernetes-Backups-and-Recovery-with-K8up) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Large File Handling](https://github.com/seaweedfs/seaweedfs/wiki/Large-File-Handling) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Load Command Line Options from a file](https://github.com/seaweedfs/seaweedfs/wiki/Load-Command-Line-Options-from-a-file) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Master Server API](https://github.com/seaweedfs/seaweedfs/wiki/Master-Server-API) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Migrate Maintenance Scripts to Admin Script Plugin](https://github.com/seaweedfs/seaweedfs/wiki/Migrate-Maintenance-Scripts-to-Admin-Script-Plugin) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Migrate to Filer Store](https://github.com/seaweedfs/seaweedfs/wiki/Migrate-to-Filer-Store) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Mount Remote Storage](https://github.com/seaweedfs/seaweedfs/wiki/Mount-Remote-Storage) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [nodejs with Seaweed S3](https://github.com/seaweedfs/seaweedfs/wiki/nodejs-with-Seaweed-S3) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [OIDC Integration](https://github.com/seaweedfs/seaweedfs/wiki/OIDC-Integration) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Optimization](https://github.com/seaweedfs/seaweedfs/wiki/Optimization) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Optimization for Many Small Buckets](https://github.com/seaweedfs/seaweedfs/wiki/Optimization-for-Many-Small-Buckets) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Path Specific Configuration](https://github.com/seaweedfs/seaweedfs/wiki/Path-Specific-Configuration) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Path Specific Filer Store](https://github.com/seaweedfs/seaweedfs/wiki/Path-Specific-Filer-Store) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Plugin Worker Scheduling](https://github.com/seaweedfs/seaweedfs/wiki/Plugin-Worker-Scheduling) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [PostgreSQL compatible Server weed db](https://github.com/seaweedfs/seaweedfs/wiki/PostgreSQL-compatible-Server-weed-db) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Production Setup](https://github.com/seaweedfs/seaweedfs/wiki/Production-Setup) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Pub Sub to SMQ to SQL](https://github.com/seaweedfs/seaweedfs/wiki/Pub-Sub-to-SMQ-to-SQL) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Quick Start with weed mini](https://github.com/seaweedfs/seaweedfs/wiki/Quick-Start-with-weed-mini) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [rclone with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/rclone-with-SeaweedFS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Replication](https://github.com/seaweedfs/seaweedfs/wiki/Replication) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [restic with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/restic-with-SeaweedFS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Run Blob Storage on Public Internet](https://github.com/seaweedfs/seaweedfs/wiki/Run-Blob-Storage-on-Public-Internet) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [run HBase on SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/run-HBase-on-SeaweedFS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Run Presto on SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/Run-Presto-on-SeaweedFS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [run Spark on SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/run-Spark-on-SeaweedFS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Rust Volume Server](https://github.com/seaweedfs/seaweedfs/wiki/Rust-Volume-Server) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 API Audit log](https://github.com/seaweedfs/seaweedfs/wiki/S3-API-Audit-log) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 API Benchmark](https://github.com/seaweedfs/seaweedfs/wiki/S3-API-Benchmark) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 API FAQ](https://github.com/seaweedfs/seaweedfs/wiki/S3-API-FAQ) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Bucket Policies](https://github.com/seaweedfs/seaweedfs/wiki/S3-Bucket-Policies) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Bucket Quota](https://github.com/seaweedfs/seaweedfs/wiki/S3-Bucket-Quota) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Conditional Operations](https://github.com/seaweedfs/seaweedfs/wiki/S3-Conditional-Operations) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Configuration](https://github.com/seaweedfs/seaweedfs/wiki/S3-Configuration) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 CORS](https://github.com/seaweedfs/seaweedfs/wiki/S3-CORS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Credentials](https://github.com/seaweedfs/seaweedfs/wiki/S3-Credentials) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Nginx Proxy](https://github.com/seaweedfs/seaweedfs/wiki/S3-Nginx-Proxy) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Object Lock and Retention](https://github.com/seaweedfs/seaweedfs/wiki/S3-Object-Lock-and-Retention) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Object Versioning](https://github.com/seaweedfs/seaweedfs/wiki/S3-Object-Versioning) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Policy Variables](https://github.com/seaweedfs/seaweedfs/wiki/S3-Policy-Variables) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Rate Limiting](https://github.com/seaweedfs/seaweedfs/wiki/S3-Rate-Limiting) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Table Bucket](https://github.com/seaweedfs/seaweedfs/wiki/S3-Table-Bucket) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Table Bucket Commands](https://github.com/seaweedfs/seaweedfs/wiki/S3-Table-Bucket-Commands) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [S3 Tables Security](https://github.com/seaweedfs/seaweedfs/wiki/S3-Tables-Security) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [s3cmd with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/s3cmd-with-SeaweedFS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Seaweed Message Queue](https://github.com/seaweedfs/seaweedfs/wiki/Seaweed-Message-Queue) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [SeaweedFS Architecture](https://github.com/seaweedfs/seaweedfs/wiki/SeaweedFS-Architecture) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [SeaweedFS Iceberg Catalog](https://github.com/seaweedfs/seaweedfs/wiki/SeaweedFS-Iceberg-Catalog) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [SeaweedFS in Docker Swarm](https://github.com/seaweedfs/seaweedfs/wiki/SeaweedFS-in-Docker-Swarm) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [SeaweedFS Java Client](https://github.com/seaweedfs/seaweedfs/wiki/SeaweedFS-Java-Client) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Security Configuration](https://github.com/seaweedfs/seaweedfs/wiki/Security-Configuration) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Security Overview](https://github.com/seaweedfs/seaweedfs/wiki/Security-Overview) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Server Side Encryption](https://github.com/seaweedfs/seaweedfs/wiki/Server-Side-Encryption) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Server Side Encryption SSE C](https://github.com/seaweedfs/seaweedfs/wiki/Server-Side-Encryption-SSE-C) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Server Side Encryption SSE KMS](https://github.com/seaweedfs/seaweedfs/wiki/Server-Side-Encryption-SSE-KMS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Server Startup via Systemd](https://github.com/seaweedfs/seaweedfs/wiki/Server-Startup-via-Systemd) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [SFTP Server](https://github.com/seaweedfs/seaweedfs/wiki/SFTP-Server) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [SQL Queries on Message Queue](https://github.com/seaweedfs/seaweedfs/wiki/SQL-Queries-on-Message-Queue) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [SQL Quick Reference](https://github.com/seaweedfs/seaweedfs/wiki/SQL-Quick-Reference) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [SRV Service Discovery](https://github.com/seaweedfs/seaweedfs/wiki/SRV-Service-Discovery) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Store file with a Time To Live](https://github.com/seaweedfs/seaweedfs/wiki/Store-file-with-a-Time-To-Live) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Structured Data Lake with SMQ and SQL](https://github.com/seaweedfs/seaweedfs/wiki/Structured-Data-Lake-with-SMQ-and-SQL) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Super Large Directories](https://github.com/seaweedfs/seaweedfs/wiki/Super-Large-Directories) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Supported APIs vs Minio](https://github.com/seaweedfs/seaweedfs/wiki/Supported-APIs-vs-Minio) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [System Metrics](https://github.com/seaweedfs/seaweedfs/wiki/System-Metrics) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [TensorFlow with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/TensorFlow-with-SeaweedFS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Tiered Storage](https://github.com/seaweedfs/seaweedfs/wiki/Tiered-Storage) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [TUS Resumable Uploads](https://github.com/seaweedfs/seaweedfs/wiki/TUS-Resumable-Uploads) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [UrBackup with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/UrBackup-with-SeaweedFS) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Use Cases](https://github.com/seaweedfs/seaweedfs/wiki/Use-Cases) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Volume Files Structure](https://github.com/seaweedfs/seaweedfs/wiki/Volume-Files-Structure) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Volume Management](https://github.com/seaweedfs/seaweedfs/wiki/Volume-Management) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Volume Server API](https://github.com/seaweedfs/seaweedfs/wiki/Volume-Server-API) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [WebDAV](https://github.com/seaweedfs/seaweedfs/wiki/WebDAV) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [weed shell](https://github.com/seaweedfs/seaweedfs/wiki/weed-shell) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Words from SeaweedFS Users](https://github.com/seaweedfs/seaweedfs/wiki/Words-from-SeaweedFS-Users) ### Uh oh! There was an error while loading. Please reload this page.

 - Loading [Worker](https://github.com/seaweedfs/seaweedfs/wiki/Worker) ### Uh oh! There was an error while loading. Please reload this page.

 - Show 127 more pages…

 [/seaweedfs/seaweedfs/wiki/_Sidebar/_edit](https://github.com/seaweedfs/seaweedfs/wiki/_Sidebar/_edit)

### Introduction
[#introduction](https://github.com/seaweedfs/seaweedfs/wiki#introduction)

- [Quick Start with weed mini](https://github.com/seaweedfs/seaweedfs/wiki/Quick-Start-with-weed-mini)

- [Components](https://github.com/seaweedfs/seaweedfs/wiki/Components)

- [Getting Started](https://github.com/seaweedfs/seaweedfs/wiki/Getting-Started)

- [Production Setup](https://github.com/seaweedfs/seaweedfs/wiki/Production-Setup)

- [Benchmarks](https://github.com/seaweedfs/seaweedfs/wiki/Benchmarks)

- [FAQ](https://github.com/seaweedfs/seaweedfs/wiki/FAQ)

- [Applications](https://github.com/seaweedfs/seaweedfs/wiki/Applications)

### API
[#api](https://github.com/seaweedfs/seaweedfs/wiki#api)

- [Master Server API](https://github.com/seaweedfs/seaweedfs/wiki/Master-Server-API)

- [Volume Server API](https://github.com/seaweedfs/seaweedfs/wiki/Volume-Server-API)

- [Filer Server API](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Server-API)

- [Client Libraries](https://github.com/seaweedfs/seaweedfs/wiki/Client-Libraries)

- [SeaweedFS Java Client](https://github.com/seaweedfs/seaweedfs/wiki/SeaweedFS-Java-Client)

### Configuration
[#configuration](https://github.com/seaweedfs/seaweedfs/wiki#configuration)

- [Replication](https://github.com/seaweedfs/seaweedfs/wiki/Replication)

- [Store file with a Time To Live](https://github.com/seaweedfs/seaweedfs/wiki/Store-file-with-a-Time-To-Live)

- [Failover Master Server](https://github.com/seaweedfs/seaweedfs/wiki/Failover-Master-Server)

- [Erasure coding for warm storage](https://github.com/seaweedfs/seaweedfs/wiki/Erasure-Coding-for-warm-storage)

- [Server Startup via Systemd](https://github.com/seaweedfs/seaweedfs/wiki/Server-Startup-via-Systemd)

- [Environment Variables](https://github.com/seaweedfs/seaweedfs/wiki/Environment-Variables)

### Filer
[#filer](https://github.com/seaweedfs/seaweedfs/wiki#filer)

- [Filer Setup](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Setup)

- [Directories and Files](https://github.com/seaweedfs/seaweedfs/wiki/Directories-and-Files)

- [File Operations Quick Reference](https://github.com/seaweedfs/seaweedfs/wiki/File-Operations-Quick-Reference)

- [Data Structure for Large Files](https://github.com/seaweedfs/seaweedfs/wiki/Data-Structure-for-Large-Files)

- [Filer Data Encryption](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Data-Encryption)

- [Filer Commands and Operations](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Commands-and-Operations)

- [Filer JWT Use](https://github.com/seaweedfs/seaweedfs/wiki/Filer-JWT-Use)

- [TUS Resumable Uploads](https://github.com/seaweedfs/seaweedfs/wiki/TUS-Resumable-Uploads)

### Filer Stores
[#filer-stores](https://github.com/seaweedfs/seaweedfs/wiki#filer-stores)

- [Filer Cassandra Setup](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Cassandra-Setup)

- [Filer Redis Setup](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Redis-Setup)

- [Super Large Directories](https://github.com/seaweedfs/seaweedfs/wiki/Super-Large-Directories)

- [Path-Specific Filer Store](https://github.com/seaweedfs/seaweedfs/wiki/Path-Specific-Filer-Store)

- [Choosing a Filer Store](https://github.com/seaweedfs/seaweedfs/wiki/Choosing-a-Filer-Store)

- [Customize Filer Store](https://github.com/seaweedfs/seaweedfs/wiki/Customize-Filer-Store)

### Management
[#management](https://github.com/seaweedfs/seaweedfs/wiki#management)

- [Admin UI](https://github.com/seaweedfs/seaweedfs/wiki/Admin-UI)

- [Worker](https://github.com/seaweedfs/seaweedfs/wiki/Worker)

- [Plugin Worker Scheduling](https://github.com/seaweedfs/seaweedfs/wiki/Plugin-Worker-Scheduling)

### Advanced Filer Configurations
[#advanced-filer-configurations](https://github.com/seaweedfs/seaweedfs/wiki#advanced-filer-configurations)

- [Migrate to Filer Store](https://github.com/seaweedfs/seaweedfs/wiki/Migrate-to-Filer-Store)

- [Add New Filer Store](https://github.com/seaweedfs/seaweedfs/wiki/Customize-Filer-Store)

- [Filer Store Replication](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Store-Replication)

- [Filer Active Active cross cluster continuous synchronization](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Active-Active-cross-cluster-continuous-synchronization)

- [Filer as a Key-Large-Value Store](https://github.com/seaweedfs/seaweedfs/wiki/Filer-as-a-Key-Large-Value-Store)

- [Path Specific Configuration](https://github.com/seaweedfs/seaweedfs/wiki/Path-Specific-Configuration)

- [Filer Change Data Capture](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Change-Data-Capture)

### FUSE Mount
[#fuse-mount](https://github.com/seaweedfs/seaweedfs/wiki#fuse-mount)

- [FIO benchmark](https://github.com/seaweedfs/seaweedfs/wiki/FIO-benchmark)

- [fstab](https://github.com/seaweedfs/seaweedfs/wiki/fstab)

### WebDAV
[#webdav](https://github.com/seaweedfs/seaweedfs/wiki#webdav)

### SFTP Server
[#sftp-server](https://github.com/seaweedfs/seaweedfs/wiki#sftp-server)

### Cloud Drive
[#cloud-drive](https://github.com/seaweedfs/seaweedfs/wiki#cloud-drive)

- [Cloud Drive Benefits](https://github.com/seaweedfs/seaweedfs/wiki/Cloud-Drive-Benefits)

- [Cloud Drive Architecture](https://github.com/seaweedfs/seaweedfs/wiki/Cloud-Drive-Architecture)

- [Configure Remote Storage](https://github.com/seaweedfs/seaweedfs/wiki/Configure-Remote-Storage)

- [Mount Remote Storage](https://github.com/seaweedfs/seaweedfs/wiki/Mount-Remote-Storage)

- [Cache Remote Storage](https://github.com/seaweedfs/seaweedfs/wiki/Cache-Remote-Storage)

- [Cloud Drive Quick Setup](https://github.com/seaweedfs/seaweedfs/wiki/Cloud-Drive-Quick-Setup)

- [Gateway to Remote Object Storage](https://github.com/seaweedfs/seaweedfs/wiki/Gateway-to-Remote-Object-Storage)

### AWS S3 API
[#aws-s3-api](https://github.com/seaweedfs/seaweedfs/wiki#aws-s3-api)

- [Amazon S3 API](https://github.com/seaweedfs/seaweedfs/wiki/Amazon-S3-API)

- [Supported APIs vs Minio](https://github.com/seaweedfs/seaweedfs/wiki/Supported-APIs-vs-Minio)

- [S3 Conditional Operations](https://github.com/seaweedfs/seaweedfs/wiki/S3-Conditional-Operations)

- [S3 CORS](https://github.com/seaweedfs/seaweedfs/wiki/S3-CORS)

- [S3 Object Lock and Retention](https://github.com/seaweedfs/seaweedfs/wiki/S3-Object-Lock-and-Retention)

- [S3 Object Versioning](https://github.com/seaweedfs/seaweedfs/wiki/S3-Object-Versioning)

- [S3 API Benchmark](https://github.com/seaweedfs/seaweedfs/wiki/S3-API-Benchmark)

- [S3 API FAQ](https://github.com/seaweedfs/seaweedfs/wiki/S3-API-FAQ)

- [S3 Bucket Quota](https://github.com/seaweedfs/seaweedfs/wiki/S3-Bucket-Quota)

- [S3 Rate Limiting](https://github.com/seaweedfs/seaweedfs/wiki/S3-Rate-Limiting)

- [S3 API Audit log](https://github.com/seaweedfs/seaweedfs/wiki/S3-API-Audit-log)

- [S3 Nginx Proxy](https://github.com/seaweedfs/seaweedfs/wiki/S3-Nginx-Proxy)

- [Docker Compose for S3](https://github.com/seaweedfs/seaweedfs/wiki/Docker-Compose-for-S3)

### S3 Table Bucket
[#s3-table-bucket](https://github.com/seaweedfs/seaweedfs/wiki#s3-table-bucket)

- [S3 Table Bucket](https://github.com/seaweedfs/seaweedfs/wiki/S3-Table-Bucket)

- [SeaweedFS Iceberg Catalog](https://github.com/seaweedfs/seaweedfs/wiki/SeaweedFS-Iceberg-Catalog)

- [Iceberg Table Maintenance](https://github.com/seaweedfs/seaweedfs/wiki/Iceberg-Table-Maintenance)

- [S3 Tables Security](https://github.com/seaweedfs/seaweedfs/wiki/S3-Tables-Security)

### S3 Authentication & IAM
[#s3-authentication--iam](https://github.com/seaweedfs/seaweedfs/wiki#s3-authentication--iam)

- [S3 Configuration](https://github.com/seaweedfs/seaweedfs/wiki/S3-Configuration) - Start Here

- [S3 Credentials](https://github.com/seaweedfs/seaweedfs/wiki/S3-Credentials) (`-s3.config`)

- [OIDC Integration](https://github.com/seaweedfs/seaweedfs/wiki/OIDC-Integration) (`-s3.iam.config`)

- [S3 Policy Variables](https://github.com/seaweedfs/seaweedfs/wiki/S3-Policy-Variables)

- [S3 Bucket Policies](https://github.com/seaweedfs/seaweedfs/wiki/S3-Bucket-Policies)

- [Amazon IAM API](https://github.com/seaweedfs/seaweedfs/wiki/Amazon-IAM-API)

- [AWS IAM CLI](https://github.com/seaweedfs/seaweedfs/wiki/AWS-IAM-CLI)

### Server-Side Encryption
[#server-side-encryption](https://github.com/seaweedfs/seaweedfs/wiki#server-side-encryption)

- [Server-Side Encryption](https://github.com/seaweedfs/seaweedfs/wiki/Server-Side-Encryption)

- [Server-Side Encryption SSE-KMS](https://github.com/seaweedfs/seaweedfs/wiki/Server-Side-Encryption-SSE-KMS)

- [Server-Side Encryption SSE-C](https://github.com/seaweedfs/seaweedfs/wiki/Server-Side-Encryption-SSE-C)

### S3 Client Tools
[#s3-client-tools](https://github.com/seaweedfs/seaweedfs/wiki#s3-client-tools)

- [AWS CLI with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/AWS-CLI-with-SeaweedFS)

- [s3cmd with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/s3cmd-with-SeaweedFS)

- [rclone with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/rclone-with-SeaweedFS)

- [restic with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/restic-with-SeaweedFS)

- [nodejs with Seaweed S3](https://github.com/seaweedfs/seaweedfs/wiki/nodejs-with-Seaweed-S3)

### Machine Learning
[#machine-learning](https://github.com/seaweedfs/seaweedfs/wiki#machine-learning)

- [TensorFlow with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/TensorFlow-with-SeaweedFS)

### HDFS
[#hdfs](https://github.com/seaweedfs/seaweedfs/wiki#hdfs)

- [Hadoop Compatible File System](https://github.com/seaweedfs/seaweedfs/wiki/Hadoop-Compatible-File-System)

- [run Spark on SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/run-Spark-on-SeaweedFS)

- [run HBase on SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/run-HBase-on-SeaweedFS)

- [run Presto on SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/Run-Presto-on-SeaweedFS)

- [Hadoop Benchmark](https://github.com/seaweedfs/seaweedfs/wiki/Hadoop-Benchmark)

- [HDFS via S3 connector](https://github.com/seaweedfs/seaweedfs/wiki/HDFS-via-S3-connector)

### Replication and Backup
[#replication-and-backup](https://github.com/seaweedfs/seaweedfs/wiki#replication-and-backup)

- [Async Replication to another Filer](https://github.com/seaweedfs/seaweedfs/wiki/Async-Replication-to-another-Filer) [Deprecated]

- [Async Backup](https://github.com/seaweedfs/seaweedfs/wiki/Async-Backup)

- [Async Filer Metadata Backup](https://github.com/seaweedfs/seaweedfs/wiki/Async-Filer-Metadata-Backup)

- [Async Replication to Cloud](https://github.com/seaweedfs/seaweedfs/wiki/Async-Replication-to-Cloud) [Deprecated]

- [Kubernetes Backups and Recovery with K8up](https://github.com/seaweedfs/seaweedfs/wiki/Kubernetes-Backups-and-Recovery-with-K8up)

### Metadata Change Events
[#metadata-change-events](https://github.com/seaweedfs/seaweedfs/wiki#metadata-change-events)

- [Filer Metadata Events](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Metadata-Events)

- [Filer Notification Webhook](https://github.com/seaweedfs/seaweedfs/wiki/Filer-Notification-Webhook)

### Messaging
[#messaging](https://github.com/seaweedfs/seaweedfs/wiki#messaging)

- [Structured Data Lake with SMQ and SQL](https://github.com/seaweedfs/seaweedfs/wiki/Structured-Data-Lake-with-SMQ-and-SQL)

- [Seaweed Message Queue](https://github.com/seaweedfs/seaweedfs/wiki/Seaweed-Message-Queue)

- [SQL Queries on Message Queue](https://github.com/seaweedfs/seaweedfs/wiki/SQL-Queries-on-Message-Queue)

- [SQL Quick Reference](https://github.com/seaweedfs/seaweedfs/wiki/SQL-Quick-Reference)

- [PostgreSQL-compatible Server weed db](https://github.com/seaweedfs/seaweedfs/wiki/PostgreSQL-compatible-Server-weed-db)

- [Pub-Sub to SMQ to SQL](https://github.com/seaweedfs/seaweedfs/wiki/Pub-Sub-to-SMQ-to-SQL)

- [Kafka to Kafka Gateway to SMQ to SQL](https://github.com/seaweedfs/seaweedfs/wiki/Kafka-to-Kafka-Gateway-to-SMQ-to-SQL)

### Use Cases
[#use-cases](https://github.com/seaweedfs/seaweedfs/wiki#use-cases)

- [Use Cases](https://github.com/seaweedfs/seaweedfs/wiki/Use-Cases)

- [Actual Users](https://github.com/seaweedfs/seaweedfs/wiki/Actual-Users)

### Operations
[#operations](https://github.com/seaweedfs/seaweedfs/wiki#operations)

- [System Metrics](https://github.com/seaweedfs/seaweedfs/wiki/System-Metrics)

- [weed shell](https://github.com/seaweedfs/seaweedfs/wiki/weed-shell)

- [Data Backup](https://github.com/seaweedfs/seaweedfs/wiki/Data-Backup)

- [Deployment to Kubernetes and Minikube](https://github.com/seaweedfs/seaweedfs/wiki/Deployment-to-Kubernetes-and-Minikube)

### Rust Volume Server
[#rust-volume-server](https://github.com/seaweedfs/seaweedfs/wiki#rust-volume-server)

- [Rust Volume Server](https://github.com/seaweedfs/seaweedfs/wiki/Rust-Volume-Server)

### Advanced
[#advanced](https://github.com/seaweedfs/seaweedfs/wiki#advanced)

- [Large File Handling](https://github.com/seaweedfs/seaweedfs/wiki/Large-File-Handling)

- [Optimization](https://github.com/seaweedfs/seaweedfs/wiki/Optimization)

- [Optimization for Many Small Buckets](https://github.com/seaweedfs/seaweedfs/wiki/Optimization-for-Many-Small-Buckets)

- [Volume Management](https://github.com/seaweedfs/seaweedfs/wiki/Volume-Management)

- [Tiered Storage](https://github.com/seaweedfs/seaweedfs/wiki/Tiered-Storage)

- [Cloud Tier](https://github.com/seaweedfs/seaweedfs/wiki/Cloud-Tier)

- [Cloud Monitoring](https://github.com/seaweedfs/seaweedfs/wiki/Cloud-Monitoring)

- [Load Command Line Options from a file](https://github.com/seaweedfs/seaweedfs/wiki/Load-Command-Line-Options-from-a-file)

- [SRV Service Discovery](https://github.com/seaweedfs/seaweedfs/wiki/SRV-Service-Discovery)

- [Volume Files Structure](https://github.com/seaweedfs/seaweedfs/wiki/Volume-Files-Structure)

### Security
[#security](https://github.com/seaweedfs/seaweedfs/wiki#security)

- [Security Overview](https://github.com/seaweedfs/seaweedfs/wiki/Security-Overview)

- [Security Configuration](https://github.com/seaweedfs/seaweedfs/wiki/Security-Configuration)

- [Cryptography and FIPS Compliance](https://github.com/seaweedfs/seaweedfs/wiki/Cryptography-and-FIPS-Compliance)

- [Run Blob Storage on Public Internet](https://github.com/seaweedfs/seaweedfs/wiki/Run-Blob-Storage-on-Public-Internet)

### Misc Use Case Examples
[#misc-use-case-examples](https://github.com/seaweedfs/seaweedfs/wiki#misc-use-case-examples)

- [UrBackup with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/UrBackup-with-SeaweedFS)

- [Docker Image Registry with SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki/Docker-Image-Registry-with-SeaweedFS)

- [SeaweedFS in Docker Swarm](https://github.com/seaweedfs/seaweedfs/wiki/SeaweedFS-in-Docker-Swarm)

- [Words from SeaweedFS Users](https://github.com/seaweedfs/seaweedfs/wiki/Words-from-SeaweedFS-Users)

- [Independent Benchmarks](https://github.com/seaweedfs/seaweedfs/wiki/Independent-Benchmarks)

- [Hardware](https://github.com/seaweedfs/seaweedfs/wiki/Hardware)

### Clone this wiki locally
