from invoke import run, task


@task
def protoc():
    run('mkdir -p hedgehog/proto/gen')
    run("protoc --proto_path=proto --python_out=. `find proto -name '*.proto'`")
