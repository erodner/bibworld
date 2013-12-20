FaPuLi - fast publication lists

FaPuLi is a tool to create HTML publications lists

author: Erik Rodner (Erik.Rodner (at) uni-jena.de)



Deploying the flask app
--------------------------------------------

There are many ways to deploy a flask app. An easy way is to use the nginx webserver and uwsgi as a middleware component (with python and http plugin!). An example
nginx config is part of this package and the nginx server can be started with:

```
uwsgi --plugins http,python --no-site -s /tmp/uwsgi.sock -w fapuliserver:app --pythonpath /usr/lib/python2.7/site-packages/ --pythonpath /usr/lib64/python2.7/site-packages/ --chmod-socket=666
```

Enjoy!


