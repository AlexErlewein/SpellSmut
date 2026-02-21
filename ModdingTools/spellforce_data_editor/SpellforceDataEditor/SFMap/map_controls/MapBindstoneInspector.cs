using SFEngine.SFCFF;
using SFEngine.SFMap;
using System;
using System.Windows.Forms;

namespace SpellforceDataEditor.SFMap.map_controls
{
    public partial class MapBindstoneInspector : SpellforceDataEditor.SFMap.map_controls.MapInspector
    {
        bool move_camera_on_select = false;
        bool bindstone_selected_from_list = true;

        bool trackbar_clicked = false;
        int trackbar_initial_angle = -1;

        public MapBindstoneInspector()
        {
            InitializeComponent();
        }

        private void MapBindstoneInspector_Load(object sender, EventArgs e)
        {
            ReloadList();
            ResizeList();
            SetInspectorPanelEditable(PanelProperties, false);
        }

        private void ReloadList()
        {
            ListBindstones.Items.Clear();
            for (int i = 0; i < map.int_object_manager.bindstones_index.Count; i++)
            {
                LoadNextBindstone(i);
            }
        }

        private int GetBindstoneIndex(SFMapInteractiveObject o)
        {
            int i = map.int_object_manager.int_objects.IndexOf(o);
            if (i != SFEngine.Utility.NO_INDEX)
            {
                return map.int_object_manager.bindstones_index.IndexOf(i);
            }

            return SFEngine.Utility.NO_INDEX;
        }

        private int GetPlayerIndexByBindstoneIndex(int i)
        {
            return map.metadata.FindPlayerByBindstoneIndex(i);
        }

        private string GetBindstoneString(SFMapInteractiveObject io)
        {
            int player = map.metadata.FindPlayerBySpawnPos(io.grid_position);
            if (player == SFEngine.Utility.NO_INDEX)
            {
                return "Bindstone at " + io.grid_position.ToString();
            }

            if (map.metadata.spawns[player].text_id == 0)
            {
                return "Bindstone at " + io.grid_position.ToString();
            }

            // Get text in the editor's current language
            string text = SFCategoryManager.GetTextByLanguage(map.metadata.spawns[player].text_id, SFEngine.Settings.LanguageID);

            // Check if text was found
            if (text == SFEngine.Utility.S_TEXT_MISSING || text == SFEngine.Utility.S_LANG_MISSING)
            {
                return "Bindstone at " + io.grid_position.ToString();
            }

            return $"{text.Trim()} {io.grid_position}";
        }

        private void ShowList()
        {
            if (ButtonResizeList.Text == "-")
            {
                return;
            }

            ResizeList();

            ButtonResizeList.Text = "-";
        }

        private void ResizeList()
        {
            PanelBindstonesList.Height = Height - PanelBindstonesList.Location.Y - 3;
            ListBindstones.Height = PanelBindstonesList.Height - 75;
        }

        public void RemoveBindstone(int index)
        {
            if (ListBindstones.SelectedIndex == index)
            {
                SetInspectorPanelEditable(PanelProperties, false);
            }

            ListBindstones.Items.RemoveAt(index);
        }

        public void LoadNextBindstone(int index)
        {
            SFMapInteractiveObject io = map.int_object_manager.int_objects[map.int_object_manager.bindstones_index[index]];
            ListBindstones.Items.Insert(index, GetBindstoneString(io));
        }

        private void HideList()
        {
            if (ButtonResizeList.Text == "+")
            {
                return;
            }

            PanelBindstonesList.Height = 30;

            ButtonResizeList.Text = "+";
        }

        public override void OnSelect(object o)
        {
            move_camera_on_select = false;
            bindstone_selected_from_list = false;

            if (o == null)
            {
                selection_helper.CancelSelection();
                SetInspectorPanelEditable(PanelProperties, false);
            }
            else
            {
                ListBindstones.SelectedIndex = GetBindstoneIndex((SFMapInteractiveObject)o);
            }
        }

        private void ListBindstones_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (ListBindstones.SelectedIndex == SFEngine.Utility.NO_INDEX)
            {
                return;
            }

