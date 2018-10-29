from invoke import run, task


@task
def gsl(context):
    from gsl_protocol_python import main

    main()


@task
def protoc(context):
    run("protoc --proto_path=proto --python_out=. `find proto -name '*.proto'`")
