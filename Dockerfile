# Use an official Python runtime as our parent image.  Notice that it is windows-based.
# We need this so that, in theory, our .pyd file will run, since it targets windows with 64-bit Python installed.
FROM python:3.6.6-windowsservercore-ltsc2016

# Here I think we're creating a new directory called "opt/webapp" in the image's file system,
# and then copying all of our crap into that directory.
ADD . /opt/webapp
WORKDIR /opt/webapp

# Make sure our module dependencies are installed, except for our custom dependencies, of course.
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Note that this is not supported by heroku.  We'll be using the $PORT env-var instead.
# EXPOSE 80

# This is just for testing purposes.  Heroku sets this up for us but we'll do it for now.
# ENV PORT 80

# Run our CherryPy-based HTTP server.
CMD ["python", "GameServer.py"]