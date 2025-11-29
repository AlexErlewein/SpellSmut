using SFEngine.SFCFF;
using SFEngine.SFCFF.CTG;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;

namespace SpellforceDataEditor.SFMap.map_dialog
{
    public partial class MapTextEditorDialog : Form
    {
        public ushort SelectedTextID { get; set; } = 0;
        private bool _updatingLanguage = false;

        // Language ID to name mapping
        private readonly Dictionary<byte, string> _languageNames = new Dictionary<byte, string>
        {
            { 0, "English" },
            { 1, "German" },
            { 2, "French" },
            { 3, "Spanish" },
            { 4, "Italian" },
            { 5, "Russian" },
            { 6, "Polish" },
            { 7, "Czech" }
        };

        public MapTextEditorDialog()
        {
            InitializeComponent();
        }

        private void MapTextEditorDialog_Load(object sender, EventArgs e)
        {
            // Populate language dropdown
            ComboBoxLanguage.Items.Clear();
            foreach (var lang in _languageNames.OrderBy(x => x.Key))
            {
                ComboBoxLanguage.Items.Add($"{lang.Value} (ID: {lang.Key})");
            }

            // Set default to editor's current language
            int defaultLangIndex = ComboBoxLanguage.Items.Cast<string>()
                .ToList()
                .FindIndex(s => s.StartsWith($"{_languageNames[(byte)SFEngine.Settings.LanguageID]} (ID: {SFEngine.Settings.LanguageID})"));
            if (defaultLangIndex >= 0)
            {
                ComboBoxLanguage.SelectedIndex = defaultLangIndex;
            }
            else if (ComboBoxLanguage.Items.Count > 0)
            {
                ComboBoxLanguage.SelectedIndex = 0;
            }

            ReloadTextList();
            if (SelectedTextID != 0)
            {
                // Find and select the text ID in the list
                for (int i = 0; i < ListTexts.Items.Count; i++)
                {
                    string item = ListTexts.Items[i].ToString();
                    if (item.StartsWith(SelectedTextID.ToString() + " "))
                    {
                        ListTexts.SelectedIndex = i;
                        break;
                    }
                }
            }
        }

        private byte GetSelectedLanguageID()
        {
            if (ComboBoxLanguage.SelectedIndex == -1)
                return 0;

            string selected = ComboBoxLanguage.SelectedItem.ToString();
            // Extract language ID from string like "English (ID: 0)"
            int startIdx = selected.IndexOf("ID: ") + 4;
            int endIdx = selected.IndexOf(")", startIdx);
            if (startIdx > 3 && endIdx > startIdx)
            {
                if (byte.TryParse(selected.Substring(startIdx, endIdx - startIdx), out byte langId))
                {
                    return langId;
                }
            }
            return 0;
        }

        private void ReloadTextList()
        {
            ListTexts.Items.Clear();
            Category2016 c2016 = SFCategoryManager.gamedata.c2016;

            for (int i = 0; i < c2016.GetNumOfItems(); i++)
            {
                ushort text_id = c2016[i, 0].TextID;
                string text = SFCategoryManager.GetTextByLanguage(text_id, SFEngine.Settings.LanguageID);
                string display_text = text.Trim();
                if (display_text.Length > 50)
                {
                    display_text = display_text.Substring(0, 47) + "...";
                }
                ListTexts.Items.Add($"{text_id} - {display_text}");
            }
        }

        private void UpdateLanguageStatus()
        {
            if (ListTexts.SelectedIndex == -1)
            {
                LabelLanguageStatus.Text = "";
                return;
            }

            Category2016 c2016 = SFCategoryManager.gamedata.c2016;
            int index = ListTexts.SelectedIndex;
            byte selectedLang = GetSelectedLanguageID();

            // Check which languages exist for this text ID
            List<byte> availableLanguages = new List<byte>();
            for (int i = 0; i < c2016.GetItemSubItemNum(index); i++)
            {
                byte langId = c2016[index, i].LanguageID;
                if (!availableLanguages.Contains(langId))
                {
                    availableLanguages.Add(langId);
                }
            }

            // Update status label
            if (availableLanguages.Contains(selectedLang))
            {
                LabelLanguageStatus.Text = $"({availableLanguages.Count} language(s))";
                LabelLanguageStatus.ForeColor = Color.Green;
            }
            else
            {
                LabelLanguageStatus.Text = $"Missing! ({availableLanguages.Count} language(s))";
                LabelLanguageStatus.ForeColor = Color.Red;
            }
        }

        private void ListTexts_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (ListTexts.SelectedIndex == -1)
            {
                TextBoxTextContent.Text = "";
                TextBoxTextID.Text = "";
                LabelLanguageStatus.Text = "";
                return;
            }

            Category2016 c2016 = SFCategoryManager.gamedata.c2016;
            int index = ListTexts.SelectedIndex;
            ushort text_id = c2016[index, 0].TextID;

            TextBoxTextID.Text = text_id.ToString();

            // Get text in currently selected language
            LoadTextForCurrentLanguage();
            UpdateLanguageStatus();
        }

        private void ComboBoxLanguage_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (_updatingLanguage || ListTexts.SelectedIndex == -1)
                return;

