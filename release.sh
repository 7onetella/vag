#!/bin/bash -e

poetry version patch --no-ansi
new_version=$(cat pyproject.toml | grep "^version = \"*\"" | cut -d'"' -f2)
sed -i.bak "s/__version__ = .*/__version__ = \"${new_version}\"/g" vag/__init__.py
rm -f vag/__init__.py.bak

poetry install
poetry build

poetry publish -u $PYPI_USERNAME -p $PYPI_PASSWORD

git add pyproject.toml
git add vag/__init__.py
git commit -m "releasing ${new_version}"
git push -u origin
git tag vag-${new_version}
git push origin tag vag-${new_version}