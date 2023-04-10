from typing import Tuple, Dict, DefaultDict
import spark_dsg
import copy

import numpy as np
import networkx as nx
from collections import defaultdict

from .constants import OBJECT_ID_TO_LABEL

from .scenegraph import *


def dsg_loader(path: str) -> Building:
    """Load a 3D scene graph.

    args:
        path: path to a Spark-DSG dsg.json file.

    returns:
        building: 3D scene graph building
    """
    print('dsg_loader started')
    G = spark_dsg.DynamicSceneGraph.load(path)
    building = Building()
    building.voxel_size = .5 # TODO: ??

    # Set room attributes
    rid_to_index = {n.id.value : ix for ix, n in enumerate(G.get_layer(spark_dsg.DsgLayers.ROOMS).nodes)}

    for r in G.get_layer(spark_dsg.DsgLayers.ROOMS).nodes:

        room_index = rid_to_index[r.id.value]
        building.room[room_index] = Room()
        building.room[room_index].id = room_index

        building.room[room_index].location = copy.copy(r.attributes.position)

        ## This would be used if we had room semantic labels, e.g. from Matterport
        #semantic_label = ROOM_LABELS[ROOM_INDEX[chr(r.attributes.semantic_label)]]
        #building.room[room_index].scene_category = semantic_label
        building.room[room_index].scene_category = 'tbd'

        # add connectivity information
        for r2 in r.siblings():
            r2_index = rid_to_index[G.get_node(r2).id.value]
            building.room[room_index].connected_rooms.add(r2_index)

    # Set object attributes

    oid_to_index = {n.id.value : ix for ix, n in enumerate(G.get_layer(spark_dsg.DsgLayers.OBJECTS).nodes)}
    for o in G.get_layer(spark_dsg.DsgLayers.OBJECTS).nodes:
        if o.get_parent() is None:
            continue
        place = G.get_node(o.get_parent())
        if place.get_parent() is None:
            continue

        parent_room = G.get_node(place.get_parent())
        parent_room_index = rid_to_index[parent_room.id.value] 

        object_index = oid_to_index[o.id.value]

        object_class_index = o.attributes.semantic_label
        object_class = OBJECT_ID_TO_LABEL[object_class_index]

        building.object[object_index] = SceneObject()
        building.object[object_index].id = object_index
        building.object[object_index].class_ = object_class
        building.object[object_index].parent_room = parent_room_index
        building.object[object_index].location = o.attributes.position

    print('dsg_loader finished')
    return building