            LoadTextForCurrentLanguage();
            UpdateLanguageStatus();
        }

        private void LoadTextForCurrentLanguage()
        {
            if (ListTexts.SelectedIndex == -1)
                return;

            _updatingLanguage = true;

            Category2016 c2016 = SFCategoryManager.gamedata.c2016;
            int index = ListTexts.SelectedIndex;
            byte selectedLang = GetSelectedLanguageID();

            // Find the language entry for selected language
            int lang_index = -1;
            for (int i = 0; i < c2016.GetItemSubItemNum(index); i++)
            {
                if (c2016[index, i].LanguageID == selectedLang)
                {
                    lang_index = i;
                    break;
                }
            }

            if (lang_index != -1)
            {
                // Language entry exists - load it
                string text = c2016[index, lang_index].GetContentString().TrimEnd('\0');
                TextBoxTextContent.Text = text;
                TextBoxTextContent.Enabled = true;
            }
            else
            {
                // Language entry missing - show placeholder
                TextBoxTextContent.Text = "";
                TextBoxTextContent.Enabled = true;
            }

            _updatingLanguage = false;
        }

        private void ButtonAddNew_Click(object sender, EventArgs e)
        {
            // Find next free text ID
            Category2016 c2016 = SFCategoryManager.gamedata.c2016;
            ushort new_id = 1;

            // Find the highest existing ID
            ushort max_id = 0;
            for (int i = 0; i < c2016.GetNumOfItems(); i++)
            {
                ushort id = c2016[i, 0].TextID;
                if (id > max_id)
                {
                    max_id = id;
                }
            }

            // Start from max_id + 1 and find first free
            new_id = (ushort)(max_id + 1);
            while (c2016.GetItemIndex(new_id, out _))
            {
                new_id++;
                if (new_id == 0) // Overflow protection
                {
                    MessageBox.Show("No free text ID available!", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }
            }

            // Add new text ID using AddID (creates a new main item)
            int new_index = c2016.GetNumOfItems();
            c2016.AddID(new_index, new_id);

            // Add language entry for all common languages with placeholder text
            foreach (var lang in new byte[] { 0, 1 }) // English and German by default
            {
                Category2016Item lang_item = new Category2016Item();
                lang_item.TextID = new_id;
                lang_item.LanguageID = lang;
                lang_item.Mode = 0;

                int subitem_index = c2016.GetItemSubItemNum(new_index);
                c2016.AddSubItem(new_index, subitem_index, lang_item);

                c2016.SetField(new_index, subitem_index, "Handle", SFEngine.StringUtils.FromString("", 0, 50));
                c2016.SetField(new_index, subitem_index, "Content", SFEngine.StringUtils.FromString("New Text", lang, 512));
            }

            // Reload and select the new item
            ReloadTextList();
            for (int i = 0; i < ListTexts.Items.Count; i++)
            {
                if (ListTexts.Items[i].ToString().StartsWith(new_id.ToString() + " "))
                {
                    ListTexts.SelectedIndex = i;
                    break;
                }
            }

            TextBoxTextContent.Focus();
            TextBoxTextContent.SelectAll();
        }

        private void ButtonOK_Click(object sender, EventArgs e)
        {
            if (ListTexts.SelectedIndex != -1)
            {
                Category2016 c2016 = SFCategoryManager.gamedata.c2016;
                int index = ListTexts.SelectedIndex;
                SelectedTextID = c2016[index, 0].TextID;
            }
            DialogResult = DialogResult.OK;
            Close();
        }

        private void ButtonCancel_Click(object sender, EventArgs e)
        {
            DialogResult = DialogResult.Cancel;
            Close();
        }

        private void TextBoxTextContent_TextChanged(object sender, EventArgs e)
        {
            if (_updatingLanguage || ListTexts.SelectedIndex == -1)
            {
                return;
            }

            Category2016 c2016 = SFCategoryManager.gamedata.c2016;
            int index = ListTexts.SelectedIndex;
            byte selectedLang = GetSelectedLanguageID();

            // Find the language entry for selected language
            int lang_index = -1;
            for (int i = 0; i < c2016.GetItemSubItemNum(index); i++)
            {
                if (c2016[index, i].LanguageID == selectedLang)
                {
                    lang_index = i;
                    break;
                }
            }

            if (lang_index == -1)
            {
                // Language not found - add it
                lang_index = c2016.GetItemSubItemNum(index);
                Category2016Item new_lang_item = new Category2016Item();
                c2016.GetID(index, out int text_id);
                new_lang_item.TextID = (ushort)text_id;
                new_lang_item.LanguageID = selectedLang;
                new_lang_item.Mode = 0;

                // Add the language subitem first
                c2016.AddSubItem(index, lang_index, new_lang_item);

                // Then set the fields using SetField
                c2016.SetField(index, lang_index, "Handle", SFEngine.StringUtils.FromString("", 0, 50));
                c2016.SetField(index, lang_index, "Content", SFEngine.StringUtils.FromString(TextBoxTextContent.Text, selectedLang, 512));

                UpdateLanguageStatus();
            }
            else
            {
                // Update existing language entry
                c2016.SetField(index, lang_index, "Content", SFEngine.StringUtils.FromString(TextBoxTextContent.Text, selectedLang, 512));
            }

            // Update ONLY the single list item if editing the display language (much faster than full reload)
            if (selectedLang == (byte)SFEngine.Settings.LanguageID)
            {
                ushort text_id = c2016[index, 0].TextID;
                string display_text = TextBoxTextContent.Text.Trim();
                if (display_text.Length > 50)
                {
                    display_text = display_text.Substring(0, 47) + "...";
                }

                // Block events while updating list (prevents cursor reset)
                int oldSelectionStart = TextBoxTextContent.SelectionStart;
                int oldSelectionLength = TextBoxTextContent.SelectionLength;

                _updatingLanguage = true;
                ListTexts.Items[index] = $"{text_id} - {display_text}";
                _updatingLanguage = false;

                // Restore cursor position
                TextBoxTextContent.SelectionStart = oldSelectionStart;
                TextBoxTextContent.SelectionLength = oldSelectionLength;
            }
        }
    }
}
