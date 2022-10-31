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
    --topic communication_in \
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
    --topic position \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic sensors \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic gps \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic camera \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec broker \
  kafka-topics --create --if-not-exists \
    --topic communication_out \
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
	chmod u+x $(PATH_PREFIX)/delivery-robot/monitor/monitor.py
	chmod u+x $(PATH_PREFIX)/delivery-robot/central/central.py
	chmod u+x $(PATH_PREFIX)/delivery-robot/communication_in/communication_in.py
	chmod u+x $(PATH_PREFIX)/delivery-robot/communication_out/communication_out.py
	chmod u+x $(PATH_PREFIX)/delivery-robot/fleet/server.py
	chmod u+x $(PATH_PREFIX)/delivery-robot/hmi/hmi.py
	chmod u+x $(PATH_PREFIX)/delivery-robot/motion/motion.py
	chmod u+x $(PATH_PREFIX)/delivery-robot/position/position.py
	chmod u+x $(PATH_PREFIX)/delivery-robot/sensors/sensors.py
	chmod u+x $(PATH_PREFIX)/delivery-robot/camera/camera.py
	chmod u+x $(PATH_PREFIX)/delivery-robot/gps/gps.py

pipenv:
	pipenv install -r requirements.txt

prepare: sys-packages permissions pipenv build run-broker

prepare-screen:
	# WSL specific preparation
	sudo /etc/init.d/screen-cleanup start


run-screen: broker run-central-screen run-communication_out-screen run-communication_in-screen run-fleet-screen run-hmi-screen run-motion-screen run-sensors-screen run-position-screen run-gps-screen run-camera-screen

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
	screen -dmS monitor bash -c "cd $(PATH_PREFIX)/delivery-robot/; pipenv run ./monitor/monitor.py config.ini"

run-monitor:
	cd $(PATH_PREFIX)/delivery-robot/; pipenv run ./monitor/monitor.py config.ini


run-position:
	cd $(PATH_PREFIX)/delivery-robot/; pipenv run position/position.py config.ini

run-position-screen:
	screen -dmS position bash -c "cd $(PATH_PREFIX)/delivery-robot/; pipenv run position/position.py config.ini"

run-central:
	cd $(PATH_PREFIX)/delivery-robot/; pipenv run central/central.py config.ini

run-central-screen:
	screen -dmS central bash -c "cd $(PATH_PREFIX)/delivery-robot/; pipenv run central/central.py config.ini"

run-communication_in:
	cd $(PATH_PREFIX)/delivery-robot/; pipenv run communication_in/communication_in.py config.ini

run-communication_in-screen:
	screen -dmS central bash -c "cd $(PATH_PREFIX)/delivery-robot/; pipenv run communication_in/communication_in.py config.ini"

run-communication_out:
	cd $(PATH_PREFIX)/delivery-robot/; pipenv run communication_out/communication_out.py config.ini

run-communication_out-screen:
	screen -dmS central bash -c "cd $(PATH_PREFIX)/delivery-robot/; pipenv run communication_out/communication_out.py config.ini"

run-fleet:
	cd $(PATH_PREFIX)/delivery-robot/; pipenv run fleet/fleet.py config.ini

run-fleet-screen:
	screen -dmS fleet bash -c "cd $(PATH_PREFIX)/delivery-robot/; pipenv run fleet/fleet.py config.ini"

run-hmi:
	cd $(PATH_PREFIX)/delivery-robot/; pipenv run hmi/hmi.py config.ini

run-hmi-screen:
	screen -dmS hmi bash -c "cd $(PATH_PREFIX)/delivery-robot/; pipenv run hmi/hmi.py config.ini"

run-motion:
	cd $(PATH_PREFIX)/delivery-robot/; pipenv run motion/motion.py config.ini

run-motion-screen:
	screen -dmS motion bash -c "cd $(PATH_PREFIX)/delivery-robot/; pipenv run motion/motion.py config.ini"

run-sensors:
	cd $(PATH_PREFIX)/delivery-robot/; pipenv run sensors/sensors.py config.ini

run-sensors-screen:
	screen -dmS sensors bash -c "cd $(PATH_PREFIX)/delivery-robot/; pipenv run sensors/sensors.py config.ini"

run-gps:
	cd $(PATH_PREFIX)/delivery-robot/; pipenv run gps/gps.py config.ini

run-gps-screen:
	screen -dmS gps bash -c "cd $(PATH_PREFIX)/delivery-robot/; pipenv run gps/gps.py config.ini"

run-camera:
	cd $(PATH_PREFIX)/delivery-robot/; pipenv run camera/camera.py config.ini

run-camera-screen:
	screen -dmS camera bash -c "cd $(PATH_PREFIX)/delivery-robot/; pipenv run camera/camera.py config.ini"

test:
	pytest -sv
