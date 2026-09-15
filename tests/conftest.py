import os
from pathlib import PurePath
from typing import Any, Generator

import pytest
from partisan.irods import Collection


@pytest.fixture(scope="function")
def tmp_irods_collection_path(tmp_path) -> Generator[PurePath, Any, None]:
    """A fixture providing a temporary iRODS collection."""
    root_path = PurePath("/testZone/home/irods/sangerdmtmp")
    if tmp_path.is_absolute():
        tmp_path = tmp_path.relative_to(tmp_path.anchor)
    coll_path = root_path / tmp_path
    coll = Collection(coll_path).create(exist_ok=True, parents=True)

    try:
        yield coll_path
    finally:
        coll.remove(recurse=True)


@pytest.fixture(scope="function")
def tmp_sample_collections(tmp_irods_collection_path):
    """
    A fixture that creates iRODS collection paths
    and makes a pre-made set of metadata available
    as a dictionary.
    """
    runfolder = "434895-20260110_0323"
    irods_runfolder_path = PurePath(tmp_irods_collection_path, runfolder)
    irods_items = {
        os.path.join(irods_runfolder_path, "434895-s1-Z0001-CAGCTCGAATGCGAT"): {
            "id_product": "244c6fce98d0261f25cedd81dbfcfc08e2207c954c8e25f471f5b6aaca144a32",
        },
        os.path.join(irods_runfolder_path, "434895-s2-Z0002-CATGTGCAGCCATCGAT"): {
            "id_product": "4710c1002d44c4dee326f91a663e223e6e8f64fe866ab84b7a5f264ae0028396",
        },
        os.path.join(irods_runfolder_path, "434895-s3-Z0003-CATCACACATGAATGAT"): {
            "id_product": "a32f711c95f4252d2318092977b242079a22480def01e1794baa3b51c416c8ee",
        },
        os.path.join(irods_runfolder_path, "434895-s4-Z0004-CTGTGTAGGCATGAT"): {
            "id_product": "00e23960e8c6b308dfbfc8859b600ec94567abd7f171f0ec916b886025b2ee63",
        },
    }

    for coll_path in irods_items.keys():
        Collection(coll_path).create(exist_ok=True, parents=True)

    return irods_items
