using OpenTK.Mathematics;
using SFEngine.SFCFF.CTG;
using System.Collections.Generic;
using System.Linq;

namespace SFEngine.SFMap
{
    public class SFMapObject : SFMapEntity
    {
        static int max_id = 0;

        public int unknown1 = 0;
        public bool block_movement_terrain = false;  // When true, sets TERRAIN_MOVEMENT flag on terrain tiles underneath object (visible in terrain view)

        public override string GetName()
        {
            return "OBJECT_" + id.ToString();
        }

        public SFMapObject()
        {
            id = max_id;
            max_id += 1;
        }
    }

    public class SFMapObjectManager
    {
        public List<SFMapObject> objects { get; private set; } = new List<SFMapObject>();
        // object game id, collision boundary
        public Dictionary<ushort, SFMapCollisionBoundary> object_collision { get; private set; } = new Dictionary<ushort, SFMapCollisionBoundary>();
        public SFMap map = null;

        public void AddObjectCollisionBoundary(int id)
        {
            // add new collision boundary (PENDING TESTS!!!!!!!!!!!)
            if (object_collision.ContainsKey((ushort)id))
            {
                return;
            }

            // Check if game data is loaded
            if (SFCFF.SFCategoryManager.gamedata == null || SFCFF.SFCategoryManager.gamedata.c2057 == null)
            {
                LogUtils.Log.Warning(LogUtils.LogSource.SFMap, $"AddObjectCollisionBoundary: Game data not loaded for object {id}");
                return;
            }

            bool outline_found = SFCFF.SFCategoryManager.gamedata.c2057.GetItemIndex(id, out int outline_index);
            if (!outline_found)
            {
                LogUtils.Log.Info(LogUtils.LogSource.SFMap, $"AddObjectCollisionBoundary: No collision data for object {id}");
                return;
            }
            int outline_num = SFCFF.SFCategoryManager.gamedata.c2057.GetItemSubItemNum(outline_index);
            outline_index = SFCFF.SFCategoryManager.gamedata.c2057.Indices[outline_index];

            SFMapCollisionBoundary cb = new SFMapCollisionBoundary() { origin = Vector2.Zero };
            int total_vertices = 0;
            for (int i = 0; i < outline_num; i++)
            {
                Category2057Item outline = SFCFF.SFCategoryManager.gamedata.c2057[outline_index];

                int vertex_count = outline.Coords.Count / 2;
                total_vertices += vertex_count;
                Vector2[] vertex_list = new Vector2[vertex_count];
                for (int j = 0; j < vertex_count; j++)
                {
                    vertex_list[j] = new Vector2();
                    vertex_list[j].X = outline.Coords[j * 2 + 0] / 140.0f;
                    vertex_list[j].Y = outline.Coords[j * 2 + 1] / 140.0f;
                }
                cb.polygons.Add(new SFMapCollisionPolygon2D(vertex_list, Vector2.Zero));

                outline_index++;
            }

            LogUtils.Log.Info(LogUtils.LogSource.SFMap, $"AddObjectCollisionBoundary: Object {id} has {outline_num} polygons with {total_vertices} total vertices");

            object_collision.Add((ushort)id, cb);
        }

        public int AddObject(int id, SFCoord position, int angle, int npc, int unk1, int index = -1)
        {
            AddObjectCollisionBoundary(id);

            SFMapObject obj = new SFMapObject();
            obj.grid_position = position;
            obj.game_id = id;
            obj.angle = angle;
            obj.npc_id = npc;
            obj.unknown1 = unk1;

            if (index == -1)
            {
                index = objects.Count;
            }

            objects.Insert(index, obj);

            string obj_name = obj.GetName();

            obj.node = SF3D.SFRender.SFRenderEngine.scene.AddSceneObject(id, obj_name, true, true);
            // custom resource mesh setting :^)
            ObjectSetResourceIfAvailable(id, obj.node);

            obj.node.SetParent(map.heightmap.GetChunkNode(position));

            map.heightmap.SetFlag(position, SFMapHeightMapFlag.ENTITY_OBJECT, true);
            ApplyObjectBlockFlags(obj.grid_position, obj.angle, (ushort)obj.game_id, true);

            SF3D.SceneSynchro.SceneNode _obj = obj.node;
            _obj.Position = map.heightmap.GetFixedPosition(position);
            _obj.Scale = new Vector3(100 / 128.0f);
            _obj.SetAnglePlane(angle);
            map.UpdateNodeDecal(_obj, new Vector2(position.x, position.y), Vector2.Zero, angle);

            map.heightmap.GetChunk(position).objects.Add(obj);

            return index;
        }

        public void RemoveObject(int object_index)
        {
            SFMapObject obj = objects[object_index];

            objects.RemoveAt(object_index);

            SF3D.SceneSynchro.SceneNode obj_node = obj.node;
            if (obj_node != null)
            {
                SF3D.SFRender.SFRenderEngine.scene.RemoveSceneNode(obj_node);
            }

            map.heightmap.GetChunk(obj.grid_position).objects.Remove(obj);

            map.heightmap.SetFlag(obj.grid_position, SFMapHeightMapFlag.ENTITY_OBJECT, false);
            ApplyObjectBlockFlags(obj.grid_position, obj.angle, (ushort)obj.game_id, false);
        }

