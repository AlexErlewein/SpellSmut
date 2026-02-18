using System;
using System.Drawing;
using System.Windows.Forms;

namespace SpellforceDataEditor.SFMap.map_controls
{
    public enum TerrainTileType { NONE, BASE, CUSTOM };

    public partial class MapTerrainTextureInspector : SpellforceDataEditor.SFMap.map_controls.MapInspector
    {
        TerrainTileType inspectortype = TerrainTileType.NONE;
        private bool tile_properties_editable = false;

        private int GetTileWidth()
        {
            int desired = ThemeManager.ScaleDpi(70, this);
            int min = ThemeManager.ScaleDpi(52, this);
            int max = ThemeManager.ScaleDpi(110, this);

            int innerPad = ThemeManager.ScaleDpi(4, this);
            int available = Math.Max(1, PanelTiles.ClientSize.Width - (innerPad * 2));

            // Prefer a constant pixel size (scaled for DPI). If the panel is too narrow,
            // allow shrinking below the normal minimum to avoid horizontal clipping.
            if (available < min)
            {
                return Math.Max(1, available);
            }

            return Math.Min(Math.Max(min, desired), Math.Min(max, available));
        }

        private void SetTilePropertiesEditable(bool editable)
        {
            tile_properties_editable = editable;

            PanelTileProperties.Enabled = true;

            // Keep checkboxes enabled so their ForeColor is readable in dark mode.
            // Use TabStop + click handler guards to prevent edits when not editable.
            TileBlocksMovement.Enabled = true;
            TileBlocksVision.Enabled = true;
            TileBlocksMovement.TabStop = editable;
            TileBlocksVision.TabStop = editable;

            ThemeManager.ApplyTheme(PanelTileProperties);
            ThemeManager.ApplyTheme(TileBlocksMovement);
            ThemeManager.ApplyTheme(TileBlocksVision);
        }

        private void LayoutTileGrid()
        {
            if (PanelTiles == null)
            {
                return;
            }

            int tileWidth = GetTileWidth();
            int innerPad = ThemeManager.ScaleDpi(4, this);
            int spacingX = ThemeManager.ScaleDpi(6, this);
            int spacingY = ThemeManager.ScaleDpi(6, this);

            int available = Math.Max(1, PanelTiles.ClientSize.Width - (innerPad * 2));
            int columns = Math.Max(1, (available + spacingX) / (tileWidth + spacingX));

            PanelTiles.SuspendLayout();
            try
            {
                int tileHeight = 0;
                for (int i = 0; i < PanelTiles.Controls.Count; i++)
                {
                    if (PanelTiles.Controls[i] is not MapTerrainTextureControl mttc)
                    {
                        continue;
                    }

                    mttc.ResizeWidth(tileWidth);
                    tileHeight = Math.Max(tileHeight, mttc.Height);
                }

                if (tileHeight <= 0)
                {
                    tileHeight = tileWidth + ThemeManager.ScaleDpi(18, this);
                }

                for (int i = 0; i < PanelTiles.Controls.Count; i++)
                {
                    if (PanelTiles.Controls[i] is not MapTerrainTextureControl mttc)
                    {
                        continue;
                    }

                    int col = i % columns;
                    int row = i / columns;
                    mttc.Location = new Point(
                        innerPad + (col * (tileWidth + spacingX)),
                        innerPad + (row * (tileHeight + spacingY)));
                }

                int rows = (int)Math.Ceiling(PanelTiles.Controls.Count / (double)columns);
                int minHeight = innerPad + (rows * tileHeight) + (Math.Max(0, rows - 1) * spacingY) + innerPad;
                PanelTiles.AutoScrollMinSize = new Size(0, minHeight);
            }
            finally
            {
                PanelTiles.ResumeLayout();
            }
        }

        private void LayoutInspector()
        {
            int pad = ThemeManager.ScaleDpi(3, this);
            int contentWidth = Math.Max(10, ClientSize.Width - (pad * 2));

            LabelTileType.Location = new Point(pad, pad);
            int y = LabelTileType.Bottom + pad;

            int bottom = ClientSize.Height - pad;

            PanelTileProperties.Width = contentWidth;
            PanelTileProperties.Location = new Point(pad, bottom - PanelTileProperties.Height);
            bottom = PanelTileProperties.Top - pad;

            if (PanelTileMixer.Visible)
            {
                PanelTileMixer.Width = contentWidth;
                PanelTileMixer.Location = new Point(pad, bottom - PanelTileMixer.Height);
                bottom = PanelTileMixer.Top - pad;
            }

            if (PanelButtons.Visible)
            {
                PanelButtons.Width = contentWidth;
                PanelButtons.Location = new Point(pad, bottom - PanelButtons.Height);
                bottom = PanelButtons.Top - pad;
            }

            PanelTiles.Location = new Point(pad, y);
            PanelTiles.Size = new Size(contentWidth, Math.Max(10, bottom - y));

            LayoutTileGrid();
        }

