using System;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace SpellforceDataEditor
{
    /// <summary>
    /// Helper class for handling DPI scaling in Windows Forms applications.
    /// Provides methods to dynamically adjust form layouts based on Windows display scaling settings.
    /// </summary>
    public static class DpiHelper
    {
        #region Win32 API for DPI

        [DllImport("user32.dll")]
        private static extern int GetDpiForWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern int GetDpiForSystem();

        [DllImport("shcore.dll")]
        private static extern int GetScaleFactorForDevice(IntPtr device);

        #endregion

        private const int DEFAULT_DPI = 96;

        /// <summary>
        /// Gets the current DPI scaling factor for the application.
        /// Returns 1.0 for 96 DPI (100%), 1.25 for 120 DPI (125%), 1.5 for 144 DPI (150%), etc.
        /// </summary>
        public static float GetScalingFactor()
        {
            try
            {
                // For .NET 8 with PerMonitorV2, we can use the form's DeviceDpi property
                // This will return the actual DPI of the monitor where the form is displayed
                return GetDpiForSystem() / (float)DEFAULT_DPI;
            }
            catch
            {
                return 1.0f;
            }
        }

        /// <summary>
        /// Gets the DPI scaling factor for a specific form.
        /// </summary>
        /// <param name="form">The form to check DPI for</param>
        /// <returns>Scaling factor (e.g., 1.25 for 125% scaling)</returns>
        public static float GetScalingFactor(Form form)
        {
            if (form == null) return 1.0f;
            return form.DeviceDpi / (float)DEFAULT_DPI;
        }

        /// <summary>
        /// Gets the DPI scaling factor for a specific control.
        /// </summary>
        /// <param name="control">The control to check DPI for</param>
        /// <returns>Scaling factor (e.g., 1.25 for 125% scaling)</returns>
        public static float GetScalingFactor(Control control)
        {
            if (control == null) return 1.0f;
            return control.DeviceDpi / (float)DEFAULT_DPI;
        }

        /// <summary>
        /// Scales a size value by the current DPI factor.
        /// </summary>
        /// <param name="value">The original size value</param>
        /// <param name="factor">The DPI scaling factor (optional, will use current if null)</param>
        /// <returns>Scaled size value</returns>
        public static int ScaleSize(int value, float? factor = null)
        {
            float f = factor ?? GetScalingFactor();
            return (int)Math.Round(value * f);
        }

        /// <summary>
        /// Scales a size value by the current DPI factor.
        /// </summary>
        /// <param name="value">The original size value</param>
        /// <param name="factor">The DPI scaling factor (optional, will use current if null)</param>
        /// <returns>Scaled size value</returns>
        public static float ScaleSize(float value, float? factor = null)
        {
            float f = factor ?? GetScalingFactor();
            return value * f;
        }

        /// <summary>
        /// Unscales a size value by the current DPI factor.
        /// Useful when you need to convert from scaled pixels back to logical pixels.
        /// </summary>
        /// <param name="value">The scaled size value</param>
        /// <param name="factor">The DPI scaling factor (optional, will use current if null)</param>
        /// <returns>Unscaled size value</returns>
        public static int UnscaleSize(int value, float? factor = null)
        {
            float f = factor ?? GetScalingFactor();
            return (int)Math.Round(value / f);
        }

        /// <summary>
        /// Applies DPI scaling to a form by adjusting its client size.
        /// Call this in the form's Load event after InitializeComponent().
        /// </summary>
        /// <param name="form">The form to scale</param>
        /// <param name="originalSize">The designed size at 96 DPI</param>
        public static void ApplyDpiScaling(Form form, Size originalSize)
        {
            if (form == null) return;

            float scaleFactor = GetScalingFactor(form);

            // Only scale if not already at default DPI
            if (Math.Abs(scaleFactor - 1.0f) > 0.01f)
            {
                // Scale the form size
                form.ClientSize = new Size(
                    ScaleSize(originalSize.Width, scaleFactor),
                    ScaleSize(originalSize.Height, scaleFactor)
                );

                // Optionally, scale font sizes
                ScaleFont(form, scaleFactor);
            }
        }

        /// <summary>
        /// Recursively scales font sizes for a control and all its children.
        /// </summary>
        /// <param name="control">The root control</param>
        /// <param name="scaleFactor">The DPI scaling factor</param>
        public static void ScaleFont(Control control, float scaleFactor)
        {
            if (control == null || control.Font == null) return;

            // Scale the font size
            float newSize = control.Font.Size * scaleFactor;
            if (newSize > 0 && newSize < 72) // Reasonable font size limits
            {
                try
                {
                    control.Font = new Font(
                        control.Font.FontFamily,
                        newSize,
                        control.Font.Style
                    );
                }
                catch { }
            }

            // Recursively scale children
            foreach (Control child in control.Controls)
            {
                ScaleFont(child, scaleFactor);
            }
        }

        /// <summary>
        /// Gets a human-readable description of the current DPI setting.
        /// </summary>
        /// <returns>String like "100% (96 DPI)" or "125% (120 DPI)"</returns>
        public static string GetDpiDescription()
        {
            return GetDpiDescription(GetDpiForSystem());
        }

        /// <summary>
        /// Gets a human-readable description for a specific DPI value.
        /// </summary>
        /// <param name="dpi">The DPI value</param>
        /// <returns>String like "100% (96 DPI)"</returns>
        public static string GetDpiDescription(int dpi)
        {
            int percentage = (int)Math.Round((dpi / (float)DEFAULT_DPI) * 100);
            return $"{percentage}% ({dpi} DPI)";
        }

        /// <summary>
        /// Checks if the current display is using non-standard DPI scaling.
        /// </summary>
        /// <returns>True if DPI is not 96 (100%)</returns>
        public static bool IsHighDpi()
        {
            return GetDpiForSystem() != DEFAULT_DPI;
        }

        /// <summary>
        /// Logs the current DPI settings for debugging.
        /// </summary>
        public static void LogDpiInfo()
        {
            int systemDpi = GetDpiForSystem();
            float scaleFactor = systemDpi / (float)DEFAULT_DPI;
            int percentage = (int)Math.Round(scaleFactor * 100);

            SFEngine.LogUtils.Log.Info(SFEngine.LogUtils.LogSource.Main,
                $"DPI Info: System DPI = {systemDpi}, Scale Factor = {scaleFactor:F2}, Display = {percentage}%");
        }
    }
}
