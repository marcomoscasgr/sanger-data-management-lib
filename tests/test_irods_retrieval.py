import pytest
from pytest import mark as m

from partisan.irods import AVU


from partisan.irods import Collection
from sangerdm.irods.exception import (
    MultipleIRODSCollectionsFound,
    IRODSCollectionNotFound,
)
from sangerdm.irods.retrieval import (
    find_collection_by_id_product,
    find_collections_by_id_products,
    find_allornone_collections_by_id_products,
)

PRODUCT_METADATA_KEY = "id_product"


class TestIRODSRetrieval:
    @m.context("When an iRODS collection has the requested id_product")
    @m.it("Returns its iRODS location")
    def test_find_collection_by_id_product(self, tmp_sample_collections):
        for irods_path, metadata in tmp_sample_collections.items():
            for a, v in metadata.items():
                Collection(irods_path).add_metadata(AVU(a, v))

        ipath = list(tmp_sample_collections.keys())[0]
        id_product = tmp_sample_collections[ipath][PRODUCT_METADATA_KEY]
        location = find_collection_by_id_product("/testZone/home/irods", id_product)
        assert location == ipath

    @m.context("When no iRODS collection has the requested id_product")
    @m.it("Raises IRODSCollectionNotFound error")
    def test_find_collection_by_id_product_no_collection(self, tmp_sample_collections):
        with pytest.raises(IRODSCollectionNotFound):
            find_collection_by_id_product(
                "/testZone/home/irods",
                "244c6fce98d0261f25cedd81dnotexisting7c954c8e25f471f5b6aaca144a32",
            )

    @m.context(
        "When the same sample product ID is assigned to multiple iRODS collections"
    )
    @m.it("Raises MultipleIRODSCollectionsFound error")
    def test_find_collection_by_id_product_multiple_ids(self, tmp_sample_collections):
        paths = list(tmp_sample_collections.keys())
        duplicated_id_product = tmp_sample_collections[paths[0]][PRODUCT_METADATA_KEY]
        tmp_sample_collections[paths[1]][PRODUCT_METADATA_KEY] = duplicated_id_product

        for irods_path, metadata in tmp_sample_collections.items():
            for a, v in metadata.items():
                Collection(irods_path).add_metadata(AVU(a, v))

        with pytest.raises(MultipleIRODSCollectionsFound):
            find_collection_by_id_product("/testZone/home/irods", duplicated_id_product)

    @m.context("When sample iRODS collections have the requested id_products")
    @m.context("When a sample iRODS collection does not exist")
    @m.it("Returns their iRODS locations except for the non-existing one")
    def test_find_collections_by_id_products(self, tmp_sample_collections):
        for irods_path, metadata in tmp_sample_collections.items():
            for a, v in metadata.items():
                Collection(irods_path).add_metadata(AVU(a, v))

        id_products = [
            "244c6fce98d0261f25cedd81dnotexisting7c954c8e25f471f5b6aaca144a32",
            "4710c1002d44c4dee326f91a663e223e6e8f64fe866ab84b7a5f264ae0028396",
            "a32f711c95f4252d2318092977b242079a22480def01e1794baa3b51c416c8ee",
            "00e23960e8c6b308dfbfc8859b600ec94567abd7f171f0ec916b886025b2ee63",
        ]
        locations = find_collections_by_id_products("/testZone/home/irods", id_products)
        assert len(locations) == 3
        for id_product, irods_path in locations.items():
            assert irods_path in list(tmp_sample_collections.keys())
            assert (
                tmp_sample_collections[irods_path][PRODUCT_METADATA_KEY] == id_product
            )

    @m.context("When sample iRODS collections have the requested id_products")
    @m.it("Returns all their iRODS locations")
    def test_find_allornone_collections_by_id_products(self, tmp_sample_collections):
        for irods_path, metadata in tmp_sample_collections.items():
            for a, v in metadata.items():
                Collection(irods_path).add_metadata(AVU(a, v))

        id_products = [
            "244c6fce98d0261f25cedd81dbfcfc08e2207c954c8e25f471f5b6aaca144a32",
            "4710c1002d44c4dee326f91a663e223e6e8f64fe866ab84b7a5f264ae0028396",
            "a32f711c95f4252d2318092977b242079a22480def01e1794baa3b51c416c8ee",
            "00e23960e8c6b308dfbfc8859b600ec94567abd7f171f0ec916b886025b2ee63",
        ]
        locations = find_allornone_collections_by_id_products(
            "/testZone/home/irods", id_products
        )
        assert len(locations) == len(id_products)
        for id_product, irods_path in locations.items():
            assert irods_path in list(tmp_sample_collections.keys())
            assert (
                tmp_sample_collections[irods_path][PRODUCT_METADATA_KEY] == id_product
            )
