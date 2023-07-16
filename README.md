# astrobase_tasks

![](docs/astrobase-architecture.png)

### astrobase
``astrobase_tasks`` is not a standalone package, but an addition to the ``astrobase`` project.
 ``Astrobase`` is a Django web application that wraps my observation database in a REST API, 
so that it can be accessed by a GUI (``AstroView``) and by the ``astrobase_tasks`` package. 

``Astrobase`` is also a (Django) backend that implements a number of data services, 
like importing external resources like comets, minor planets, exoplanets and stars.
And it is a controler for 'jobs' for plate solving and plotting additional information on the images.

### astrobase_tasks
This repo, ``astrobase_tasks``, is developed and deployed separately from ``astrobase`` 
and contains the underlying functionality for the 'jobs' mentioned above.
It runs various (async) tasks using Celery with RabbitMQ.

## The Technology Stack
  * Python 3.10
  * Celery
  * RabbitMQ

### Celery with RabbitMQ
There are 3 types of tasks that can be run simultaneously on 3 different Celery message queues
* registration jobs: 'plate solve' an image to nova.astronomy.net'and download the results (starchart, fits files)
* imaging job: plot information on an image (grid, stars, transients, exoplanets)
* image cutout of a list of images

(inspired by : https://www.distributedpython.com/2018/11/15/celery-docker/)


### Docker
``astrobase_tasks`` runs in Docker together with some other services.
(The ``docker-compose.yml`` file is not provided in this repo)

* astrobase backend (REST API to the sqlite database)
  * observations (not needed for ``astrobase_tasks package``) 
  * jobs, contains all information to fire off task in ``astrobase_tasks``
  * exoplanets, updated data about all the confirmed exoplanets

* rabbitMQ (message broker used by Celery)
* celery_beat (another instance of the ``astrobase_tasks`` image that provides the 'heartbeat' to check for new tasks)
  
![](docs/astrobase_tasks.png)


## The Functionality

### registration_controller.py
The registration pipeline handles the plate solving at astrometry.net


### jobs_controller.py
Handles incoming jobs from ``astrobase``.

It polls the astrobase `jobs` API at an interval through the ``AstrobaseIO`` interface package.
The job contains all the information to start the task 

### fits_imaging.py
This module uses ``astropy`` and ``pillow`` to combine the WCS coordinatesystem in the fits file with plotting functionality on images.
There are a number of functions to plot various items:
* coordinate grid
* the stars and their magnitudes as used by astrometry.net for plate solving
* markers of different types and colors at coordinates, used for transients and exoplanets
* create image cutouts
