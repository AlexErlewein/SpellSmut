using System.Windows.Forms;

namespace SpellforceDataEditor.SFMap.map_controls
{
    public partial class MapInspector : UserControl
    {
        public SFEngine.SFMap.SFMap map = null;
        public SFMap.SFMapSelectionHelper selection_helper = null;

        protected void SetInspectorPanelEditable(Control panel, bool editable)
        {
            if (panel == null)
            {
                return;
            }

            // Keep labels readable in dark mode by not disabling the whole parent panel.
            panel.Enabled = true;
            foreach (Control child in panel.Controls)
            {
                SetControlEditableState(child, editable);
            }
        }

        private static void SetControlEditableState(Control control, bool editable)
        {
            if (control is LinkLabel || control is Label)
            {
                control.Enabled = true;
                return;
            }

            if (control is TextBox textBox)
            {
                textBox.Enabled = true;
                textBox.ReadOnly = !editable;
                textBox.TabStop = editable;
                return;
            }

            if (control.HasChildren)
            {
                control.Enabled = true;
                foreach (Control child in control.Controls)
                {
                    SetControlEditableState(child, editable);
                }

                return;
            }

            control.Enabled = editable;
        }

        public MapInspector()
        {
            InitializeComponent();
        }

        public virtual void OnSelect(object o)
        {

        }
    }
}
