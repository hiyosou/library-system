FROM python:3.11-slim

# keep image small and predictable
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

USER root

# ソースコードは最初にコピー
COPY opt/ /opt/
WORKDIR /opt

# copy requirements after source (per requirement)
COPY requirements.txt /opt/

# install minimal runtime deps and gunicorn for running the app
# --no-cache-dir to keep image small
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# create an unprivileged user and fix permissions
RUN useradd --create-home appuser \
	&& chown -R appuser:appuser /opt

EXPOSE 5000

USER appuser

# Use gunicorn with a single worker by default (lightweight)
# main:app を起点にしてアプリを実行
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "main:app"]