            SetInspectorPanelEditable(PanelProperties, true);
            SFMapInteractiveObject bindstone = map.int_object_manager.int_objects[map.int_object_manager.bindstones_index[ListBindstones.SelectedIndex]];
            int player = GetPlayerIndexByBindstoneIndex(ListBindstones.SelectedIndex);
            if (player == -1)
            {
                SFEngine.LogUtils.Log.Warning(SFEngine.LogUtils.LogSource.SFMap,
                    "MapBindstoneInspector.ListBindstones_SelectedIndexChanged(): Can't find player at position "
                    + bindstone.grid_position.ToString());
                TextID.Text = "0";
                Unknown.Text = "0";
                UpdateTextPreview(0);
            }
            else
            {
                TextID.Text = map.metadata.spawns[player].text_id.ToString();
                Unknown.Text = map.metadata.spawns[player].unknown.ToString();
                UpdateTextPreview(map.metadata.spawns[player].text_id);
            }
            PosX.Text = bindstone.grid_position.x.ToString();
            PosY.Text = bindstone.grid_position.y.ToString();
            AngleTrackbar.Value = bindstone.angle;
            // angle, angletrackbar

            selection_helper.SelectInteractiveObject(bindstone);
            if ((move_camera_on_select) || (bindstone_selected_from_list))
            {
                MainForm.mapedittool.SetCameraViewPoint(bindstone.grid_position);
            }

            move_camera_on_select = false;
            bindstone_selected_from_list = true;
        }

        private void ButtonResizeList_Click(object sender, EventArgs e)
        {
            if (ButtonResizeList.Text == "-")
            {
                HideList();
            }
            else
            {
                ShowList();
            }
        }

        private void Angle_Validated(object sender, EventArgs e)
        {
            if (ListBindstones.SelectedIndex == SFEngine.Utility.NO_INDEX)
            {
                return;
            }

            SFMapInteractiveObject bindstone = map.int_object_manager.int_objects[map.int_object_manager.bindstones_index[ListBindstones.SelectedIndex]];

            int v = SFEngine.Utility.TryParseUInt16(Angle.Text, (ushort)bindstone.angle);
            v = (v >= 0 ? (v <= 359 ? v : 359) : 0);

            // undo/redo
            MainForm.mapedittool.op_queue.Push(new map_operators.MapOperatorEntityChangeProperty()
            {
                type = map_operators.MapOperatorEntityType.BINDSTONE,
                index = ListBindstones.SelectedIndex,
                property = map_operators.MapOperatorEntityProperty.ANGLE,
                PreChangeProperty = bindstone.angle,
                PostChangeProperty = v
            });

            AngleTrackbar.Value = v;
        }

        private void AngleTrackbar_ValueChanged(object sender, EventArgs e)
        {
            if (ListBindstones.SelectedIndex == SFEngine.Utility.NO_INDEX)
            {
                return;
            }

            SFMapInteractiveObject bindstone = map.int_object_manager.int_objects[map.int_object_manager.bindstones_index[ListBindstones.SelectedIndex]];
            Angle.Text = AngleTrackbar.Value.ToString();
            map.int_object_manager.RotateInteractiveObject(map.int_object_manager.bindstones_index[ListBindstones.SelectedIndex], AngleTrackbar.Value);

            MainForm.mapedittool.update_render = true;
        }

        // this is to make sure the undo/redo queue only receives the latest angle changed as an action to perform
        private void AngleTrackbar_MouseDown(object sender, MouseEventArgs e)
        {
            if (ListBindstones.SelectedIndex == SFEngine.Utility.NO_INDEX)
            {
                return;
            }

            trackbar_clicked = true;

            if (trackbar_initial_angle == -1)
            {
                SFMapInteractiveObject bindstone = map.int_object_manager.int_objects[map.int_object_manager.bindstones_index[ListBindstones.SelectedIndex]];
                trackbar_initial_angle = bindstone.angle;
            }
        }

        private void AngleTrackbar_MouseUp(object sender, MouseEventArgs e)
        {
            if (!trackbar_clicked)
            {
                return;
            }

            // undo/redo
            MainForm.mapedittool.op_queue.Push(new map_operators.MapOperatorEntityChangeProperty()
            {
                type = map_operators.MapOperatorEntityType.BINDSTONE,
                index = ListBindstones.SelectedIndex,
                property = map_operators.MapOperatorEntityProperty.ANGLE,
                PreChangeProperty = trackbar_initial_angle,
                PostChangeProperty = AngleTrackbar.Value
            });

            trackbar_clicked = false;
            trackbar_initial_angle = -1;
        }

