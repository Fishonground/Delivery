PATH_PREFIX=~

create-topics:
  	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic monitor \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic central \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic communication \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic hmi \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic motion \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic positioning \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic sensors \
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
	chmod u+x $(PATH_PREFIX)/secure-update/monitor/monitor.py
	chmod u+x $(PATH_PREFIX)/secure-update/central/central.py
	chmod u+x $(PATH_PREFIX)/secure-update/communication/communication.py
	chmod u+x $(PATH_PREFIX)/secure-update/fleet/server.py
	chmod u+x $(PATH_PREFIX)/secure-update/hmi/hmi.py
	chmod u+x $(PATH_PREFIX)/secure-update/motion/motion.py
	chmod u+x $(PATH_PREFIX)/secure-update/positioning/positioning.py
	chmod u+x $(PATH_PREFIX)/secure-update/sensors/sensors.py

pipenv:
	pipenv install -r requirements.txt

prepare: sys-packages permissions pipenv build run-broker

prepare-screen:
	# WSL specific preparation
	sudo /etc/init.d/screen-cleanup start


run-screen: broker run-central-screen run-communication-screen run-fleet-screen run-hmi-screen run-motion-screen run-sensors-screen run-positioning-screen

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


run-positioning:
	cd $(PATH_PREFIX)/secure-update; pipenv run positioning/positioning.py config.ini

run-positioning-screen:
	screen -dmS positioning bash -c "cd $(PATH_PREFIX)/secure-update; pipenv run positioning/positioning.py config.ini"

run-central:
	cd $(PATH_PREFIX)/secure-update; pipenv run central/central.py config.ini

run-central-screen:
	screen -dmS central bash -c "cd $(PATH_PREFIX)/secure-update; pipenv run central/central.py config.ini"

run-communication:
	cd $(PATH_PREFIX)/secure-update; pipenv run communication/communication.py config.ini

run-communication-screen:
	screen -dmS central bash -c "cd $(PATH_PREFIX)/secure-update; pipenv run central/central.py config.ini"

run-fleet:
	cd $(PATH_PREFIX)/secure-update; pipenv run fleet/fleet.py config.ini

run-fleet-screen:
	screen -dmS fleet bash -c "cd $(PATH_PREFIX)/secure-update; pipenv run fleet/fleet.py config.ini"

run-hmi:
	cd $(PATH_PREFIX)/secure-update; pipenv run hmi/hmi.py config.ini

run-hmi-screen:
	screen -dmS hmi bash -c "cd $(PATH_PREFIX)/secure-update; pipenv run hmi/hmi.py config.ini"

run-motion:
	cd $(PATH_PREFIX)/secure-update; pipenv run motion/motion.py config.ini

run-motion-screen:
	screen -dmS motion bash -c "cd $(PATH_PREFIX)/secure-update; pipenv run motion/motion.py config.ini"

run-sensors:
	cd $(PATH_PREFIX)/secure-update; pipenv run sensors/sensors.py config.ini

run-sensors-screen:
	screen -dmS sensors bash -c "cd $(PATH_PREFIX)/secure-update; pipenv run sensors/sensors.py config.ini"

test:
	pytest -sv
