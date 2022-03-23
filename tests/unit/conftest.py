"""Defines fixtures available to all tests."""

import enum
import json
import os
import typing as t

import pydantic
import pytest
import yaml

JsonObject = t.Dict[t.Any, t.Any]


class FixtureExpectedStatus(enum.Enum):
    ok = "ok"
    ko = "ko"


class FixturesVersion(pydantic.BaseModel):
    ok: t.List[str]
    ko: t.List[str]


class SpecVersion(enum.Enum):
    v3_0_0 = "v3.0.0"
    v3_0_1 = "v3.0.1"
    v3_0_2 = "v3.0.2"
    v3_0_3 = "v3.0.3"
    v3_1_0 = "v3.1.0"


def load_yaml(filename: str) -> JsonObject:
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath) as yaml_file:
        return yaml.safe_load(yaml_file.read())  # type: ignore


class FixtureLoader(pydantic.BaseModel):
    fixture_dir: str

    def load_file(self, filename: str) -> str:
        filepath = os.path.join(self.fixture_dir, filename)
        with open(filepath) as file:
            return file.read()

    def load_json(self, filename: str) -> JsonObject:
        data = self.load_file(filename)
        return json.loads(data)  # type: ignore

    def load_yaml(self, filename: str) -> JsonObject:
        data = self.load_file(filename)
        return yaml.safe_load(data)  # type: ignore


@pytest.fixture
def fixture_loader(request: t.Any) -> FixtureLoader:
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    return FixtureLoader(fixture_dir=os.path.join(os.path.dirname(filename), "fixture"))


def list_specific_fixtures_version(
    version: SpecVersion,
) -> FixturesVersion:

    ok_dir: str = os.path.join(
        os.path.dirname(__file__),
        version.value,
        "fixture",
        FixtureExpectedStatus.ok.value,
    )
    ko_dir: str = os.path.join(
        os.path.dirname(__file__),
        version.value,
        "fixture",
        FixtureExpectedStatus.ko.value,
    )

    fixtures_ok: t.List[str] = []
    fixtures_ko: t.List[str] = []

    fixtures_ok_files = [file for file in os.walk(ok_dir)][0][-1]
    for file in fixtures_ok_files:
        fixtures_ok.append(os.path.join(ok_dir, file))

    fixtures_ko_files = [file for file in os.walk(ko_dir)][0][-1]
    for file in fixtures_ko_files:
        fixtures_ko.append(os.path.join(ok_dir, file))

    return FixturesVersion(
        ok=fixtures_ok,
        ko=fixtures_ko,
    )
