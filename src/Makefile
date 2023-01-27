PROJECT_NAME = Movies

all:
	@echo "make load_dump		- Загрузка тестовых данных в базу "
	@echo "make run		- Запуск контейнеров "
	@echo "make stop		- Выключение контейнера."
	@echo "make rebuild		- Пересборка контейнера."
	@echo "make logs		- Логи сборки."

load_dump:
	cat dump1.sql | docker-compose exec -T db psql -U app -d movies_database

run:
	#docker-compose up Команда для сборки и запуска контейнера.
	#--build Сборка образа перед запуском контейнера.
	#-d Detached mode.
	docker-compose up --build -d

logs:
	#docker-compose logs Команда для открытия логов контейнеров.
	docker-compose logs


rebuild:
	#docker-compose up Команда для пересборки и запуска контейнера.
	#--build Сборка образа перед запуском контейнера.
	#-d Detached mode.
	docker-compose down && docker-compose up --build -d

stop:
	#Остановка и удаление контейнеров, запущенных docker-compose up.
	docker-compose down


