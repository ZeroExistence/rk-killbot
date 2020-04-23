# Use an official Python runtime as a parent image
FROM python:alpine
LABEL maintainer="admin@moe.ph"

# Set environment varibles
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV prod

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip3 install -r /app/requirements.txt
RUN pip3 install gunicorn

# Copy the current directory contents into the container at /app/
COPY . /app/
# Set the working directory to /app/
WORKDIR /app/

RUN python manage-prod.py migrate

RUN useradd rk-killbot
RUN chown -R rk-killbot /app
USER rk-killbot

CMD python3 rk-killbot.py
