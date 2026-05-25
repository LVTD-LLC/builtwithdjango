# Build stage
FROM node:16 AS build

WORKDIR /app
COPY . .

RUN npm install
RUN npm run build

# Production stage
FROM python:3.11

WORKDIR /app

COPY . .
COPY --from=build /app/frontend/build/ ./frontend/build/

RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=builtwithdjango.settings
ARG APP_PROCESS_TYPE=server
ENV APP_PROCESS_TYPE=${APP_PROCESS_TYPE}

EXPOSE 80

CMD ["sh", "deployment/entrypoint.sh"]