        private void TextID_Validated(object sender, EventArgs e)
        {
            if (ListBindstones.SelectedIndex == SFEngine.Utility.NO_INDEX)
            {
                return;
            }

            SFMapInteractiveObject bindstone = map.int_object_manager.int_objects[map.int_object_manager.bindstones_index[ListBindstones.SelectedIndex]];
            int player = GetPlayerIndexByBindstoneIndex(ListBindstones.SelectedIndex);
            if (player == SFEngine.Utility.NO_INDEX)
            {
                SFEngine.LogUtils.Log.Warning(SFEngine.LogUtils.LogSource.SFMap,
                    "MapBindstoneInspector.TextID_Validated(): Can't find player at position "
                    + bindstone.grid_position.ToString());
                return;
            }

            // undo/redo
            MainForm.mapedittool.op_queue.Push(new map_operators.MapOperatorEntityChangeProperty()
            {
                type = map_operators.MapOperatorEntityType.BINDSTONE,
                index = ListBindstones.SelectedIndex,
                property = map_operators.MapOperatorEntityProperty.ID,
                PreChangeProperty = map.metadata.spawns[player].text_id,
                PostChangeProperty = SFEngine.Utility.TryParseUInt16(TextID.Text, map.metadata.spawns[player].text_id)
            });

            ushort new_text_id = SFEngine.Utility.TryParseUInt16(TextID.Text, map.metadata.spawns[player].text_id);
            map.metadata.spawns[player].text_id = new_text_id;
            UpdateTextPreview(new_text_id);
            ListBindstones.Items[ListBindstones.SelectedIndex] = GetBindstoneString(bindstone);
        }

        private void Unknown_Validated(object sender, EventArgs e)
        {
            if (ListBindstones.SelectedIndex == SFEngine.Utility.NO_INDEX)
            {
                return;
            }

            SFMapInteractiveObject bindstone = map.int_object_manager.int_objects[map.int_object_manager.bindstones_index[ListBindstones.SelectedIndex]];
            int player = GetPlayerIndexByBindstoneIndex(ListBindstones.SelectedIndex);
            if (player == SFEngine.Utility.NO_INDEX)
            {
                SFEngine.LogUtils.Log.Warning(SFEngine.LogUtils.LogSource.SFMap,
                    "MapBindstoneInspector.Unknown_Validated(): Can't find player at position "
                    + bindstone.grid_position.ToString());
                return;
            }

            // undo/redo
            MainForm.mapedittool.op_queue.Push(new map_operators.MapOperatorEntityChangeProperty()
            {
                type = map_operators.MapOperatorEntityType.BINDSTONE,
                index = ListBindstones.SelectedIndex,
                property = map_operators.MapOperatorEntityProperty.BINDSTONEUNKNOWN,
                PreChangeProperty = map.metadata.spawns[player].unknown,
                PostChangeProperty = SFEngine.Utility.TryParseInt16(Unknown.Text, map.metadata.spawns[player].unknown)
            });

            map.metadata.spawns[player].unknown = SFEngine.Utility.TryParseInt16(Unknown.Text, map.metadata.spawns[player].unknown);
        }

        private void PosX_Validated(object sender, EventArgs e)
        {
            if (ListBindstones.SelectedIndex == SFEngine.Utility.NO_INDEX)
            {
                return;
            }

            SFMapInteractiveObject bindstone = map.int_object_manager.int_objects[map.int_object_manager.bindstones_index[ListBindstones.SelectedIndex]];
            int player = GetPlayerIndexByBindstoneIndex(ListBindstones.SelectedIndex);
            if (player == SFEngine.Utility.NO_INDEX)
            {
                return;
            }

            ushort new_x = SFEngine.Utility.TryParseUInt16(PosX.Text, (ushort)bindstone.grid_position.x);
            
            // Validate bounds
            if (new_x >= map.width)
            {
                new_x = (ushort)(map.width - 1);
                PosX.Text = new_x.ToString();
            }

            if (new_x == bindstone.grid_position.x)
            {
                return;
            }

            SFCoord old_pos = bindstone.grid_position;
            SFCoord new_pos = new SFCoord(new_x, bindstone.grid_position.y);

            // undo/redo
            MainForm.mapedittool.op_queue.Push(new map_operators.MapOperatorEntityChangeProperty()
            {
                type = map_operators.MapOperatorEntityType.BINDSTONE,
                index = ListBindstones.SelectedIndex,
                property = map_operators.MapOperatorEntityProperty.POSITION,
                PreChangeProperty = old_pos,
                PostChangeProperty = new_pos
            });

            int int_obj_index = map.int_object_manager.bindstones_index[ListBindstones.SelectedIndex];
            map.int_object_manager.MoveInteractiveObject(int_obj_index, new_pos);
            map.metadata.spawns[player].pos = new_pos;

            // Update list display and view
            ListBindstones.Items[ListBindstones.SelectedIndex] = GetBindstoneString(bindstone);
            selection_helper.SelectInteractiveObject(bindstone);
            MainForm.mapedittool.update_render = true;
        }

