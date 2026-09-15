import pytest
from pytest import mark as m

from partisan.irods import AVU


from partisan.irods import Collection
from sangerdm.irods.exception import (
    MultipleIRODSCollectionsFound,
    IRODSCollectionNotFound,
)
from sangerdm.irods.retrieval import (
    find_collections_by_id_products,
)

PRODUCT_METADATA_KEY = "id_product"


class TestIRODSRetrieval:
    @m.context("When sample iRODS collections have the requested id_products")
    @m.it("Returns all their iRODS locations")
    def test_find_collections_by_id_products(self, tmp_sample_collections):
        for irods_path, metadata in tmp_sample_collections.items():
            for a, v in metadata.items():
                Collection(irods_path).add_metadata(AVU(a, v))

        id_products = [
            "244c6fce98d0261f25cedd81dbfcfc08e2207c954c8e25f471f5b6aaca144a32",
            "4710c1002d44c4dee326f91a663e223e6e8f64fe866ab84b7a5f264ae0028396",
            "a32f711c95f4252d2318092977b242079a22480def01e1794baa3b51c416c8ee",
            "00e23960e8c6b308dfbfc8859b600ec94567abd7f171f0ec916b886025b2ee63",
        ]
        locations = find_collections_by_id_products("/testZone/home/irods", id_products)
        assert len(locations) == len(id_products)
        for id_product, irods_paths in locations.items():
            ipath = irods_paths.pop()
            assert ipath in list(tmp_sample_collections.keys())
            assert tmp_sample_collections[ipath][PRODUCT_METADATA_KEY] == id_product

    @m.context("When sample iRODS collections have the requested id_products")
    @m.context("When a sample iRODS collection does not exist")
    @m.it("Returns an empty list for the non-existing one")
    def test_find_collections_by_id_products_no_collection(
        self, tmp_sample_collections
    ):
        for irods_path, metadata in tmp_sample_collections.items():
            for a, v in metadata.items():
                Collection(irods_path).add_metadata(AVU(a, v))

        notexisting = "244c6fce98d0261f25cedd81dnotexisting7c954c8e25f471f5b6aaca144a32"
        existing = [
            "4710c1002d44c4dee326f91a663e223e6e8f64fe866ab84b7a5f264ae0028396",
            "a32f711c95f4252d2318092977b242079a22480def01e1794baa3b51c416c8ee",
            "00e23960e8c6b308dfbfc8859b600ec94567abd7f171f0ec916b886025b2ee63",
        ]
        locations = find_collections_by_id_products(
            "/testZone/home/irods", [notexisting] + existing
        )
        assert len(locations) == 4
        assert locations[notexisting] == []
        for id_product in existing:
            ipath = locations[id_product].pop()
            assert ipath in list(tmp_sample_collections.keys())
            assert tmp_sample_collections[ipath][PRODUCT_METADATA_KEY] == id_product

    @m.context("When sample iRODS collections have the requested id_products")
    @m.context("When a sample iRODS collection does not exist")
    @m.context("When each iRODS path is required to exist")
    @m.it("Raises IRODSCollectionNotFound exception")
    def test_find_collections_by_id_products_not_existing(self, tmp_sample_collections):
        for irods_path, metadata in tmp_sample_collections.items():
            for a, v in metadata.items():
                Collection(irods_path).add_metadata(AVU(a, v))

        id_products = [
            "244c6fce98d0261f25cedd81dnotexisting7c954c8e25f471f5b6aaca144a32",
            "4710c1002d44c4dee326f91a663e223e6e8f64fe866ab84b7a5f264ae0028396",
            "a32f711c95f4252d2318092977b242079a22480def01e1794baa3b51c416c8ee",
            "00e23960e8c6b308dfbfc8859b600ec94567abd7f171f0ec916b886025b2ee63",
        ]

        with pytest.raises(IRODSCollectionNotFound):
            find_collections_by_id_products(
                "/testZone/home/irods", id_products, exists=True
            )

    @m.context(
        "When the same sample product ID is assigned to multiple iRODS collections"
    )
    @m.context("When each iRODS path should be unique to an id_product")
    @m.it("Raises MultipleIRODSCollectionsFound exception")
    def test_find_collections_by_id_products_multiple_paths(
        self, tmp_sample_collections
    ):
        paths = list(tmp_sample_collections.keys())
        duplicated_id_product = tmp_sample_collections[paths[0]][PRODUCT_METADATA_KEY]
        tmp_sample_collections[paths[1]][PRODUCT_METADATA_KEY] = duplicated_id_product

        id_products = []
        for irods_path, metadata in tmp_sample_collections.items():
            id_products.append(metadata[PRODUCT_METADATA_KEY])
            for a, v in metadata.items():
                Collection(irods_path).add_metadata(AVU(a, v))

        with pytest.raises(MultipleIRODSCollectionsFound):
            find_collections_by_id_products(
                "/testZone/home/irods", id_products, unique=True
            )
