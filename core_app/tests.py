from pathlib import Path

import pytest
import yaml
from django.conf import settings


# Implement a no-op so that the real sqlite db is used for tests during refactoring
@pytest.fixture(scope="session")
def django_db_setup():
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.mysql",
        "HOST": "db.example.com",
        "NAME": "external_db",
    }


def describe_safety_net_for_refactoring():
    @pytest.mark.skipif(Path("all_pages.yaml").exists(), reason="CheckFile")
    def test_create_oracle_for_all_pages(client, db):
        assert client.login(username="siraj", password="kevin123")
        response = client.get("/student/1/all/")
        pages_all = response.context["pages_all"]

        with open("all_pages.yaml", "w") as file:
            yaml.dump(pages_all, file)

    @pytest.fixture()
    def all_pages_oracle():
        with open("all_pages.yaml") as file:
            return yaml.load(file)

    # We generate a reference file that will store all the stats generated by the current program so that each time we refactor,
    # we can check against the reference file to ensure that the refactoring did not break the algorithm.
    # Since the algorithm regenerates the due pages data every day, this file needs to be regenerated every day.
    # Then we want to store the ouput of the algorithm(next_interval and scheduled_due_date) into the DB directly
    # so that we can fetch it directly from DB rather than processing all the revisions for all the pages every time
    # either the Due pages or All pages are visited. After this is done, then this test and the yaml file can be retired.
    def compare_with_oracle(all_pages_oracle, client, db):
        assert client.login(username="siraj", password="kevin123")
        response = client.get("/student/1/all/")
        assert response.context["pages_all"] == all_pages_oracle