        private void PosY_Validated(object sender, EventArgs e)
        {
            if (ListBindstones.SelectedIndex == SFEngine.Utility.NO_INDEX)
            {
                return;
            }

            SFMapInteractiveObject bindstone = map.int_object_manager.int_objects[map.int_object_manager.bindstones_index[ListBindstones.SelectedIndex]];
            int player = GetPlayerIndexByBindstoneIndex(ListBindstones.SelectedIndex);
            if (player == SFEngine.Utility.NO_INDEX)
            {
                return;
            }

            ushort new_y = SFEngine.Utility.TryParseUInt16(PosY.Text, (ushort)bindstone.grid_position.y);
            
            // Validate bounds
            if (new_y >= map.height)
            {
                new_y = (ushort)(map.height - 1);
                PosY.Text = new_y.ToString();
            }

            if (new_y == bindstone.grid_position.y)
            {
                return;
            }

            SFCoord old_pos = bindstone.grid_position;
            SFCoord new_pos = new SFCoord(bindstone.grid_position.x, new_y);

            // undo/redo
            MainForm.mapedittool.op_queue.Push(new map_operators.MapOperatorEntityChangeProperty()
            {
                type = map_operators.MapOperatorEntityType.BINDSTONE,
                index = ListBindstones.SelectedIndex,
                property = map_operators.MapOperatorEntityProperty.POSITION,
                PreChangeProperty = old_pos,
                PostChangeProperty = new_pos
            });

            int int_obj_index = map.int_object_manager.bindstones_index[ListBindstones.SelectedIndex];
            map.int_object_manager.MoveInteractiveObject(int_obj_index, new_pos);
            map.metadata.spawns[player].pos = new_pos;

            // Update list display and view
            ListBindstones.Items[ListBindstones.SelectedIndex] = GetBindstoneString(bindstone);
            selection_helper.SelectInteractiveObject(bindstone);
            MainForm.mapedittool.update_render = true;
        }

        private void TextID_MouseDown(object sender, MouseEventArgs e)
        {
            if(e.Button == MouseButtons.Right)
            {
                if(MainForm.data != null)
                {
                    MainForm.data.trace_id(2016, SFEngine.Utility.TryParseUInt16(TextID.Text));
                }
            }
        }

        private void TextID_TextChanged(object sender, EventArgs e)
        {
            // Update preview as user types (but don't save until validated)
            ushort text_id = SFEngine.Utility.TryParseUInt16(TextID.Text, 0);
            UpdateTextPreview(text_id);
        }

        private void UpdateTextPreview(ushort text_id)
        {
            if (text_id == 0)
            {
                TextPreview.Text = "(No text - ID 0)";
                TextPreview.ForeColor = System.Drawing.Color.LightGray;
                return;
            }

            string text = SFCategoryManager.GetTextByLanguage(text_id, SFEngine.Settings.LanguageID);
            
            if (text == SFEngine.Utility.S_TEXT_MISSING || text == SFEngine.Utility.S_LANG_MISSING)
            {
                TextPreview.Text = $"(Text ID {text_id} not found)";
                TextPreview.ForeColor = System.Drawing.Color.Orange;
            }
            else
            {
                TextPreview.Text = text.Trim();
                TextPreview.ForeColor = System.Drawing.Color.LightGreen;
            }
        }

        private void ButtonEditText_Click(object sender, EventArgs e)
        {
            map_dialog.MapTextEditorDialog dialog = new map_dialog.MapTextEditorDialog();
            dialog.SelectedTextID = SFEngine.Utility.TryParseUInt16(TextID.Text, 0);
            if (dialog.ShowDialog() == DialogResult.OK)
            {
                // Update Text ID if a new one was selected
                if (dialog.SelectedTextID != 0 && dialog.SelectedTextID != SFEngine.Utility.TryParseUInt16(TextID.Text, 0))
                {
                    TextID.Text = dialog.SelectedTextID.ToString();
                    TextID_Validated(TextID, EventArgs.Empty);
                }
                else
                {
                    // Just refresh the preview
                    UpdateTextPreview(SFEngine.Utility.TryParseUInt16(TextID.Text, 0));
                }
            }
        }
    }
}