        public void ReplaceObject(int object_index, ushort new_object_id)
        {
            SFMapObject obj = objects[object_index];

            if (obj.node != null)
            {
                SF3D.SFRender.SFRenderEngine.scene.RemoveSceneNode(obj.node);
            }

            obj.node = SF3D.SFRender.SFRenderEngine.scene.AddSceneObject(new_object_id, obj.GetName(), true, true);
            obj.node.SetParent(map.heightmap.GetChunkNode(obj.grid_position));

            AddObjectCollisionBoundary(new_object_id);

            ApplyObjectBlockFlags(obj.grid_position, obj.angle, (ushort)obj.game_id, false);
            obj.game_id = new_object_id;
            ApplyObjectBlockFlags(obj.grid_position, obj.angle, (ushort)obj.game_id, true);

            // object transform
            float z = map.heightmap.GetZ(obj.grid_position) / 100.0f;
            obj.node.Position = map.heightmap.GetFixedPosition(obj.grid_position);
            obj.node.Scale = new Vector3(100 / 128f);
            obj.node.SetAnglePlane(obj.angle);
            map.UpdateNodeDecal(obj.node, new Vector2(obj.grid_position.x, obj.grid_position.y), Vector2.Zero, obj.angle);
        }

        public void RotateObject(int object_map_index, int angle)
        {
            SFMapObject obj = objects[object_map_index];

            ApplyObjectBlockFlags(obj.grid_position, obj.angle, (ushort)obj.game_id, false);
            obj.angle = angle;
            ApplyObjectBlockFlags(obj.grid_position, obj.angle, (ushort)obj.game_id, true);

            obj.node.SetAnglePlane(angle);
            map.UpdateNodeDecal(obj.node, new Vector2(obj.grid_position.x, obj.grid_position.y), Vector2.Zero, obj.angle);
        }

        public void MoveObject(int object_map_index, SFCoord new_pos)
        {
            SFMapObject obj = objects[object_map_index];

            // move unit and set chunk dependency
            map.heightmap.GetChunkNode(obj.grid_position).MapChunk.objects.Remove(obj);
            map.heightmap.SetFlag(obj.grid_position, SFMapHeightMapFlag.ENTITY_OBJECT, false);
            ApplyObjectBlockFlags(obj.grid_position, obj.angle, (ushort)obj.game_id, false);
            obj.grid_position = new_pos;
            ApplyObjectBlockFlags(obj.grid_position, obj.angle, (ushort)obj.game_id, true);
            map.heightmap.SetFlag(obj.grid_position, SFMapHeightMapFlag.ENTITY_OBJECT, true);
            map.heightmap.GetChunkNode(obj.grid_position).MapChunk.objects.Add(obj);
            obj.node.SetParent(map.heightmap.GetChunkNode(obj.grid_position));

            // change visual transform
            float z = map.heightmap.GetZ(new_pos) / 100.0f;
            obj.node.Position = map.heightmap.GetFixedPosition(new_pos);
            map.UpdateNodeDecal(obj.node, new Vector2(obj.grid_position.x, obj.grid_position.y), Vector2.Zero, obj.angle);
        }

        public void ApplyObjectBlockFlags(SFCoord pos, int angle, ushort id, bool set)
        {
            // Find the object to check for terrain movement blocking
            SFMapObject obj = objects.FirstOrDefault(o => o.game_id == id && o.grid_position == pos);

            // block_movement_terrain: when true, sets movement blocking flags on terrain tiles under object
            bool set_blocking = set && obj != null && obj.block_movement_terrain;

            if (!object_collision.ContainsKey(id))
            {
                // Set/clear flags based on checkbox
                map.heightmap.SetFlag(pos, SFMapHeightMapFlag.TERRAIN_MOVEMENT, set_blocking);
                map.heightmap.SetFlag(pos, SFMapHeightMapFlag.FLAG_MOVEMENT, set_blocking);
                return;
            }

            // Set/clear flags on all cells covered by the object's collision boundary
            SFMapCollisionBoundary bcb = object_collision[(ushort)id];
            foreach (SFCoord p in bcb.GetCells(pos, angle))
            {
                map.heightmap.SetFlag(p, SFMapHeightMapFlag.TERRAIN_MOVEMENT, set_blocking);
                map.heightmap.SetFlag(p, SFMapHeightMapFlag.FLAG_MOVEMENT, set_blocking);
            }
        }

