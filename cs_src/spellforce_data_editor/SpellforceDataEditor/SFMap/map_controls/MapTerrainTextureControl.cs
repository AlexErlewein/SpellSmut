using System;
using System.Drawing;
using System.Windows.Forms;

namespace SpellforceDataEditor.SFMap.map_controls
{
    public delegate void OnButtonPress(int id);

    public partial class MapTerrainTextureControl : UserControl
    {
        public int ID { get; set; } = SFEngine.Utility.NO_INDEX;
        public OnButtonPress delegate_onpress = null;

        private void SyncColors()
        {
            ButtonTextureImage.BackColor = BackColor;
            ButtonTextureImage.ForeColor = ForeColor;
            ButtonTextureID.BackColor = BackColor;
            ButtonTextureID.ForeColor = ForeColor;
        }

        private int GetIdLabelHeight()
        {
            int measured = TextRenderer.MeasureText("000", ButtonTextureID.Font).Height;
            return Math.Max(16, measured + 6);
        }

        public MapTerrainTextureControl()
        {
            InitializeComponent();

            // Ensure ThemeManager BackColor is respected (otherwise VisualStyles may draw a white background).
            ButtonTextureImage.UseVisualStyleBackColor = false;
            ButtonTextureImage.FlatStyle = FlatStyle.Flat;
            ButtonTextureImage.FlatAppearance.BorderSize = 1;

            SyncColors();
        }

        protected override void OnBackColorChanged(EventArgs e)
        {
            base.OnBackColorChanged(e);
            SyncColors();
        }

        protected override void OnForeColorChanged(EventArgs e)
        {
            base.OnForeColorChanged(e);
            SyncColors();
        }

        private void MapTerrainTextureControl_Resize(object sender, EventArgs e)
        {
            ButtonTextureImage.Size = new Size(Width - 6, Width - 6);
            ButtonTextureImage.Location = new Point(3, 3);

            int labelHeight = Height - Width;
            if (labelHeight <= 0)
            {
                labelHeight = GetIdLabelHeight();
            }

            ButtonTextureID.Size = new Size(Width - 6, labelHeight);
            ButtonTextureID.Location = new Point(3, Width);
        }

        public void SetImage(Image im, int tex_id)
        {
            ButtonTextureImage.Image = im;
            ButtonTextureID.Text = tex_id.ToString();
        }

        public void ResizeWidth(int w)
        {
            Size = new Size(w, w + GetIdLabelHeight());
        }

        private void ButtonTextureImage_Click(object sender, EventArgs e)
        {
            delegate_onpress?.Invoke(ID);
        }
    }
}
