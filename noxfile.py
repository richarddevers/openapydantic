from nox_poetry import session

python_version = ["3.8"]
source = "openapydantic/"


@session(python=python_version)
def security(session):
    session.install("bandit", "safety")
    session.run("bandit", source)
    session.run("safety", "check")


@session(python=python_version)
def quality(session):
    session.install("flake8", "isort", "black")
    session.run("flake8", source)
    session.run("isort", "-c", source)
    session.run("black", "--check", source)


@session(python=python_version)
def test(session):
    session.install("pytest")
    session.run("poetry", "update")
    session.run("poetry", "run", "pytest")
