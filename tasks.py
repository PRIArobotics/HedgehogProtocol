from invoke import run, task


@task
def protoc(context):
    run("protoc --proto_path=proto --python_out=. `find proto -name '*.proto'`")


@task
def gsl(context):
    run("gsl gsl/protocol.xml")