        public MapTerrainTextureInspector()
        {
            InitializeComponent();
            SelectedCustomTileMixImage1.ID = 0;
            SelectedCustomTileMixImage1.delegate_onpress = OnCustomTileMixPress;
            SelectedCustomTileMixImage2.ID = 1;
            SelectedCustomTileMixImage2.delegate_onpress = OnCustomTileMixPress;
            SelectedCustomTileMixImage3.ID = 2;
            SelectedCustomTileMixImage3.delegate_onpress = OnCustomTileMixPress;

            SizeChanged += (sender, e) => LayoutInspector();
        }

        // tile index 0: invalid
        // tile index >= 32: custom tile
        // tile index >= 224: base tile
        public void UpdateTile(byte tile_index)
        {
            if (tile_index < 32)
            {
                throw new Exception("MapTerrainTextureInspector.UpdateTile(): Invalid tile index!");
            }

            if (inspectortype == TerrainTileType.CUSTOM)
            {
                map.heightmap.texture_manager.RefreshTileTexture(tile_index);
                map.heightmap.texture_manager.RefreshTilePreview(tile_index);
                map.heightmap.texture_manager.UpdateUniformTileColor(tile_index, tile_index);

                byte selected_tile = (byte)((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile;
                if (selected_tile == tile_index)
                {
                    SelectedCustomTileTex.SetImage(map.heightmap.texture_manager.texture_tile_image[tile_index], 0);
                    SelectedCustomTileMixImage1.SetImage(map.heightmap.texture_manager.texture_tile_image[map.heightmap.texture_manager.texture_tiledata[tile_index].ind1], map.heightmap.texture_manager.texture_tiledata[tile_index].ind1);
                    SelectedCustomTileMixImage2.SetImage(map.heightmap.texture_manager.texture_tile_image[map.heightmap.texture_manager.texture_tiledata[tile_index].ind2], map.heightmap.texture_manager.texture_tiledata[tile_index].ind2);
                    SelectedCustomTileMixImage3.SetImage(map.heightmap.texture_manager.texture_tile_image[map.heightmap.texture_manager.texture_tiledata[tile_index].ind3], map.heightmap.texture_manager.texture_tiledata[tile_index].ind3);
                }

                foreach (MapTerrainTextureControl c in PanelTiles.Controls)
                {
                    if (c.ID == (int)tile_index)
                    {
                        c.SetImage(map.heightmap.texture_manager.texture_tile_image[tile_index], tile_index);
                        break;
                    }
                }

                MainForm.mapedittool.ui.RedrawMinimapFull();
            }

            TileBlocksMovement.Checked = map.heightmap.texture_manager.texture_tiledata[tile_index].blocks_movement;
            TileBlocksVision.Checked = map.heightmap.texture_manager.texture_tiledata[tile_index].blocks_vision;

            MainForm.mapedittool.update_render = true;
        }

        public void OnCustomTileMixPress(int ID)
        {
            map_dialog.MapSelectTile tileselectdialog = new map_dialog.MapSelectTile(map, map_dialog.MapTileSelectType.BASE);
            tileselectdialog.ShowDialog();

            if (tileselectdialog.SelectedTile != SFEngine.Utility.NO_INDEX)
            {
                byte selected_tile = (byte)((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile;

                map_operators.MapOperatorTileChangeState op_tcs = new map_operators.MapOperatorTileChangeState()
                {
                    tile_index = selected_tile,
                    PreOperatorTileState = map.heightmap.texture_manager.texture_tiledata[selected_tile]
                };

                if (ID == 0)
                {
                    map.heightmap.texture_manager.texture_tiledata[selected_tile].ind1 = (byte)tileselectdialog.SelectedTile;
                    SelectedCustomTileMixImage1.SetImage(
                        map.heightmap.texture_manager.texture_tile_image[map.heightmap.texture_manager.texture_tiledata[selected_tile].ind1],
                        map.heightmap.texture_manager.texture_tiledata[selected_tile].ind1);
                }
                else if (ID == 1)
                {
                    map.heightmap.texture_manager.texture_tiledata[selected_tile].ind2 = (byte)tileselectdialog.SelectedTile;
                    SelectedCustomTileMixImage2.SetImage(
                         map.heightmap.texture_manager.texture_tile_image[map.heightmap.texture_manager.texture_tiledata[selected_tile].ind2],
                         map.heightmap.texture_manager.texture_tiledata[selected_tile].ind2);
                }
                else if (ID == 2)
                {
                    map.heightmap.texture_manager.texture_tiledata[selected_tile].ind3 = (byte)tileselectdialog.SelectedTile;
                    SelectedCustomTileMixImage3.SetImage(
                         map.heightmap.texture_manager.texture_tile_image[map.heightmap.texture_manager.texture_tiledata[selected_tile].ind3],
                         map.heightmap.texture_manager.texture_tiledata[selected_tile].ind3);
                }
                else
                {
                    throw new Exception("MapTerrainTextureInspector.OnCustomTileMixPress(): Invalid button ID!");
                }

                op_tcs.Finish(map);
                MainForm.mapedittool.op_queue.Push(op_tcs);

                UpdateTile(selected_tile);
            }
        }

        public void OnBaseTexturePress(int ID)
        {
            if (ID == 0)
            {
                ((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile = 0;
                SetInspectorPanelEditable(PanelTileProperties, false);
                SetInspectorPanelEditable(PanelTileMixer, false);
                SetInspectorPanelEditable(PanelButtons, false);
                SetTilePropertiesEditable(false);
                return;
            }
            ((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile = ID + 223;
            SetInspectorPanelEditable(PanelTileProperties, true);
            SetTilePropertiesEditable(true);
            TileBlocksMovement.Checked = map.heightmap.texture_manager.texture_tiledata[ID + 223].blocks_movement;
            TileBlocksVision.Checked = map.heightmap.texture_manager.texture_tiledata[ID + 223].blocks_vision;
        }

        public void OnCustomTexturePress(int ID)
        {
            ((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile = ID;
            SetInspectorPanelEditable(PanelTileProperties, true);
            SetInspectorPanelEditable(PanelTileMixer, true);
            SetTilePropertiesEditable(true);
            TileBlocksMovement.Checked = map.heightmap.texture_manager.texture_tiledata[ID].blocks_movement;
            TileBlocksVision.Checked = map.heightmap.texture_manager.texture_tiledata[ID].blocks_vision;

            SelectedCustomTileMixImage1.SetImage(
                map.heightmap.texture_manager.texture_tile_image[map.heightmap.texture_manager.texture_tiledata[ID].ind1],
                map.heightmap.texture_manager.texture_tiledata[ID].ind1);
            SelectedCustomTileMixImage2.SetImage(
                 map.heightmap.texture_manager.texture_tile_image[map.heightmap.texture_manager.texture_tiledata[ID].ind2],
                 map.heightmap.texture_manager.texture_tiledata[ID].ind2);
            SelectedCustomTileMixImage3.SetImage(
                 map.heightmap.texture_manager.texture_tile_image[map.heightmap.texture_manager.texture_tiledata[ID].ind3],
                 map.heightmap.texture_manager.texture_tiledata[ID].ind3);
            TexWeight1.Text = map.heightmap.texture_manager.texture_tiledata[ID].weight1.ToString();
            TexWeight2.Text = map.heightmap.texture_manager.texture_tiledata[ID].weight2.ToString();
            TexWeight3.Text = map.heightmap.texture_manager.texture_tiledata[ID].weight3.ToString();

            SelectedCustomTileTex.SetImage(map.heightmap.texture_manager.texture_tile_image[ID], ID);
        }

        public void LoadBaseTextures()
        {
            PanelTileMixer.Visible = false;
            PanelButtons.Visible = false;
            PanelTiles.Controls.Clear();

            for (int i = 1; i < 32; i++)
            {
                MapTerrainTextureControl mttc = new MapTerrainTextureControl();
                mttc.ID = i;
                mttc.delegate_onpress = OnBaseTexturePress;
                mttc.SetImage(map.heightmap.texture_manager.texture_tile_image[i], i);
                PanelTiles.Controls.Add(mttc);
                ThemeManager.ApplyTheme(mttc);
            }

            SetInspectorPanelEditable(PanelTileProperties, false);
            SetTilePropertiesEditable(false);
            LayoutInspector();
        }

        public void LoadCustomTextures()
        {
            PanelTileMixer.Visible = true;
            PanelButtons.Visible = true;
            PanelTiles.Controls.Clear();
            for (int i = 32; i < 224; i++)
            {
                if (map.heightmap.texture_manager.tile_defined[i])
                {
                    MapTerrainTextureControl mttc = new MapTerrainTextureControl();
                    mttc.ID = i;
                    mttc.delegate_onpress = OnCustomTexturePress;
                    mttc.SetImage(map.heightmap.texture_manager.texture_tile_image[i], i);
                    PanelTiles.Controls.Add(mttc);
                    ThemeManager.ApplyTheme(mttc);
                }
            }

            SetInspectorPanelEditable(PanelTileMixer, false);
            SetInspectorPanelEditable(PanelTileProperties, false);
            SetTilePropertiesEditable(false);
            LayoutInspector();
        }

        public void SetInspectorType(TerrainTileType type)
        {
            if (type == TerrainTileType.NONE)
            {
                throw new Exception("MapTerrainTextureInspector.SetInspectorType(): Invalid inspector type!");
            }

            if (type == inspectortype)
            {
                return;
            }

            inspectortype = type;
            RefreshTexturePreview();
            LayoutInspector();
        }

        public void SelectTileType(byte ttype)
        {
            if (ttype > 223)
            {
                ttype = (byte)(ttype - 223);
            }

            if (ttype == 0)
            {
                OnBaseTexturePress(0);
                return;
            }
            if (ttype < 32)
            {
                SetInspectorType(TerrainTileType.BASE);
                OnBaseTexturePress(ttype);
                PanelTiles.Controls[ttype - 1].Focus();
            }
            else
            {
                SetInspectorType(TerrainTileType.CUSTOM);
                OnCustomTexturePress(ttype);
                foreach (MapTerrainTextureControl c in PanelTiles.Controls)
                {
                    if (c.ID == ttype)
                    {
                        c.Focus();
                        break;
                    }
                }
            }
        }

        public void RefreshTexturePreview()
        {
            if ((MainForm.mapedittool.selected_editor != null) && (MainForm.mapedittool.selected_editor is MapEdit.MapTerrainTextureEditor))
            {
                ((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile = 0;
            }

            if (inspectortype == TerrainTileType.BASE)
            {
                LoadBaseTextures();
            }
            else
            {
                LoadCustomTextures();
            }
        }

        private void TexWeight1_Validated(object sender, EventArgs e)
        {
            byte selected_tile = (byte)((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile;
            TexWeight1.Text = SFEngine.Utility.TryParseUInt8(TexWeight1.Text).ToString();

            map_operators.MapOperatorTileChangeState op_tcs = new map_operators.MapOperatorTileChangeState()
            {
                tile_index = selected_tile,
                PreOperatorTileState = map.heightmap.texture_manager.texture_tiledata[selected_tile]
            };

            map.heightmap.texture_manager.texture_tiledata[selected_tile].weight1 = SFEngine.Utility.TryParseUInt8(TexWeight1.Text);

            op_tcs.Finish(map);
            MainForm.mapedittool.op_queue.Push(op_tcs);

            UpdateTile(selected_tile);
        }

        private void TexWeight2_Validated(object sender, EventArgs e)
        {
            byte selected_tile = (byte)((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile;
            TexWeight2.Text = SFEngine.Utility.TryParseUInt8(TexWeight2.Text).ToString();

            map_operators.MapOperatorTileChangeState op_tcs = new map_operators.MapOperatorTileChangeState()
            {
                tile_index = selected_tile,
                PreOperatorTileState = map.heightmap.texture_manager.texture_tiledata[selected_tile]
            };

            map.heightmap.texture_manager.texture_tiledata[selected_tile].weight2 = SFEngine.Utility.TryParseUInt8(TexWeight2.Text);

            op_tcs.Finish(map);
            MainForm.mapedittool.op_queue.Push(op_tcs);

            UpdateTile(selected_tile);
        }

        private void TexWeight3_Validated(object sender, EventArgs e)
        {
            byte selected_tile = (byte)((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile;
            TexWeight3.Text = SFEngine.Utility.TryParseUInt8(TexWeight3.Text).ToString();

            map_operators.MapOperatorTileChangeState op_tcs = new map_operators.MapOperatorTileChangeState()
            {
                tile_index = selected_tile,
                PreOperatorTileState = map.heightmap.texture_manager.texture_tiledata[selected_tile]
            };

            map.heightmap.texture_manager.texture_tiledata[selected_tile].weight3 = SFEngine.Utility.TryParseUInt8(TexWeight3.Text);

            op_tcs.Finish(map);
            MainForm.mapedittool.op_queue.Push(op_tcs);

            UpdateTile(selected_tile);
        }

        private void ButtonAddCustomTile_Click(object sender, EventArgs e)
        {
            int new_tile = 32;
            while (true)
            {
                if (map.heightmap.texture_manager.tile_defined[new_tile] == false)
                {
                    break;
                }

                new_tile += 1;
            }

            MainForm.mapedittool.op_queue.Push(new map_operators.MapOperatorAddOrRemoveTileType()
            {
                tile_index = new_tile,
                is_adding = true
            });

            map.heightmap.texture_manager.tile_defined[new_tile] = true;
            RefreshTexturePreview();
        }

        private void ButtonRemoveCustomTile_Click(object sender, EventArgs e)
        {
            byte selected_tile = (byte)((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile;
            if (selected_tile == 0)
            {
                return;
            }

            if (map.heightmap.texture_manager.tile_defined[selected_tile] == true)
            {
                MainForm.mapedittool.op_queue.Push(new map_operators.MapOperatorAddOrRemoveTileType()
                {
                    tile_index = selected_tile,
                    is_adding = false
                });

                map.heightmap.texture_manager.tile_defined[selected_tile] = false;
                RefreshTexturePreview();
            }
        }

        public void SetTileBlocksMovement(byte tile_index, bool blocks_movement)
        {
            map.heightmap.texture_manager.texture_tiledata[tile_index].blocks_movement = blocks_movement;
            TileBlocksMovement.Checked = blocks_movement;

            for(int y = 0; y < map.height; y++)
            {
                for(int x = 0; x < map.width; x++)
                {
                    if(map.heightmap.GetTile(new SFEngine.SFMap.SFCoord(x, y)) == tile_index)
                    {
                        map.heightmap.SetFlag(new SFEngine.SFMap.SFCoord(x, y), SFEngine.SFMap.SFMapHeightMapFlag.TERRAIN_MOVEMENT, blocks_movement);
                    }
                }
            }
            map.heightmap.RefreshOverlay();
        }

        public void SetTileBlocksVision(byte tile_index, bool blocks_vision)
        {
            map.heightmap.texture_manager.texture_tiledata[tile_index].blocks_vision = blocks_vision;
            TileBlocksVision.Checked = blocks_vision;
            for (int y = 0; y < map.height; y++)
            {
                for (int x = 0; x < map.width; x++)
                {
                    if (map.heightmap.GetTile(new SFEngine.SFMap.SFCoord(x, y)) == tile_index)
                    {
                        map.heightmap.SetFlag(new SFEngine.SFMap.SFCoord(x, y), SFEngine.SFMap.SFMapHeightMapFlag.TERRAIN_VISION, blocks_vision);
                    }
                }
            }
            map.heightmap.RefreshOverlay();
        }

        private void TileBlocksMovement_Click(object sender, EventArgs e)
        {
            if (!tile_properties_editable)
            {
                return;
            }

            byte selected_tile = (byte)((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile;

            map_operators.MapOperatorTileChangeState op_tcs = new map_operators.MapOperatorTileChangeState()
            {
                tile_index = selected_tile,
                PreOperatorTileState = map.heightmap.texture_manager.texture_tiledata[selected_tile]
            };

            SetTileBlocksMovement(selected_tile, !TileBlocksMovement.Checked);

            op_tcs.Finish(map);
            MainForm.mapedittool.op_queue.Push(op_tcs);
        }

        private void TileBlocksVision_Click(object sender, EventArgs e)
        {
            if (!tile_properties_editable)
            {
                return;
            }

            byte selected_tile = (byte)((MapEdit.MapTerrainTextureEditor)MainForm.mapedittool.selected_editor).SelectedTile;

            map_operators.MapOperatorTileChangeState op_tcs = new map_operators.MapOperatorTileChangeState()
            {
                tile_index = selected_tile,
                PreOperatorTileState = map.heightmap.texture_manager.texture_tiledata[selected_tile]
            };

            SetTileBlocksVision(selected_tile, !TileBlocksVision.Checked);

            op_tcs.Finish(map);
            MainForm.mapedittool.op_queue.Push(op_tcs);
        }
    }
}
