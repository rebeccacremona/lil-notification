'li notification
================

A proof-of-concept: can we use websockets to alert users about upcoming deployments, and prevent confusion on ajax-heavy, infrequently refreshed pages?

Runnng Locally
--------------

### Up

1. Install [Docker](https://docs.docker.com/installation/) or [Docker Toolbox](https://www.docker.com/products/docker-toolbox)

2. `git clone git@github.com:rebeccacremona/lil-notification.git`

3. `cd lil-notification`

4. (recommended) Nickname some commonly-used commands by adding the following to your .bash_profile or similar:
`alias dfab="docker-compose exec web fab"`
`alias dmanage.py="docker-compose exec web manage.py"`

5. Run `docker-compose up -d` to start two containers in the background:
    -  a "db" container with a postgres database
    -  a "web" container with python, Django, and the rest of our dev environment.

6. Run `dfab init_db` to initialize a development database.

7. Run `dfab run` to start the Django development server.

8. Log in to `/admin` with the credentials admin/admin and create one or more "Applications".

9. In one or more tabs or windows, open a page that listens in real time for your Application's maintenance events: `/:slug/:tier/`

10. Using the Django admin or the api (POST to `/api/applications/:id/maintenance-events/`), create a Maintenance Event.

11. See all your open tabs and windows flash a notification in real time.

12. Using the Django admin or the api (PATCH to `/api/maintenance-events/:id/`), make changes to your Maintenance Event: update the status, change associated times, etc. Watch your open tabs and windows update themselves.


### Down

To stop all running containers (and retain any information in your database), run `docker-compose stop`.
