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


def find_collection_by_id_product(pipeline_coll: str, id_product: str) -> str:
    """
    Retrieve the iRODS path of a sample collection through its specific `id_product`.
    If an id_product is not related to any iRODS collections, the function will raise an
    exception.

    Args:
        pipeline_coll (str):
            iRODS path to pipeline collection.
        id_product [str]:
            Unique ID of a sequencing product.

    Raises:
        Exception:
            (IRODSCollectionNotFound): No location related to the `id_product` in iRODS.
            (MultipleIRODSCollectionsFound): More than one location is found in iRODS for a product ID.

    Returns:
        (str): iRODS path.
    """
    query = [
        AVU(PRODUCT_METADATA_KEY, id_product),
    ]
    query_response = query_metadata(*query, data_object=False, zone=pipeline_coll)
    if not query_response:
        raise IRODSCollectionNotFound(f"product ID '{id_product}'")
    if len(query_response) > 1:
        raise MultipleIRODSCollectionsFound(f"product ID '{id_product}'")

    collection = query_response.pop()
    log.debug(f"Found '{collection}' related to product ID '{id_product}'")
    return str(collection)


def find_collections_by_id_products(
    pipeline_coll: str, id_products: list[str]
) -> dict[str, str]:
    """
    Retrieve the iRODS paths of sample collections through their specific `id_product`.
    This iRODS path retrieval function doesn't raise. The function will return only
    the paths that exist and are unique (i.e. if there are multiple collections from
    an id_product, that id_product is not considered).

    Args:
        pipeline_coll (str):
            iRODS path to pipeline collection.
        id_products (list[str]):
            A list of unique IDs of sequencing products.

    Returns:
        dict[str,str]:
            * key (str): sample product ID.
            * value (str): iRODS path.
    """
    product_locations = {}
    for id_product in id_products:
        try:
            product_locations[id_product] = find_collection_by_id_product(
                pipeline_coll=pipeline_coll, id_product=id_product
            )
        except MultipleIRODSCollectionsFound as micf:
            log.info(str(micf), exc_info=True)
        except IRODSCollectionNotFound as icnf:
            log.info(str(icnf), exc_info=True)
    return product_locations


def find_allornone_collections_by_id_products(
    pipeline_coll: str, id_products: list[str]
) -> dict[str, str]:
    """
    Retrieve the iRODS paths of sample collections through their specific `id_product`.
    There must be only one iRODS path for each id_product to successfully call this
    function. Moreover, all products must have an existing path.

    Otherwise throws exceptions same as 'find_collection_by_id_product' function

    Args:
        pipeline_coll (str):
            iRODS path to pipeline collection.
        id_products (list[str]):
            A list of unique IDs of sequencing products.

    Returns:
        dict[str,str]:
            * key (str): sample product ID.
            * value (str): iRODS path.
    """
    product_locations = {}
    for id_product in id_products:
        product_locations[id_product] = find_collection_by_id_product(
            pipeline_coll=pipeline_coll, id_product=id_product
        )
    return product_locations
