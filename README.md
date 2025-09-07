# Cloud Basic Course
This repository contains the code, report and presentation for the project of Cloud Computing Basic (Course year 2023-2024) teached in the Data Science & Artificial Intelligence Master @ University of Trieste.

To better understand the choices, tests and project structure you're welcome to read the report and/or presentation.

# How to run

It is assumed that you have installed Docker on your machine and that you're located inside the project folder. To build the containers you simply need to run the script `setup.sh`:
```bash
./setup.sh
```
This will compose the containers and remove some applications from Nextcloud. After that you can visit http://localhost:8080 and login as the admin:
```yaml
username: admin
password: password
```

If you're interested in replicating the locust tests you will first need to install `locust` and `python-dotenv` on your python env of choice:
```bash
pip install locust python-dotenv
``` 
Then move to the folder **scripts** and run `create_users.sh` to populate the Nextcloud users
```bash
./create_users.sh
```
Now you have access to 3 different tests that you can execute via shell
 - `./run_easy.sh`
 - `./run_throughput.sh`
 - `./run_bandwidth.sh`




