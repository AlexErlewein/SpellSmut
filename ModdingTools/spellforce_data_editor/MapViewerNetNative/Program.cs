using System;
using System.Windows.Forms;

namespace MapViewerNetNative
{
    class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);

            try
            {
                MapViewerWindow mew = new MapViewerWindow();
                mew.Run();
            }
            catch (Exception ex)
            {
                string errorMessage = "An error occurred while starting MapViewer:\n\n" + ex.Message;
                if (ex.InnerException != null)
                {
                    errorMessage += "\n\nInner Exception: " + ex.InnerException.Message;
                }
                errorMessage += "\n\nStack Trace:\n" + ex.StackTrace;
                MessageBox.Show(errorMessage, "MapViewer Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                System.Environment.Exit(1);
            }
        }

    }
}
