import docker

from config import LOCAL_USER_SCRIPTS_DIR

# Create a Docker client
client = docker.from_env()

# Create a container and start the container
container = client.containers.create(
    image='python:3.8-alpine',
    volumes=[f'{LOCAL_USER_SCRIPTS_DIR}:/tmp'],
    tty=True,
)
container.start()

try:
    result = container.exec_run(cmd='time -f "%e" python /tmp/python_script.py')
    exit_code: int = result.exit_code
    stdout: str = result.output.decode('utf-8')

    output, execution_time, _ = stdout.rsplit('\n', 2)
    execution_time = float(execution_time)

    print(exit_code)
    print(execution_time)
    print(f'OUTPUT:\n{output}')

except Exception as e:
    print(e)
finally:
    container.kill()
    container.remove()
