FROM node:18-alpine

# Install dependencies
RUN apk add --no-cache curl unzip bash docker-cli

# Install latest Supabase CLI (v2.x)
RUN curl -L https://github.com/supabase/cli/releases/download/v2.26.9/supabase_linux_amd64.tar.gz \
  | tar -xz -C /usr/local/bin

WORKDIR /app
COPY . .
