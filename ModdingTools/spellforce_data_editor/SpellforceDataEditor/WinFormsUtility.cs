using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;

namespace SpellforceDataEditor
{
    //helper class providing with useful functions
    public static class WinFormsUtility
    {
        // brushes for unified color scheme
        public static SolidBrush BrushBackgroundDefault = new SolidBrush(Color.White);
        public static SolidBrush BrushBackgroundElemModified = new SolidBrush(Color.FromArgb(200, 200, 100));
        public static SolidBrush BrushBackgroundElemAdded = new SolidBrush(Color.FromArgb(100, 200, 100));
        public static SolidBrush BrushBackgroundElemRemoved = new SolidBrush(Color.FromArgb(200, 100, 100));
        public static SolidBrush BrushBackgroundElemSelected = new SolidBrush(Color.FromArgb(40, 40, 200));
        public static SolidBrush BrushTextDefault = new SolidBrush(Color.Black);
        public static SolidBrush BrushTextElemSelected = new SolidBrush(Color.White);


        public static void UseLightTheme()
        {
            BrushBackgroundDefault = new SolidBrush(Color.White);
            BrushBackgroundElemModified = new SolidBrush(Color.FromArgb(200, 200, 100));
            BrushBackgroundElemAdded = new SolidBrush(Color.FromArgb(100, 200, 100));
            BrushBackgroundElemRemoved = new SolidBrush(Color.FromArgb(200, 100, 100));
            BrushBackgroundElemSelected = new SolidBrush(Color.FromArgb(40, 40, 200));
            BrushTextDefault = new SolidBrush(Color.Black);
            BrushTextElemSelected = new SolidBrush(Color.White);
        }

        public static void UseDarkTheme()
        {
            BrushBackgroundDefault = new SolidBrush(Color.FromArgb(32, 32, 32));
            BrushBackgroundElemModified = new SolidBrush(Color.FromArgb(120, 120, 60));
            BrushBackgroundElemAdded = new SolidBrush(Color.FromArgb(60, 120, 60));
            BrushBackgroundElemRemoved = new SolidBrush(Color.FromArgb(120, 60, 60));
            BrushBackgroundElemSelected = new SolidBrush(Color.FromArgb(70, 70, 160));
            BrushTextDefault = new SolidBrush(Color.Gainsboro);
            BrushTextElemSelected = new SolidBrush(Color.White);
        }


        static public string GetString(string caption, string label, string default_str = "")
        {
            special_forms.utility_forms.GetStringForm form = new special_forms.utility_forms.GetStringForm();
            form.SetDescription(caption, label, default_str);
            form.ShowDialog();
            if (form.Result == DialogResult.Cancel)
            {
                return default_str;
            }

            return form.ResultString;
        }

        public static void TreeShallowCopy(Dictionary<string, TreeNode> src, TreeNodeCollection dst)
        {
            foreach (string tn in src.Keys)
            {
                dst.Add(src[tn]);
            }
        }
    }
}
