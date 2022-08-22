PATH_PREFIX=~

create-topics:
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic downloader \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic monitor \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic manager \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic storage \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic updater \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic verifier \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic positioning \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1


sys-packages:
	# sudo apt install -y docker-compose
	sudo apt install python3-pip -y
	sudo pip install pipenv

broker:
	docker-compose -f kafka/docker-compose.yaml up -d

permissions:
	chmod u+x $(PATH_PREFIX)/secure-update/app/app.py
	chmod u+x $(PATH_PREFIX)/secure-update/downloader/downloader.py
	chmod u+x $(PATH_PREFIX)/secure-update/file_server/server.py
	chmod u+x $(PATH_PREFIX)/secure-update/manager/manager.py
	# chmod u+x $(PATH_PREFIX)/secure-update/manager-hacked/manager.py
	chmod u+x $(PATH_PREFIX)/secure-update/monitor/monitor.py
	chmod u+x $(PATH_PREFIX)/secure-update/storage/storage.py
	chmod u+x $(PATH_PREFIX)/secure-update/updater/updater.py
	chmod u+x $(PATH_PREFIX)/secure-update/verifier/verifier.py
	chmod u+x $(PATH_PREFIX)/secure-update/positioning/positioning.py

pipenv:
	pipenv install -r requirements.txt

prepare: sys-packages permissions pipenv build run-broker

prepare-screen:
	# WSL specific preparation
	sudo /etc/init.d/screen-cleanup start


run-screen: broker run-app-screen run-monitor-screen run-manager-screen run-file-server-screen run-downloader-screen run-storage-screen run-verifier-screen run-updater-screen

build:
	docker-compose build

run-broker:
	docker-compose up -d zookeeper broker

run:
	docker-compose up -d

restart:
	docker-compose restart

stop-app:
	pkill flask

restart-app: stop-app run


run-monitor-screen:
	screen -dmS monitor bash -c "cd $(PATH_PREFIX)/secure-update/; pipenv run ./monitor/monitor.py config.ini"

run-monitor:
	cd $(PATH_PREFIX)/secure-update/; pipenv run ./monitor/monitor.py config.ini


run-manager-screen:
	screen -dmS manager bash -c "cd $(PATH_PREFIX)/secure-update/; pipenv run ./manager/manager.py config.ini"

run-manager:
	cd $(PATH_PREFIX)/secure-update/; pipenv run ./manager/manager.py config.ini


run-hacked-manager:
	cd $(PATH_PREFIX)/secure-update/; pipenv run ./manager-hacked/manager.py config.ini

run-app:
	cd $(PATH_PREFIX)/secure-update/app/; export FLASK_DEBUG=1; pipenv run ./app.py

run-app-screen:
	screen -dmS app bash -c "cd $(PATH_PREFIX)/secure-update/; export FLASK_DEBUG=1; pipenv run ./app/app.py"

run-file-server:
	cd $(PATH_PREFIX)/secure-update/file_server; export FLASK_DEBUG=1; pipenv run ./server.py

run-file-server-screen:
	screen -dmS file-server bash -c "cd $(PATH_PREFIX)/secure-update/file_server; export FLASK_DEBUG=1; pipenv run ./server.py"

run-downloader:
	cd $(PATH_PREFIX)/secure-update; pipenv run downloader/downloader.py config.ini

run-downloader-screen:
	screen -dmS downloader bash -c "cd $(PATH_PREFIX)/secure-update; pipenv run downloader/downloader.py config.ini"

run-verifier:
	cd $(PATH_PREFIX)/secure-update; pipenv run verifier/verifier.py config.ini

run-verifier-screen:
	screen -dmS verifier bash -c "cd $(PATH_PREFIX)/secure-update; pipenv run verifier/verifier.py config.ini"

run-storage:
	cd $(PATH_PREFIX)/secure-update; pipenv run storage/storage.py config.ini

run-storage-screen:
	screen -dmS storage bash -c "cd $(PATH_PREFIX)/secure-update; pipenv run storage/storage.py config.ini"

run-updater:
	cd $(PATH_PREFIX)/secure-update; pipenv run updater/updater.py config.ini

run-updater-screen:
	screen -dmS updater bash -c "cd $(PATH_PREFIX)/secure-update; pipenv run updater/updater.py config.ini"

test:
	pytest -sv