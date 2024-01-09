FROM python:3.11-alpine3.18

# Environment variables
ENV PACKAGES=/usr/local/lib/python3.11/site-packages

# ------------------------------------------------------
# --- mkdocs
RUN pip install --no-cache-dir --upgrade \
    pymdown-extensions \
    mkdocs mkdocs-material \
    mkdocs-glightbox \
    mkdocs-minify-plugin \
    mkdocs-redirects \
    mkdocs-awesome-pages-plugin

# ------------------------------------------------------
# --- Workdir Config
VOLUME /app
WORKDIR /app

EXPOSE 8000

ENTRYPOINT ["mkdocs"]
CMD ["serve", "--dev-addr=0.0.0.0:8000"]