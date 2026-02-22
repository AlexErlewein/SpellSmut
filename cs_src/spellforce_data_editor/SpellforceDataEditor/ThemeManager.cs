using System;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace SpellforceDataEditor
{
    public enum Theme
    {
        Light,
        Dark
    }

    public static class ThemeManager
    {
        public static Theme CurrentTheme { get; private set; } = Theme.Dark;

        private static DarkToolStripRenderer _darkRenderer = new DarkToolStripRenderer();

        private static readonly Color ComboDarkBack = Color.FromArgb(24, 24, 24);
        private static readonly Color ComboDarkFore = Color.Gainsboro;
        private static readonly Color ComboDarkSelBack = Color.FromArgb(70, 70, 160);
        private static readonly Color ComboDarkSelFore = Color.White;
        private static readonly Color TabDarkBack = Color.FromArgb(32, 32, 32);
        private static readonly Color TabDarkSelectedBack = Color.FromArgb(45, 45, 45);
        private static readonly Color TabDarkBorder = Color.FromArgb(70, 70, 70);
        private static readonly Color TabDarkFore = Color.Gainsboro;

        private const int DwmwaUseImmersiveDarkModeBefore20H1 = 19;
        private const int DwmwaUseImmersiveDarkMode = 20;

        [DllImport("dwmapi.dll")]
        private static extern int DwmSetWindowAttribute(IntPtr hwnd, int dwAttribute, ref int pvAttribute, int cbAttribute);

        private static void ApplyWindowTitleBarTheme(Form form, bool dark)
        {
            if (!OperatingSystem.IsWindows())
            {
                return;
            }

            void ApplyToHandle()
            {
                if (!form.IsHandleCreated)
                {
                    return;
                }

                int useDark = dark ? 1 : 0;
                int attributeSize = Marshal.SizeOf<int>();

                int hr = DwmSetWindowAttribute(form.Handle, DwmwaUseImmersiveDarkMode, ref useDark, attributeSize);
                if (hr != 0)
                {
                    DwmSetWindowAttribute(form.Handle, DwmwaUseImmersiveDarkModeBefore20H1, ref useDark, attributeSize);
                }
            }

            if (form.IsHandleCreated)
            {
                ApplyToHandle();
            }
            else
            {
                void OnHandleCreated(object sender, EventArgs e)
                {
                    form.HandleCreated -= OnHandleCreated;
                    ApplyToHandle();
                }

                form.HandleCreated += OnHandleCreated;
            }
        }

        private static void ComboBox_DarkDrawItem(object sender, DrawItemEventArgs e)
        {
            if (e.Index < 0) return;
            ComboBox combo = (ComboBox)sender;

            bool selected = (e.State & DrawItemState.Selected) == DrawItemState.Selected;
            Color back = selected ? ComboDarkSelBack : ComboDarkBack;
            Color fore = selected ? ComboDarkSelFore : ComboDarkFore;

            using (var backBrush = new SolidBrush(back))
            {
                e.Graphics.FillRectangle(backBrush, e.Bounds);
            }

            string text = combo.GetItemText(combo.Items[e.Index]);
            TextRenderer.DrawText(e.Graphics, text, e.Font, e.Bounds, fore,
                TextFormatFlags.Left | TextFormatFlags.VerticalCenter);

            e.DrawFocusRectangle();
        }

        private static void TabControl_DarkDrawItem(object sender, DrawItemEventArgs e)
        {
            if (sender is not TabControl tabControl) return;
            if (e.Index < 0 || e.Index >= tabControl.TabPages.Count) return;

            var tabRect = e.Bounds;
            bool selected = (e.State & DrawItemState.Selected) == DrawItemState.Selected;

            using (var backBrush = new SolidBrush(selected ? TabDarkSelectedBack : TabDarkBack))
            {
                e.Graphics.FillRectangle(backBrush, tabRect);
            }

            using (var borderPen = new Pen(TabDarkBorder))
            {
                var borderRect = tabRect;
                borderRect.Width -= 1;
                borderRect.Height -= 1;
                e.Graphics.DrawRectangle(borderPen, borderRect);
            }

            TextRenderer.DrawText(
                e.Graphics,
                tabControl.TabPages[e.Index].Text,
                tabControl.Font,
                tabRect,
                TabDarkFore,
                TextFormatFlags.HorizontalCenter |
                TextFormatFlags.VerticalCenter |
                TextFormatFlags.SingleLine |
                TextFormatFlags.EndEllipsis);
        }

        public static void SetTheme(Theme theme)
        {
            CurrentTheme = theme;

            if (theme == Theme.Dark)
            {
                WinFormsUtility.UseDarkTheme();
            }
            else
            {
                WinFormsUtility.UseLightTheme();
            }

            foreach (Form form in Application.OpenForms)
            {
                ApplyTheme(form);
            }
        }

        public static void ApplyTheme(Control root)
        {
            if (root == null)
            {
                return;
            }

            ApplyThemeToControlTree(root);
        }

        /// <summary>
        /// Scales a pixel value by the current DPI factor relative to 96 DPI (100%).
        /// Use this for any runtime-calculated pixel margins or sizes.
        /// </summary>
        public static int ScaleDpi(int pixels, Control control)
        {
            float dpi = control.DeviceDpi;
            return (int)(pixels * dpi / 96f);
        }

        private static void ApplyThemeToControlTree(Control control)
        {
            ApplyThemeToSingleControl(control);

            if (control is SplitContainer split)
            {
                ApplyThemeToControlTree(split.Panel1);
                ApplyThemeToControlTree(split.Panel2);
            }

            foreach (Control child in control.Controls)
            {
                ApplyThemeToControlTree(child);
            }
        }

        private static void ApplyThemeToSingleControl(Control control)
        {
            bool dark = CurrentTheme == Theme.Dark;

            if (dark)
            {
                ApplyDarkTheme(control);
            }
            else
            {
                ApplyLightTheme(control);
            }
        }

        private static void ApplyDarkTheme(Control control)
        {
            // Containers
            if (control is Form || control is Panel || control is GroupBox ||
                control is TabControl || control is TabPage || control is SplitContainer || control is UserControl)
            {
                control.BackColor = Color.FromArgb(32, 32, 32);
                control.ForeColor = Color.Gainsboro;
            }
            else if (control is Button)
            {
                control.BackColor = Color.FromArgb(45, 45, 45);
                control.ForeColor = Color.Gainsboro;
            }
            // LinkLabel before Label (LinkLabel extends Label)
            else if (control is LinkLabel darkLink)
            {
                darkLink.LinkColor = Color.FromArgb(100, 160, 255);
                darkLink.ActiveLinkColor = Color.FromArgb(140, 190, 255);
                darkLink.VisitedLinkColor = Color.FromArgb(160, 130, 255);
                darkLink.ForeColor = Color.Gainsboro;
            }
            else if (control is Label || control is CheckBox || control is RadioButton)
            {
                control.ForeColor = Color.Gainsboro;
            }
            // CheckedListBox before ListBox (CheckedListBox extends ListBox)
            else if (control is CheckedListBox)
            {
                control.BackColor = Color.FromArgb(24, 24, 24);
                control.ForeColor = Color.Gainsboro;
            }
            else if (control is ComboBox darkCombo)
            {
                darkCombo.BackColor = ComboDarkBack;
                darkCombo.ForeColor = ComboDarkFore;
                darkCombo.FlatStyle = FlatStyle.Flat;
                if (darkCombo.DrawMode != DrawMode.OwnerDrawFixed)
                {
                    darkCombo.DrawMode = DrawMode.OwnerDrawFixed;
                    darkCombo.DrawItem += ComboBox_DarkDrawItem;
                }
            }
            else if (control is TextBox || control is ListBox)
            {
                control.BackColor = Color.FromArgb(24, 24, 24);
                control.ForeColor = Color.Gainsboro;
            }
            // ToolStrip types - apply dark renderer for dropdown menus
            else if (control is MenuStrip menuStrip)
            {
                menuStrip.BackColor = Color.FromArgb(45, 45, 45);
                menuStrip.ForeColor = Color.Gainsboro;
                menuStrip.Renderer = _darkRenderer;
            }
            else if (control is ToolStrip toolStrip)
            {
                toolStrip.BackColor = Color.FromArgb(45, 45, 45);
                toolStrip.ForeColor = Color.Gainsboro;
                toolStrip.Renderer = _darkRenderer;
            }
            else if (control is TreeView || control is ListView)
            {
                control.BackColor = Color.FromArgb(24, 24, 24);
                control.ForeColor = Color.Gainsboro;
            }
            else if (control is NumericUpDown)
            {
                control.BackColor = Color.FromArgb(24, 24, 24);
                control.ForeColor = Color.Gainsboro;
            }
            else if (control is RichTextBox)
            {
                control.BackColor = Color.FromArgb(24, 24, 24);
                control.ForeColor = Color.Gainsboro;
            }
            else if (control is DataGridView darkGrid)
            {
                darkGrid.BackgroundColor = Color.FromArgb(32, 32, 32);
                darkGrid.GridColor = Color.FromArgb(70, 70, 70);
                darkGrid.DefaultCellStyle.BackColor = Color.FromArgb(24, 24, 24);
                darkGrid.DefaultCellStyle.ForeColor = Color.Gainsboro;
                darkGrid.DefaultCellStyle.SelectionBackColor = Color.FromArgb(70, 70, 160);
                darkGrid.DefaultCellStyle.SelectionForeColor = Color.White;
                darkGrid.ColumnHeadersDefaultCellStyle.BackColor = Color.FromArgb(45, 45, 45);
                darkGrid.ColumnHeadersDefaultCellStyle.ForeColor = Color.Gainsboro;
                darkGrid.RowHeadersDefaultCellStyle.BackColor = Color.FromArgb(45, 45, 45);
                darkGrid.RowHeadersDefaultCellStyle.ForeColor = Color.Gainsboro;
                darkGrid.EnableHeadersVisualStyles = false;
            }
            else if (control is ProgressBar)
            {
                control.BackColor = Color.FromArgb(45, 45, 45);
            }
            else if (control is PictureBox)
            {
                control.BackColor = Color.FromArgb(32, 32, 32);
            }
            else if (control is TrackBar)
            {
                control.BackColor = Color.FromArgb(32, 32, 32);
                control.ForeColor = Color.Gainsboro;
            }

            if (control is TabPage darkTabPage)
            {
                darkTabPage.UseVisualStyleBackColor = false;
            }

            if (control is TabControl darkTabControl)
            {
                darkTabControl.DrawItem -= TabControl_DarkDrawItem;
                darkTabControl.DrawItem += TabControl_DarkDrawItem;
                darkTabControl.DrawMode = TabDrawMode.OwnerDrawFixed;
                darkTabControl.Invalidate();
            }

            if (control is Form darkForm)
            {
                ApplyWindowTitleBarTheme(darkForm, true);
            }
        }

        private static void ApplyLightTheme(Control control)
        {
            // Containers
            if (control is Form || control is Panel || control is GroupBox ||
                control is TabControl || control is TabPage || control is SplitContainer || control is UserControl)
            {
                control.BackColor = SystemColors.Control;
                control.ForeColor = SystemColors.ControlText;
            }
            else if (control is Button)
            {
                control.BackColor = SystemColors.Control;
                control.ForeColor = SystemColors.ControlText;
            }
            // LinkLabel before Label
            else if (control is LinkLabel lightLink)
            {
                lightLink.LinkColor = Color.Empty;
                lightLink.ActiveLinkColor = Color.Empty;
                lightLink.VisitedLinkColor = Color.Empty;
                lightLink.ForeColor = SystemColors.ControlText;
            }
            else if (control is Label || control is CheckBox || control is RadioButton)
            {
                control.ForeColor = SystemColors.ControlText;
            }
            // CheckedListBox before ListBox
            else if (control is CheckedListBox)
            {
                control.BackColor = SystemColors.Window;
                control.ForeColor = SystemColors.WindowText;
            }
            else if (control is ComboBox lightCombo)
            {
                lightCombo.BackColor = SystemColors.Window;
                lightCombo.ForeColor = SystemColors.WindowText;
                lightCombo.FlatStyle = FlatStyle.Standard;
                if (lightCombo.DrawMode == DrawMode.OwnerDrawFixed)
                {
                    lightCombo.DrawItem -= ComboBox_DarkDrawItem;
                    lightCombo.DrawMode = DrawMode.Normal;
                }
            }
            else if (control is TextBox || control is ListBox)
            {
                control.BackColor = SystemColors.Window;
                control.ForeColor = SystemColors.WindowText;
            }
            // ToolStrip types - restore default renderer
            else if (control is MenuStrip menuStrip)
            {
                menuStrip.BackColor = SystemColors.Control;
                menuStrip.ForeColor = SystemColors.ControlText;
                menuStrip.RenderMode = ToolStripRenderMode.ManagerRenderMode;
            }
            else if (control is ToolStrip toolStrip)
            {
                toolStrip.BackColor = SystemColors.Control;
                toolStrip.ForeColor = SystemColors.ControlText;
                toolStrip.RenderMode = ToolStripRenderMode.ManagerRenderMode;
            }
            else if (control is TreeView || control is ListView)
            {
                control.BackColor = SystemColors.Window;
                control.ForeColor = SystemColors.WindowText;
            }
            else if (control is NumericUpDown)
            {
                control.BackColor = SystemColors.Window;
                control.ForeColor = SystemColors.WindowText;
            }
            else if (control is RichTextBox)
            {
                control.BackColor = SystemColors.Window;
                control.ForeColor = SystemColors.WindowText;
            }
            else if (control is DataGridView lightGrid)
            {
                lightGrid.BackgroundColor = SystemColors.AppWorkspace;
                lightGrid.GridColor = SystemColors.ControlDark;
                lightGrid.DefaultCellStyle.BackColor = SystemColors.Window;
                lightGrid.DefaultCellStyle.ForeColor = SystemColors.WindowText;
                lightGrid.DefaultCellStyle.SelectionBackColor = SystemColors.Highlight;
                lightGrid.DefaultCellStyle.SelectionForeColor = SystemColors.HighlightText;
                lightGrid.ColumnHeadersDefaultCellStyle.BackColor = SystemColors.Control;
                lightGrid.ColumnHeadersDefaultCellStyle.ForeColor = SystemColors.ControlText;
                lightGrid.RowHeadersDefaultCellStyle.BackColor = SystemColors.Control;
                lightGrid.RowHeadersDefaultCellStyle.ForeColor = SystemColors.ControlText;
                lightGrid.EnableHeadersVisualStyles = true;
            }
            else if (control is ProgressBar)
            {
                control.BackColor = SystemColors.Control;
            }
            else if (control is PictureBox)
            {
                control.BackColor = SystemColors.Control;
            }
            else if (control is TrackBar)
            {
                control.BackColor = SystemColors.Control;
                control.ForeColor = SystemColors.ControlText;
            }

            if (control is TabPage lightTabPage)
            {
                lightTabPage.UseVisualStyleBackColor = true;
            }

            if (control is TabControl lightTabControl)
            {
                lightTabControl.DrawItem -= TabControl_DarkDrawItem;
                lightTabControl.DrawMode = TabDrawMode.Normal;
                lightTabControl.Invalidate();
            }

            if (control is Form lightForm)
            {
                ApplyWindowTitleBarTheme(lightForm, false);
            }
        }
    }

    /// <summary>
    /// Custom ToolStripRenderer for dark themed dropdown menus.
    /// </summary>
    public class DarkToolStripRenderer : ToolStripProfessionalRenderer
    {
        private static readonly Color BackColor = Color.FromArgb(32, 32, 32);
        private static readonly Color MenuItemSelectedColor = Color.FromArgb(55, 55, 55);
        private static readonly Color MenuItemPressedColor = Color.FromArgb(70, 70, 70);
        private static readonly Color BorderColor = Color.FromArgb(70, 70, 70);
        private static readonly Color SeparatorColor = Color.FromArgb(70, 70, 70);
        private static readonly Color TextColor = Color.Gainsboro;
        private static readonly Color DisabledTextColor = Color.FromArgb(110, 110, 110);
        private static readonly Color CheckMarkColor = Color.FromArgb(100, 160, 255);

        public DarkToolStripRenderer() : base(new DarkColorTable()) { }

        protected override void OnRenderToolStripBackground(ToolStripRenderEventArgs e)
        {
            using (var brush = new SolidBrush(BackColor))
            {
                e.Graphics.FillRectangle(brush, e.AffectedBounds);
            }
        }

        protected override void OnRenderMenuItemBackground(ToolStripItemRenderEventArgs e)
        {
            var rect = new Rectangle(Point.Empty, e.Item.Size);

            if (e.Item.Selected || e.Item.Pressed)
            {
                var color = e.Item.Pressed ? MenuItemPressedColor : MenuItemSelectedColor;
                using (var brush = new SolidBrush(color))
                {
                    e.Graphics.FillRectangle(brush, rect);
                }
                using (var pen = new Pen(BorderColor))
                {
                    e.Graphics.DrawRectangle(pen, rect.X, rect.Y, rect.Width - 1, rect.Height - 1);
                }
            }
        }

        protected override void OnRenderItemText(ToolStripItemTextRenderEventArgs e)
        {
            e.TextColor = e.Item.Enabled ? TextColor : DisabledTextColor;
            base.OnRenderItemText(e);
        }

        protected override void OnRenderSeparator(ToolStripSeparatorRenderEventArgs e)
        {
            int y = e.Item.Height / 2;
            using (var pen = new Pen(SeparatorColor))
            {
                e.Graphics.DrawLine(pen, 0, y, e.Item.Width, y);
            }
        }

        protected override void OnRenderImageMargin(ToolStripRenderEventArgs e)
        {
            // Skip default image margin rendering to keep dark background
        }

        protected override void OnRenderItemCheck(ToolStripItemImageRenderEventArgs e)
        {
            var rect = e.ImageRectangle;
            rect.Inflate(1, 1);
            using (var pen = new Pen(CheckMarkColor))
            {
                e.Graphics.DrawRectangle(pen, rect);
            }
            base.OnRenderItemCheck(e);
        }

        protected override void OnRenderArrow(ToolStripArrowRenderEventArgs e)
        {
            e.ArrowColor = TextColor;
            base.OnRenderArrow(e);
        }

        protected override void OnRenderToolStripBorder(ToolStripRenderEventArgs e)
        {
            if (e.ToolStrip is ToolStripDropDownMenu)
            {
                using (var pen = new Pen(BorderColor))
                {
                    var bounds = e.AffectedBounds;
                    e.Graphics.DrawRectangle(pen, bounds.X, bounds.Y, bounds.Width - 1, bounds.Height - 1);
                }
            }
            else
            {
                base.OnRenderToolStripBorder(e);
            }
        }
    }

    /// <summary>
    /// Dark color table for ToolStripProfessionalRenderer.
    /// </summary>
    public class DarkColorTable : ProfessionalColorTable
    {
        private static readonly Color Dark = Color.FromArgb(32, 32, 32);
        private static readonly Color MediumDark = Color.FromArgb(45, 45, 45);
        private static readonly Color Highlight = Color.FromArgb(55, 55, 55);
        private static readonly Color Border = Color.FromArgb(70, 70, 70);

        public override Color MenuItemSelected => Highlight;
        public override Color MenuItemSelectedGradientBegin => Highlight;
        public override Color MenuItemSelectedGradientEnd => Highlight;
        public override Color MenuItemPressedGradientBegin => MediumDark;
        public override Color MenuItemPressedGradientEnd => MediumDark;
        public override Color MenuBorder => Border;
        public override Color MenuItemBorder => Border;
        public override Color ToolStripDropDownBackground => Dark;
        public override Color ImageMarginGradientBegin => Dark;
        public override Color ImageMarginGradientMiddle => Dark;
        public override Color ImageMarginGradientEnd => Dark;
        public override Color SeparatorDark => Border;
        public override Color SeparatorLight => Dark;
        public override Color ToolStripContentPanelGradientBegin => Dark;
        public override Color ToolStripContentPanelGradientEnd => Dark;
        public override Color ToolStripGradientBegin => MediumDark;
        public override Color ToolStripGradientMiddle => MediumDark;
        public override Color ToolStripGradientEnd => MediumDark;
        public override Color StatusStripGradientBegin => MediumDark;
        public override Color StatusStripGradientEnd => MediumDark;
    }
}
