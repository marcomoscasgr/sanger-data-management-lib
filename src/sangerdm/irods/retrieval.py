# -*- coding: utf-8 -*-
#
# Copyright © 2026 Genome Research Ltd. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import structlog

from partisan.irods import AVU, query_metadata
from sangerdm.irods.exception import (
    IRODSCollectionNotFound,
    MultipleIRODSCollectionsFound,
)

log = structlog.get_logger(__package__)

PRODUCT_METADATA_KEY = "id_product"


def find_collections_by_id_products(
    pipeline_coll: str,
    id_products: list[str],
    unique: bool = False,
    exists: bool = False,
) -> dict[str, list[str]]:
    """
    Retrieve the iRODS paths of sample collections through their specific `id_product`.

    Args:
        pipeline_coll (str):
            iRODS path to pipeline collection.
        id_products (list[str]):
            A list of unique IDs of sequencing products.
        unique (bool):
            True - It raises MultipleIRODSCollectionsFound when an id_product
            is assigned to multiple collections. Otherwise store all collections
            found for that `id_product`. Default to False.
        exists (bool):
            True - It raises IRODSCollectionNotFound when there is no collection
            assigned to an `id_product`. Otherwise store an empty list for that
            `id_product`. Default to False.

    Raises:
        with exists=True (IRODSCollectionNotFound):
            No location related to the `id_product` in iRODS.
        with unique=True (MultipleIRODSCollectionsFound):
            More than one location is found in iRODS for a product ID.

    Returns:
        dict[str,list[str]]:
            * key (str): sample product ID.
            * value (list[str]): iRODS paths associated to the product ID.
    """
    product_locations = {}
    for id_product in id_products:
        query = [
            AVU(PRODUCT_METADATA_KEY, id_product),
        ]
        collections = query_metadata(*query, data_object=False, zone=pipeline_coll)
        if not collections and exists:
            raise IRODSCollectionNotFound(f"product ID '{id_product}'")
        if len(collections) > 1 and unique:
            raise MultipleIRODSCollectionsFound(f"product ID '{id_product}'")

        log.debug(
            f"Found {len(collections)} collections related to product ID '{id_product}'"
        )

        product_locations[id_product] = []
        if not collections:
            continue
        for collection in collections:
            log.debug(f"Found '{collection}' related to product ID '{id_product}'")
            product_locations[id_product].append(str(collection))
    return product_locations
