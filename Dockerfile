## Build frontend
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


## Runtime (FastAPI + serves frontend dist)
FROM python:3.12-bullseye

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
	&& python -m pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy built frontend assets into the runtime image
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

ENV MODE=production

# Render provides $PORT; default to 4000 locally.
ENV PORT=4000
EXPOSE 4000

CMD ["sh", "-c", "python -m uvicorn src.app:APP --host 0.0.0.0 --port ${PORT:-4000} --proxy-headers"]
