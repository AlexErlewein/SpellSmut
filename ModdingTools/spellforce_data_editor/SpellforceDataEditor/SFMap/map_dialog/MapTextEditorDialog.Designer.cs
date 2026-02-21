namespace SpellforceDataEditor.SFMap.map_dialog
{
    partial class MapTextEditorDialog
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.ListTexts = new System.Windows.Forms.ListBox();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.TextBoxTextID = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.TextBoxTextContent = new System.Windows.Forms.TextBox();
            this.ButtonAddNew = new System.Windows.Forms.Button();
            this.ButtonOK = new System.Windows.Forms.Button();
            this.ButtonCancel = new System.Windows.Forms.Button();
            this.ComboBoxLanguage = new System.Windows.Forms.ComboBox();
            this.label4 = new System.Windows.Forms.Label();
            this.LabelLanguageStatus = new System.Windows.Forms.Label();
            this.SuspendLayout();
            // 
            // ListTexts
            // 
            this.ListTexts.FormattingEnabled = true;
            this.ListTexts.ItemHeight = 15;
            this.ListTexts.Location = new System.Drawing.Point(12, 25);
            this.ListTexts.Name = "ListTexts";
            this.ListTexts.Size = new System.Drawing.Size(300, 349);
            this.ListTexts.TabIndex = 0;
            this.ListTexts.SelectedIndexChanged += new System.EventHandler(this.ListTexts_SelectedIndexChanged);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(12, 7);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(60, 15);
            this.label1.TabIndex = 1;
            this.label1.Text = "Text IDs:";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(318, 25);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(42, 15);
            this.label2.TabIndex = 2;
            this.label2.Text = "Text ID:";
            // 
            // TextBoxTextID
            // 
            this.TextBoxTextID.Enabled = false;
            this.TextBoxTextID.Location = new System.Drawing.Point(318, 43);
            this.TextBoxTextID.Name = "TextBoxTextID";
            this.TextBoxTextID.Size = new System.Drawing.Size(200, 23);
            this.TextBoxTextID.TabIndex = 3;
            //
            // label3
            //
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(318, 120);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(31, 15);
            this.label3.TabIndex = 4;
            this.label3.Text = "Text:";
            //
            // label4
            //
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(318, 69);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(60, 15);
            this.label4.TabIndex = 9;
            this.label4.Text = "Language:";
            //
            // ComboBoxLanguage
            //
            this.ComboBoxLanguage.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.ComboBoxLanguage.FormattingEnabled = true;
            this.ComboBoxLanguage.Location = new System.Drawing.Point(318, 87);
            this.ComboBoxLanguage.Name = "ComboBoxLanguage";
            this.ComboBoxLanguage.Size = new System.Drawing.Size(200, 23);
            this.ComboBoxLanguage.TabIndex = 10;
            this.ComboBoxLanguage.SelectedIndexChanged += new System.EventHandler(this.ComboBoxLanguage_SelectedIndexChanged);
            //
            // LabelLanguageStatus
            //
            this.LabelLanguageStatus.AutoSize = true;
            this.LabelLanguageStatus.ForeColor = System.Drawing.Color.Gray;
            this.LabelLanguageStatus.Location = new System.Drawing.Point(380, 69);
            this.LabelLanguageStatus.Name = "LabelLanguageStatus";
            this.LabelLanguageStatus.Size = new System.Drawing.Size(0, 15);
            this.LabelLanguageStatus.TabIndex = 11;
            //
            // TextBoxTextContent
            //
            this.TextBoxTextContent.Location = new System.Drawing.Point(318, 138);
            this.TextBoxTextContent.Multiline = true;
            this.TextBoxTextContent.Name = "TextBoxTextContent";
            this.TextBoxTextContent.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.TextBoxTextContent.Size = new System.Drawing.Size(200, 149);
            this.TextBoxTextContent.TabIndex = 5;
            this.TextBoxTextContent.TextChanged += new System.EventHandler(this.TextBoxTextContent_TextChanged);
            // 
            // ButtonAddNew
            // 
            this.ButtonAddNew.Location = new System.Drawing.Point(12, 380);
            this.ButtonAddNew.Name = "ButtonAddNew";
            this.ButtonAddNew.Size = new System.Drawing.Size(100, 30);
            this.ButtonAddNew.TabIndex = 6;
            this.ButtonAddNew.Text = "Add New Text";
            this.ButtonAddNew.UseVisualStyleBackColor = true;
            this.ButtonAddNew.Click += new System.EventHandler(this.ButtonAddNew_Click);
            // 
            // ButtonOK
            // 
            this.ButtonOK.Location = new System.Drawing.Point(363, 380);
            this.ButtonOK.Name = "ButtonOK";
            this.ButtonOK.Size = new System.Drawing.Size(75, 30);
            this.ButtonOK.TabIndex = 7;
            this.ButtonOK.Text = "OK";
            this.ButtonOK.UseVisualStyleBackColor = true;
            this.ButtonOK.Click += new System.EventHandler(this.ButtonOK_Click);
            // 
            // ButtonCancel
            // 
            this.ButtonCancel.Location = new System.Drawing.Point(444, 380);
            this.ButtonCancel.Name = "ButtonCancel";
            this.ButtonCancel.Size = new System.Drawing.Size(75, 30);
            this.ButtonCancel.TabIndex = 8;
            this.ButtonCancel.Text = "Cancel";
            this.ButtonCancel.UseVisualStyleBackColor = true;
            this.ButtonCancel.Click += new System.EventHandler(this.ButtonCancel_Click);
            //
            // MapTextEditorDialog
            //
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(531, 422);
            this.Controls.Add(this.LabelLanguageStatus);
            this.Controls.Add(this.ComboBoxLanguage);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.ButtonCancel);
            this.Controls.Add(this.ButtonOK);
            this.Controls.Add(this.ButtonAddNew);
            this.Controls.Add(this.TextBoxTextContent);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.TextBoxTextID);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.ListTexts);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "MapTextEditorDialog";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            this.Text = "Text ID Editor";
            this.Load += new System.EventHandler(this.MapTextEditorDialog_Load);
            this.ResumeLayout(false);
            this.PerformLayout();
        }

        #endregion
        private System.Windows.Forms.ListBox ListTexts;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox TextBoxTextID;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.TextBox TextBoxTextContent;
        private System.Windows.Forms.Button ButtonAddNew;
        private System.Windows.Forms.Button ButtonOK;
        private System.Windows.Forms.Button ButtonCancel;
        private System.Windows.Forms.ComboBox ComboBoxLanguage;
        private System.Windows.Forms.Label LabelLanguageStatus;
    }
}

