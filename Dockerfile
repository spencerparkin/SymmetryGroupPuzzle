# Derive from ubuntu/python docker image.
# Note that we must target the 3.6.6 run-time, because our custom dependencies do too.
FROM python:3.6.6-alpine3.8

# Here I think we're creating a new directory called "opt/webapp" in the image's file system,
# and then copying all of our crap into that directory.
ADD . /opt/webapp
WORKDIR /opt/webapp

# Make sure our module dependencies are installed, except for our custom dependencies, of course.
# Our custom dependencies were copied into our work directory.
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Note that this is not supported by heroku.  We'll be using the $PORT env-var instead.
EXPOSE 80

# This is just for testing purposes.  Heroku sets this up for us but we'll do it for now.
ENV PORT 80

# Run our CherryPy-based HTTP server.
CMD ["python3", "GameServer.py"]
