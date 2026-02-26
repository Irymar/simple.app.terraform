# Simple Terraform App: повний цикл розгортання веб-застосунку

Цей проєкт показує повний практичний цикл роботи з простим застосунком: `frontend + backend + database` від локального запуску до віддаленого автоматичного деплою.

Ідея проста: ми будуємо один і той самий застосунок, але керуємо ним на різних рівнях:
- локально через Docker Compose;
- віддалено через Terraform (інфраструктура) та GitHub Actions (CI/CD);
- із публікацією Docker-образів у Docker Hub.

Проєкт підходить як навчальний шаблон для DevOps-підходу: інфраструктура як код, повторюваний деплой, контроль змін через Git.

## Що тут є

- `frontend/` - статичний frontend у контейнері Nginx
- `backend/` - Flask API у контейнері Python
- `docker-compose.yml` - локальний сценарій (build із локального коду)
- `docker-compose.prod.yml` - remote сценарій (pull готових образів із Docker Hub)
- `infra/terraform/` - конфіг Terraform для створення VM
- `.github/workflows/deploy.yml` - CI/CD pipeline для `deploy` і `destroy`

## Технології і підходи

- `Terraform` - створення і видалення сервера декларативно
- `Docker` - стандартизоване пакування frontend/backend
- `Docker Compose` - запуск кількох сервісів однією командою
- `Docker Hub` - registry для зберігання образів
- `GitHub Actions` - автоматизація build/push/deploy/destroy
- `Infrastructure as Code` - конфігурація інфраструктури у файлах
- `CI/CD` - без ручного копіювання коду на сервер

## Локальне використання

### Передумови

- встановлений Docker Desktop (або Docker Engine + Compose plugin)

### Запуск

```bash
docker compose up --build
```

### Доступ

- Frontend: `http://localhost:8080`
- Backend health: `http://localhost:5000/api/health`
- Backend notes: `http://localhost:5000/api/notes`

### Зупинка

```bash
docker compose down
```

## Віддалений сценарій (Terraform + CI/CD)

У віддаленому режимі pipeline виконує повний ланцюжок:
1. збирає frontend/backend образи;
2. пушить образи в Docker Hub;
3. виконує `terraform apply`;
4. отримує IP сервера;
5. підключається по SSH;
6. копіює `docker-compose.prod.yml`;
7. виконує `docker compose pull` і `docker compose up -d`.

## GitHub Secrets (обов'язково)

У репозиторії: `Settings -> Secrets and variables -> Actions`

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `TF_API_TOKEN`
- `HCLOUD_TOKEN`
- `HCLOUD_SSH_KEY_NAME`
- `SSH_PRIVATE_KEY`

## Як запускати pipeline

### Deploy

- автоматично при push у `main`, або
- вручну: `Actions -> Deploy via Terraform + Docker Hub + Compose -> Run workflow -> action=deploy`

Результат:
- Frontend: `http://<SERVER_IP>:8080`
- Backend: `http://<SERVER_IP>:5000/api/health`

### Destroy

- вручну: `Actions -> Deploy via Terraform + Docker Hub + Compose -> Run workflow -> action=destroy`

Результат:
- виконується `terraform destroy`;
- сервер і ресурси видаляються.

## Terraform CLI: перший і наступні запуски

### Перший запуск

```bash
cd infra/terraform
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
terraform output -raw server_ip
```

### Щоденна робота

```bash
cd infra/terraform
terraform plan
terraform apply
terraform output -raw server_ip
```

### Видалення інфраструктури вручну

```bash
cd infra/terraform
terraform destroy
```

## Приклад повного циклу змін

1. Змінюєш код backend або frontend.
2. Робиш commit і push у `main`.
3. GitHub Actions збирає нові образи і пушить у Docker Hub.
4. Terraform гарантує, що сервер існує у потрібному стані.
5. На сервері виконується pull нових образів і перезапуск контейнерів.
6. Застосунок оновлено без ручного деплою.

## Чому ми навчились у цьому проєкті

1. Розділяти локальний і production-сценарії запуску.
2. Працювати з інфраструктурою як кодом.
3. Будувати repeatable CI/CD процес для простого застосунку.
4. Керувати повним життєвим циклом: build, deploy, operate, destroy.

Це невеликий, але повний приклад реального підходу до розгортання сучасного сервісу.
