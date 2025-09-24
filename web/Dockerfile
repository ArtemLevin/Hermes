FROM node:20-alpine

WORKDIR /app

# Устанавливаем зависимости (поддержка любых lock-файлов)
COPY package.json ./
COPY package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN \
  if [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i --frozen-lockfile; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  else npm install; fi

# Копируем исходники
COPY . .

# Порт dev-сервера Vite
EXPOSE 5173

# Переменная для доступа к API (можно использовать в коде как import.meta.env.VITE_API_URL)
ENV VITE_API_URL=http://localhost:8000

# Запуск Vite в режиме dev с пробросом на 0.0.0.0
CMD [ "npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173" ]
