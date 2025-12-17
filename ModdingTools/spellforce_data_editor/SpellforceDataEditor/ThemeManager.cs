using System.Drawing;
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
                if (control is Form || control is Panel || control is GroupBox ||
                    control is TabControl || control is TabPage || control is SplitContainer)
                {
                    control.BackColor = Color.FromArgb(32, 32, 32);
                    control.ForeColor = Color.Gainsboro;
                }
                else if (control is Button)
                {
                    control.BackColor = Color.FromArgb(45, 45, 45);
                    control.ForeColor = Color.Gainsboro;
                }
                else if (control is TextBox || control is ComboBox || control is ListBox)
                {
                    control.BackColor = Color.FromArgb(24, 24, 24);
                    control.ForeColor = Color.Gainsboro;
                }
                else if (control is Label || control is CheckBox || control is RadioButton)
                {
                    control.ForeColor = Color.Gainsboro;
                }
                else if (control is MenuStrip || control is StatusStrip || control is ToolStrip)
                {
                    control.BackColor = Color.FromArgb(45, 45, 45);
                    control.ForeColor = Color.Gainsboro;
                }
                else if (control is TreeView || control is ListView)
                {
                    control.BackColor = Color.FromArgb(24, 24, 24);
                    control.ForeColor = Color.Gainsboro;
                }

                if (control is TabPage darkTabPage)
                {
                    darkTabPage.UseVisualStyleBackColor = false;
                }
            }
            else
            {
                if (control is Form || control is Panel || control is GroupBox ||
                    control is TabControl || control is TabPage || control is SplitContainer)
                {
                    control.BackColor = SystemColors.Control;
                    control.ForeColor = SystemColors.ControlText;
                }
                else if (control is Button)
                {
                    control.BackColor = SystemColors.Control;
                    control.ForeColor = SystemColors.ControlText;
                }
                else if (control is TextBox || control is ComboBox || control is ListBox)
                {
                    control.BackColor = SystemColors.Window;
                    control.ForeColor = SystemColors.WindowText;
                }
                else if (control is Label || control is CheckBox || control is RadioButton)
                {
                    control.ForeColor = SystemColors.ControlText;
                }
                else if (control is MenuStrip || control is StatusStrip || control is ToolStrip)
                {
                    control.BackColor = SystemColors.Control;
                    control.ForeColor = SystemColors.ControlText;
                }
                else if (control is TreeView || control is ListView)
                {
                    control.BackColor = SystemColors.Window;
                    control.ForeColor = SystemColors.WindowText;
                }

                if (control is TabPage lightTabPage)
                {
                    lightTabPage.UseVisualStyleBackColor = true;
                }
            }
        }
    }
}
