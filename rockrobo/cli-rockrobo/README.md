# Rockrobo customized

**Description**
A simple command line interface for working with CVAT tasks. At the moment it
implements a basic feature set but may serve as the starting point for a more
comprehensive CVAT administration tool in the future.

**Usage**

```bash
usage: cli.py [-h] [--auth USER:[PASS]] [--server-host SERVER_HOST]
              [--server-port SERVER_PORT] [--debug]
              {create,delete,ls,frames,dump} ...

Perform common operations related to CVAT tasks.

positional arguments:
  {create,delete,ls,frames,dump}

optional arguments:
  -h, --help            show this help message and exit
  --auth USER:[PASS]    defaults to the current user and supports the PASS
                        environment variable or password prompt.
  --server-host SERVER_HOST
                        host (default: localhost)
  --server-port SERVER_PORT
                        port (default: 8080)
  --https
                        using https connection (default: False)
  --debug               show debug output
```

**Examples**

- List all tasks
  ```
  python ./cli.py \
    --auth root:rockrobo \
    --server-host localhost \
    --server-port 7000 \
    ls
  ```

- Create a task
  ```
  python ./cli.py \
    --auth root:rockrobo \
    --server-host localhost \
    --server-port 7000 \
    create task-from-cli \
    --labels ./assets/baiguang-labels.json \
    local ./assets/test-images-dir
  ```

- Delete some tasks
  ```
  python ./cli.py \
    --auth root:rockrobo \
    --server-host localhost \
    --server-port 7000 \
    delete 5
  ```

- Dump annotations
  ```
  python ./cli.py \
    --auth root:rockrobo \
    --server-host localhost \
    --server-port 7000 \
    dump \
    --format "CVAT for images 1.1" \
    4 \
    ./output.xml
  ```