        /// <summary>
        /// Sets or clears movement blocking flags for a specific object.
        /// This sets both TERRAIN_MOVEMENT (for editor display) and FLAG_MOVEMENT (for game blocking).
        /// </summary>
        public void SetObjectTerrainMovementFlag(SFMapObject obj, bool set)
        {
            var tiles = GetObjectBlockingTiles(obj);
            foreach (SFCoord p in tiles)
            {
                // TERRAIN_MOVEMENT: visual display in editor overlay
                map.heightmap.SetFlag(p, SFMapHeightMapFlag.TERRAIN_MOVEMENT, set);
                // FLAG_MOVEMENT: actual game movement blocking (saved to chunk 42)
                map.heightmap.SetFlag(p, SFMapHeightMapFlag.FLAG_MOVEMENT, set);
            }
        }
        
        /// <summary>
        /// Gets all tiles that should block movement for an object.
        /// Used when saving the map to include these tiles in chunk 42.
        /// </summary>
        public List<SFCoord> GetObjectBlockingTiles(SFMapObject obj)
        {
            List<SFCoord> tiles = new List<SFCoord>();
            
            // Try to load collision boundary if not already loaded
            if (!object_collision.ContainsKey((ushort)obj.game_id))
            {
                AddObjectCollisionBoundary(obj.game_id);
            }
            
            if (object_collision.ContainsKey((ushort)obj.game_id))
            {
                // Get all cells covered by the object's collision boundary
                SFMapCollisionBoundary bcb = object_collision[(ushort)obj.game_id];
                foreach (SFCoord p in bcb.GetCells(obj.grid_position, obj.angle))
                {
                    // Bounds check
                    if (p.x >= 0 && p.y >= 0 && map != null && 
                        p.x < map.heightmap.width && p.y < map.heightmap.height)
                    {
                        tiles.Add(p);
                    }
                }
            }
            
            // If no collision boundary or it returned no tiles, use default 3x3
            if (tiles.Count == 0)
            {
                for (int dx = -1; dx <= 1; dx++)
                {
                    for (int dy = -1; dy <= 1; dy++)
                    {
                        int nx = obj.grid_position.x + dx;
                        int ny = obj.grid_position.y + dy;
                        if (nx >= 0 && ny >= 0 && map != null && 
                            nx < map.heightmap.width && ny < map.heightmap.height)
                        {
                            tiles.Add(new SFCoord((short)nx, (short)ny));
                        }
                    }
                }
            }
            
            return tiles;
        }

        public bool ObjectIDIsReserved(int obj_id)
        {
            if ((obj_id == 65) || (obj_id == 66) || (obj_id == 67))   // editor flags (ignored)
            {
                return true;
            }

            if ((obj_id == 769) || (obj_id == 778))                  // bindstone, world portal
            {
                return true;
            }

            if ((obj_id >= 771) && (obj_id <= 777))                   // monuments
            {
                return true;
            }

            if (obj_id == 2541)                                       // spawn point
            {
                return true;
            }

            return false;
        }

        public void ObjectSetResourceIfAvailable(int obj_id, SF3D.SceneSynchro.SceneNode node)
        {
            string mesh_obj_name = "";
            string mesh_decal_name = "";
            // berries
            if ((obj_id >= 0x80) && (obj_id < 0x80 + 6))
            {
                mesh_obj_name = "nature_berry_" + (obj_id - 0x80 + 1).ToString("00");
                mesh_decal_name = "nature_berry_decal";
            }
            else if (obj_id == 0x300)
            {
                mesh_obj_name = "nature_wheat_step06";
                mesh_decal_name = "nature_wheat_decal";
            }
            else if (obj_id == 0x302)
            {
                mesh_obj_name = "nature_mushroom_06";
            }
            else if ((obj_id >= 0x100) && (obj_id < 0x100 + 9))
            {
                mesh_obj_name = "nature_crushable_rock" + (obj_id - 0x100 + 1).ToString();
                mesh_decal_name = "nature_crushable_rock_decal";
            }
            else if ((obj_id >= 0x580) && (obj_id < 0x580 + 9))
            {
                mesh_obj_name = "nature_lenya_" + (obj_id - 0x580 + 1).ToString("00");
                mesh_decal_name = "nature_lenya_decal";
            }
            else if ((obj_id >= 0x600) && (obj_id < 0x600 + 9))
            {
                mesh_obj_name = "nature_iron_" + (obj_id - 0x600 + 1).ToString("00");
                mesh_decal_name = "nature_iron_decal";
            }
            else if ((obj_id >= 0x680) && (obj_id < 0x680 + 9))
            {
                mesh_obj_name = "nature_mitthril_" + (obj_id - 0x680 + 1).ToString("00");
                mesh_decal_name = "nature_mithril_decal";
            }

            if (mesh_obj_name != "")
            {
                if (node.children.Count == 1)
                {
                    SF3D.SFRender.SFRenderEngine.scene.RemoveSceneNode(node.children[0]);         // remove missing mesh node
                }
                SF3D.SFRender.SFRenderEngine.scene.AddSceneNodeSimple(node, mesh_obj_name, "0");
                SF3D.SFRender.SFRenderEngine.scene.AddSceneNodeSimple(node, mesh_decal_name, "0");
            }
        }
    }
}
